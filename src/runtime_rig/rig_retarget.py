import logging
import time
import numpy as np

from pyglm import glm
from dataclasses import dataclass

from libs.tag.tag_array import Tag_Array
from libs.tag.data_types import Skeleton_Node_Def, Runtime_Rig_Component
from libs.matrix_operations import (
	glm_get_scale, glm_get_quat, glm_get_translation,
	glm_decompose_mat4, glm_compose_mat4, glm_interpolate_mat4,
	glm_axis_x, glm_axis_y, glm_axis_z, X, Z
)
from src.tag_readers.animation.read_animation import Animation_Data
from src.tag_readers.skeleton.read_skeleton import Skeleton
from src.tag_readers.runtime_rig.read_runtime_rig import Runtime_Rig_Data
from src.decode_animation.decode_animation import Bone_Tracks
from src.fnv_hashes.int_to_hex import u32_to_be_hex
from src.tag_readers.runtime_rig.unified_structures import (
	Unified_Constraint, Constraint_Type,
	IK_Function_Type, Space_Type, Space_Def
)
from .helpers import ik_3_solve_no_pole

logger = logging.getLogger(__name__)
IDENTITY_MAT4 = glm.mat4()

@dataclass(slots=True)
class IK_Affected_Control:
	affector_control_index: int
	affected_control_index: int


@dataclass(slots=True)
class IK_3_Chain:
	start_bone_index: int
	target_bone_index: int
	end_bone_index: int


@dataclass(slots=True)
class RFK_Chain:
	start_bone_index: int
	end_bone_index: int
	bones_indices: tuple[int, ...]


@dataclass(slots=True)
class Runtime_Rig_Cache:
	constraints: list[Unified_Constraint]
	ik_3_chains: dict[int, IK_3_Chain]
	rfk_chains: dict[int, RFK_Chain]
	ik_affected_controls: list[IK_Affected_Control]


@dataclass(slots=True)
class Animation_Cache:
	ignored_controls: set[int]
	empty_controls: set[int]


class Invalid_Rig_Error(Exception):
	pass


def log_rig_cache(rig_cache: Runtime_Rig_Cache) -> None:
	logger.info("Rig cache:")
	for ik_3_chain_affector in rig_cache.ik_3_chains:
		chain = rig_cache.ik_3_chains[ik_3_chain_affector]
		logger.info(f"\tbone {ik_3_chain_affector} is end for chain: [{chain.start_bone_index}, {chain.target_bone_index}, {chain.end_bone_index}]")

	for rfk_chain_affector in rig_cache.rfk_chains:
		chain = rig_cache.rfk_chains[rfk_chain_affector]
		logger.info(f"\tbone {rfk_chain_affector} is end for chain: {chain.bones_indices}")


def sign(val: float | int):
	if val >= 0:
		return 1
	return -1


def calc_control_limit(rig: Runtime_Rig_Data, animation_rig_components: Tag_Array[Runtime_Rig_Component]):
	logger.info("Runtime rig subsets limit:")
	limit = 0

	rig_components_len = rig.rig_components.length
	animation_components_len = animation_rig_components.length

	for i in range(min(rig_components_len, animation_components_len)):
		rig_component_hash = rig.rig_components[i].hash
		rig_component_count = rig.rig_components[i].control_count
		animation_component_hash = animation_rig_components[i].hash
		animation_component_count = animation_rig_components[i].control_count

		if rig_component_hash == animation_component_hash:
			if rig_component_count == animation_component_count:
				limit += rig_component_count
				logger.info(f"\tuse subset [{i}], {u32_to_be_hex(rig_component_hash)}, control count: {rig_component_count}")
			else:
				limit += min(rig_component_count, animation_component_count)
				logger.info(f"\tuse subset [{i}] part, {u32_to_be_hex(rig_component_hash)}, control count: {min(rig_component_count, animation_component_count)}")
				break
		else:
			break

	return limit


def build_bone_chain(
	skeleton_node_defs: Tag_Array[Skeleton_Node_Def],
	start_bone_index: int,
	end_bone_index: int
) -> tuple[int, ...]:
	chain = [end_bone_index]
	curr = end_bone_index

	while curr != start_bone_index:
		curr = skeleton_node_defs[curr].parent_node_index

		if curr == -1:
			raise Invalid_Rig_Error(
				f"IK chain start bone {end_bone_index} is not an ancestor of {start_bone_index}"
			)

		chain.append(curr)

	return tuple(reversed(chain))


def build_runtime_rig_cache(skeleton: Skeleton, rig: Runtime_Rig_Data) -> Runtime_Rig_Cache:
	constraints = rig.controls_relations
	bone_to_control = rig.bone_to_control
	bones_relations = skeleton.node_defs

	ik_affected_controls = []
	ik_3_chains = {}
	rfk_chains = {}

	for control_index in range(len(constraints)):
		constraint = constraints[control_index]
		bone_index = constraint.bone_index  # current bone is an end of a chain

		if constraint.ik_function_type == IK_Function_Type.RFK:
			chain = build_bone_chain(bones_relations, constraint.ik_chain_start_bone_index, bone_index)

			rfk_chains[bone_index] = RFK_Chain(
				start_bone_index=chain[0],
				end_bone_index=chain[-1],
				bones_indices=chain
			)

			for i in range(1, len(chain) - 1):
				ik_affected_controls.append(
					IK_Affected_Control(control_index, bone_to_control[chain[i]])
				)

		if constraint.ik_function_type == IK_Function_Type.IK_3:
			chain = build_bone_chain(bones_relations, constraint.ik_chain_start_bone_index, bone_index)

			if len(chain) != 3:
				raise Invalid_Rig_Error(
					f"IK_3 chain must have length 3, got {len(chain)}, start {chain[0]}, end {chain[-1]}"
				)

			ik_3_chains[bone_index] = IK_3_Chain(chain[0], chain[1], chain[2])

			target_bone_index = chain[1]

			ik_affected_controls.append(
				IK_Affected_Control(control_index, bone_to_control[target_bone_index])
			)

	return Runtime_Rig_Cache(
		constraints=constraints,
		ik_3_chains=ik_3_chains,
		rfk_chains=rfk_chains,
		ik_affected_controls=ik_affected_controls
	)


def build_animation_cache(
	tracks: list[Bone_Tracks | None],
	ik_affected_controls: list[IK_Affected_Control]
) -> Animation_Cache:
	bone_data: list[Bone_Tracks | None] = tracks
	# if animation has no data for control
	empty_controls = set()

	for control_index, track_group in enumerate(tracks):
		if track_group is None:
			empty_controls.add(control_index)

	logger.info(f"Controls without tracks: {list(empty_controls)}")

	ignored_controls = set()

	for i in range(len(ik_affected_controls)):
		affector_control_index = ik_affected_controls[i].affector_control_index
		affected_control_index = ik_affected_controls[i].affected_control_index

		if affected_control_index == -1:
			continue
		elif affected_control_index > affector_control_index: # if affected is after affector
			track_group: Bone_Tracks | None = bone_data[affected_control_index]

			# if bone is static through the whole animation and its control is after ik affector it will override srt data
			# hence static controls should be ignored

			if track_group is None:
				# have no control data
				ignored_controls.add(affected_control_index)
			elif all(len(x) < 2 for x in [track_group.scales, track_group.rotations, track_group.translations]):
				# it is in static codec (len == 1)
				ignored_controls.add(affected_control_index)

	return Animation_Cache(ignored_controls, empty_controls)


def get_frame_value(attr: np.ndarray, frame_index: int):
	return attr[frame_index % attr.shape[0]]


def rig_retarget(
	animation_data: Animation_Data,
	controls_data: list[Bone_Tracks | None],
	skeleton: Skeleton,
	rig: Runtime_Rig_Data,
) -> list[Bone_Tracks]:
	# animation properties
	frames = animation_data.animation_header.frame_count
	# object properties
	aim_vector = glm.vec3(0, 0, 1)
	neutral_aim_vector = glm.vec3(0, 0, 1)
	# compute skeleton cache
	bones_relations = skeleton.node_defs
	# rest pose in object space
	rest_matrices_object_space = skeleton.default_obj_space_matrices
	# rest pose in parent space
	rest_matrices_parent_space = skeleton.bone_to_parent_offset
	num_bones = bones_relations.length
	# compute rig and skeleton cache
	rig_cache = build_runtime_rig_cache(skeleton, rig)
	log_rig_cache(rig_cache)
	constraints: list[Unified_Constraint] = rig_cache.constraints

	bone_to_control = rig.bone_to_control
	control_to_bone = rig.control_to_bone
	# compute animation cache
	animation_cache = build_animation_cache(controls_data, rig_cache.ik_affected_controls)
	ignored_ik_affected_controls = animation_cache.ignored_controls

	logger.info("Ignored controls:")
	for ignored in ignored_ik_affected_controls:
		logger.info(f"\tcontrol {ignored} [bone {control_to_bone[ignored]}]")

	# intermediate storage
	skeleton_bones_matrices = glm.array.zeros(num_bones, glm.mat4)
	# result animation defaults
	converted_animation = [
		Bone_Tracks(
			bone_name_hash=bones_relations[bone_index].bone_hash,
			scales=np.ones((frames, 3), dtype=np.float32),  # 1.0
			rotations=np.zeros((frames, 4), dtype=np.float32),  # [0,0,0,1]
			translations=np.zeros((frames, 3), dtype=np.float32)  # 0.0
		) for bone_index in range(num_bones)
	]
	for track in converted_animation:
		track.rotations[:, 3] = 1.0

	# bone controls matrices, limit by compatible layers
	controls_limit = calc_control_limit(rig, animation_data.runtime_rig_components)
	logger.info(f"Controls limit: {controls_limit}")

	logger.info("Retarget started")
	start_time = time.perf_counter()

	bone_updated = np.zeros(num_bones, dtype=np.bool)

	for frame in range(frames):
		bone_updated.fill(False)

		aim_quat = glm.quat(neutral_aim_vector, aim_vector) # rotation_from_unit_vectors(neutral_aim_vector, aim_vector)

		for control_index in range(0, controls_limit):

			# static bone should not override ik
			if control_index in ignored_ik_affected_controls:
				continue

			bone_index = control_to_bone[control_index]
			track_group: Bone_Tracks | None = controls_data[control_index]
			constraint = constraints[control_index]

			if track_group is None:
				skeleton_node_def = bones_relations[bone_index]
				parent_bone_index = skeleton_node_def.parent_node_index

				if parent_bone_index > -1 and bone_updated[parent_bone_index]:
					parent_matrix = skeleton_bones_matrices[parent_bone_index]
					origin_tr = glm_get_translation(parent_matrix)
					origin_rot = glm_get_quat(parent_matrix)

					parent_offset_matrix = rest_matrices_parent_space[bone_index]
					parent_offset_tr = glm_get_translation(parent_offset_matrix)
					parent_offset_rot = glm_get_quat(parent_offset_matrix)

					result_tr = origin_tr + origin_rot * parent_offset_tr  # not adding animation data as it is identity
					result_rot = origin_rot * parent_offset_rot

					skeleton_bones_matrices[bone_index] = glm_compose_mat4(result_tr, result_rot, glm.vec3(1, 1, 1))
					bone_updated[bone_index] = True
				else:
					skeleton_bones_matrices[bone_index] = rest_matrices_object_space[bone_index]
					bone_updated[bone_index] = True
			else:
				origin_rot = glm.quat()
				origin_tr = glm.vec3()

				animation_sc = glm.vec3(get_frame_value(track_group.scales, frame))

				rotation = get_frame_value(track_group.rotations, frame)
				animation_rot = glm.normalize(glm.quat(rotation[3], rotation[0], rotation[1], rotation[2]))

				translation = get_frame_value(track_group.translations, frame)
				animation_tr = glm.vec3(translation[0], translation[1], translation[2])

				if constraint.constraint_type == Constraint_Type.POINT_AND_ORIENT:
					rotation_space: Space_Def = constraint.rot_space_0
					translation_space: Space_Def = constraint.tr_space_0

					match translation_space.space_type:
						case Space_Type.RELATIVE | Space_Type.UNK_3: # 0 and 3 for now
							parent_bone_index = translation_space.bone_index_0

							if parent_bone_index == -1:
								parent_matrix = IDENTITY_MAT4
							elif bone_updated[parent_bone_index]:
								parent_matrix = skeleton_bones_matrices[parent_bone_index]
							else:
								logger.warning(f"point_and_orient // tr constraint 'relative': bone {parent_bone_index} is not updated yet!")
								continue

							origin_tr = glm_get_translation(parent_matrix)

						case Space_Type.PARENT: # 1
							parent_bone_index = translation_space.bone_index_0

							if parent_bone_index == -1:
								origin_tr = glm_get_translation(rest_matrices_object_space[bone_index])

							elif bone_updated[parent_bone_index]:
								parent_matrix = skeleton_bones_matrices[parent_bone_index]
								parent_tr = glm_get_translation(parent_matrix)
								parent_rot = glm_get_quat(parent_matrix)

								parent_offset_matrix = rest_matrices_parent_space[bone_index]
								parent_offset_tr = glm_get_translation(parent_offset_matrix)

								origin_tr = parent_tr + parent_rot * parent_offset_tr

							else:
								logger.warning(f"point_and_orient // tr constraint 'parent': bone {parent_bone_index} is not updated yet!")
								continue

						case Space_Type.OBJECT:  # 2
							origin_tr = glm_get_translation(rest_matrices_object_space[0])

						case Space_Type.BIND:  # 4
							zeroth_matrix = rest_matrices_object_space[0]
							zeroth_tr = glm_get_translation(zeroth_matrix)

							bind_matrix = rest_matrices_object_space[bone_index]
							bind_tr = glm_get_translation(bind_matrix)
							origin_tr = zeroth_tr + bind_tr

						case Space_Type.AVERAGE:
							parent_0_index = translation_space.bone_index_0
							parent_1_index = translation_space.bone_index_1

							if parent_0_index == -1:
								parent_0_matrix = IDENTITY_MAT4
							elif bone_updated[parent_0_index]:
								parent_0_matrix = skeleton_bones_matrices[parent_0_index]
							else:
								logger.warning(f"point_and_orient // tr constraint 'average': bone 0 {parent_0_index} is not updated yet!")
								continue

							if parent_1_index == -1:
								parent_1_matrix = IDENTITY_MAT4
							elif bone_updated[parent_1_index]:
								parent_1_matrix = skeleton_bones_matrices[parent_1_index]
							else:
								logger.warning(f"point_and_orient // tr constraint 'average': bone 1 {parent_1_index} is not updated yet!")
								continue

							origin_tr = 0.5 * (
								glm_get_translation(parent_0_matrix) +
								glm_get_translation(parent_1_matrix)
							)
						case _:
							logger.warning("unsupported tr source for point and orient", translation_space.space_type)
							continue

					match rotation_space.space_type:
						case Space_Type.RELATIVE | Space_Type.UNK_3:  # 0 and 3 for now
							parent_bone_index = rotation_space.bone_index_0

							if parent_bone_index == -1:
								parent_matrix = IDENTITY_MAT4
							elif bone_updated[parent_bone_index]:
								parent_matrix = skeleton_bones_matrices[parent_bone_index]
							else:
								logger.warning(f"point_and_orient // rot constraint 'relative': bone {parent_bone_index} is not updated yet!")
								continue

							origin_rot = glm_get_quat(parent_matrix)

						case Space_Type.PARENT:  # 1
							parent_bone_index = rotation_space.bone_index_0

							if parent_bone_index == -1:
								origin_rot = glm_get_quat(rest_matrices_object_space[bone_index])

							elif bone_updated[parent_bone_index]:
								parent_matrix = skeleton_bones_matrices[parent_bone_index]
								parent_rot = glm_get_quat(parent_matrix)

								parent_offset_matrix = rest_matrices_parent_space[bone_index]
								parent_offset_rot = glm_get_quat(parent_offset_matrix)

								origin_rot = parent_rot * parent_offset_rot
							else:
								logger.warning(f"point_and_orient // rot constraint 'parent': bone {parent_bone_index} is not updated yet!")
								continue

						case Space_Type.OBJECT:  # 2
							origin_rot = glm_get_quat(rest_matrices_object_space[0])

						case Space_Type.BIND:  # 4
							zeroth_matrix = rest_matrices_object_space[0]
							zeroth_rot = glm_get_quat(zeroth_matrix)

							bind_matrix = rest_matrices_object_space[bone_index]
							bind_rot = glm_get_quat(bind_matrix)
							origin_rot = zeroth_rot * bind_rot

						case Space_Type.AVERAGE: # 5
							parent_0_index = rotation_space.bone_index_0
							parent_1_index = rotation_space.bone_index_1

							if parent_0_index == -1:
								parent_0_matrix = IDENTITY_MAT4
							elif bone_updated[parent_0_index]:
								parent_0_matrix = skeleton_bones_matrices[parent_0_index]
							else:
								logger.warning(f"point_and_orient // rot constraint 'average': bone 0 {parent_0_index} is not updated yet!")
								continue

							if parent_1_index == -1:
								parent_1_matrix = IDENTITY_MAT4
							elif bone_updated[parent_1_index]:
								parent_1_matrix = skeleton_bones_matrices[parent_1_index]
							else:
								logger.warning(f"point_and_orient // rot constraint 'average': bone 1 {parent_1_index} is not updated yet!")
								continue

							parent_0_rot = glm_get_quat(parent_0_matrix)
							parent_1_rot = glm_get_quat(parent_1_matrix)

							origin_rot = glm.slerp(parent_0_rot, parent_1_rot, 0.5)

						case Space_Type.AIM:  # 6
							aim_influence = constraint.aim_influence

							origin_rot = glm.slerp(glm.quat(), aim_quat, aim_influence)
						case _:
							logger.warning("unsupported rotation source for point and orient {rotation_space}")
							continue

					result_tr = origin_tr + animation_tr
					result_rot = origin_rot * animation_rot

					bone_matrix = glm_compose_mat4(result_tr, result_rot, animation_sc)
					skeleton_bones_matrices[bone_index] = bone_matrix

					bone_updated[bone_index] = True

				elif constraint.constraint_type == Constraint_Type.PARENT:
					rotation_space: Space_Def = constraint.rot_space_0
					# looks like tr_space 0 and 1 are not used with parent constraint
					# but if rotation_space == AIM, it has only rotation, no translation,
					# so *it seems* rot_space_1 is used as a source of translation in this case
					translation_space: Space_Def = constraint.rot_space_1

					match rotation_space.space_type:
						case Space_Type.RELATIVE | Space_Type.UNK_3:  # 0 and 3 for now
							parent_bone_index = constraint.rot_space_0.bone_index_0

							if parent_bone_index == -1:
								parent_matrix = IDENTITY_MAT4
							elif bone_updated[parent_bone_index]:
								parent_matrix = skeleton_bones_matrices[parent_bone_index]
							else:
								logger.warning(f"parent // rot constraint 'relative': bone {parent_bone_index} is not updated yet!")
								continue

							origin_tr = glm_get_translation(parent_matrix)
							origin_rot = glm_get_quat(parent_matrix)

						case Space_Type.PARENT:  # 1
							parent_bone_index = constraint.rot_space_0.bone_index_0

							if parent_bone_index == -1:
								origin_rot = glm_get_quat(rest_matrices_object_space[bone_index])
								origin_tr = glm_get_translation(rest_matrices_object_space[bone_index])
							elif bone_updated[parent_bone_index]:
								parent_matrix = skeleton_bones_matrices[parent_bone_index]
								parent_tr = glm_get_translation(parent_matrix)
								parent_rot = glm_get_quat(parent_matrix)

								parent_offset_matrix = rest_matrices_parent_space[bone_index]
								parent_offset_tr = glm_get_translation(parent_offset_matrix)
								parent_offset_rot = glm_get_quat(parent_offset_matrix)

								origin_tr = parent_tr + parent_rot * parent_offset_tr
								origin_rot = parent_rot * parent_offset_rot
							else:
								logger.warning(f"parent // rot constraint 'parent': bone {parent_bone_index} is not updated yet!")
								continue

						case Space_Type.OBJECT:  # 2
							origin_tr = glm_get_translation(rest_matrices_object_space[0])
							origin_rot = glm_get_quat(rest_matrices_object_space[0])

						case Space_Type.BIND:  # 4
							zeroth_matrix = rest_matrices_object_space[0]
							zeroth_rot = glm_get_quat(zeroth_matrix)
							zeroth_tr = glm_get_translation(zeroth_matrix)

							bind_matrix = rest_matrices_object_space[bone_index]
							bind_rot = glm_get_quat(bind_matrix)
							bind_tr = glm_get_translation(bind_matrix)

							origin_tr = zeroth_tr + zeroth_rot * bind_tr
							origin_rot = zeroth_rot * bind_rot

						case Space_Type.AVERAGE:  # 5
							parent_0_index = constraint.rot_space_0.bone_index_0
							parent_1_index = constraint.rot_space_0.bone_index_1

							if parent_0_index == -1:
								parent_0_matrix = IDENTITY_MAT4
							elif bone_updated[parent_0_index]:
								parent_0_matrix = skeleton_bones_matrices[parent_0_index]
							else:
								logger.warning(f"parent // rot constraint 'average': bone 0 {parent_0_index} is not updated yet!")
								continue

							if parent_1_index == -1:
								parent_1_matrix = IDENTITY_MAT4
							elif bone_updated[parent_1_index]:
								parent_1_matrix = skeleton_bones_matrices[parent_1_index]
							else:
								logger.warning(f"parent // rot constraint 'average': bone 1 {parent_1_index} is not updated yet!")
								continue

							parent_0_tr = glm_get_translation(parent_0_matrix)
							parent_0_rot = glm_get_quat(parent_0_matrix)

							parent_1_tr = glm_get_translation(parent_1_matrix)
							parent_1_rot = glm_get_quat(parent_1_matrix)

							origin_tr = 0.5 * (parent_0_tr + parent_1_tr)
							origin_rot = glm.slerp(parent_0_rot, parent_1_rot, 0.5)

						case Space_Type.AIM:
							aim_influence = constraint.aim_influence

							origin_tr = glm.vec3(0, 0, 0)

							origin_rot = glm.slerp(glm.quat(), aim_quat, aim_influence)

							match translation_space.space_type:
								case Space_Type.RELATIVE | Space_Type.UNK_3:
									parent_bone_index = translation_space.bone_index_0

									if parent_bone_index == -1:
										parent_matrix = IDENTITY_MAT4
									elif bone_updated[parent_bone_index]:
										parent_matrix = skeleton_bones_matrices[parent_bone_index]
									else:
										logger.warning(f"parent // tr constraint 'relative': bone {parent_bone_index} is not updated yet!")
										continue

									origin_tr = glm_get_translation(parent_matrix)

								case Space_Type.PARENT:
									parent_bone_index = translation_space.bone_index_0

									if parent_bone_index == -1:
										origin_tr = glm_get_translation(rest_matrices_object_space[bone_index])
									elif bone_updated[parent_bone_index]:
										parent_matrix = skeleton_bones_matrices[parent_bone_index]
										parent_tr = glm_get_translation(parent_matrix)
										parent_rot = glm_get_quat(parent_matrix)

										parent_offset_matrix = rest_matrices_parent_space[bone_index]
										parent_offset_tr = glm_get_translation(parent_offset_matrix)

										origin_tr = parent_tr + parent_rot * parent_offset_tr
									else:
										logger.warning(f"parent // tr constraint 'parent': bone {parent_bone_index} is not updated yet!")
										continue

								case Space_Type.AVERAGE:
									parent_0_index = translation_space.bone_index_0
									parent_1_index = translation_space.bone_index_1

									if parent_0_index == -1:
										parent_0_matrix = IDENTITY_MAT4
									elif bone_updated[parent_0_index]:
										parent_0_matrix = skeleton_bones_matrices[parent_0_index]
									else:
										logger.warning(f"parent // tr constraint 'average': bone {parent_0_index} is not updated yet!")
										continue

									if parent_1_index == -1:
										parent_1_matrix = IDENTITY_MAT4
									elif bone_updated[parent_1_index]:
										parent_1_matrix = skeleton_bones_matrices[parent_1_index]
									else:
										logger.warning(f"parent // tr constraint 'average': bone {parent_1_index} is not updated yet!")
										continue

									parent_0_tr = glm_get_translation(parent_0_matrix)
									parent_1_tr = glm_get_translation(parent_1_matrix)
									origin_tr = 0.5 * (parent_0_tr + parent_1_tr)

					result_tr = origin_tr + origin_rot * animation_tr
					result_rot = origin_rot * animation_rot

					bone_matrix = glm_compose_mat4(result_tr, result_rot, animation_sc)
					skeleton_bones_matrices[bone_index] = bone_matrix

					bone_updated[bone_index] = True

			# functions this control has

		for bone_index in rig_cache.ik_3_chains:
			control_index = bone_to_control[bone_index]
			# RFK chain
			MAX_INBETWEEN = 16

			constraint = constraints[control_index]

			if constraint.ik_function_type == IK_Function_Type.RFK:
				if bone_index not in rig_cache.rfk_chains:
					raise Invalid_Rig_Error(
						f"{bone_index} should be an end of IK chain, but chain not found"
					)

				chain = rig_cache.rfk_chains[bone_index]

				start_bone_index = chain.start_bone_index
				end_bone_index = chain.end_bone_index

				if not bone_updated[start_bone_index]:
					logger.warning(f"rfk function // start bone {start_bone_index} is not updated yet!")
					continue

				if not bone_updated[end_bone_index]:
					logger.warning(f"rfk function // end bone {end_bone_index} is not updated yet!")
					continue

				inbetween = chain.bones_indices[1:-1][-MAX_INBETWEEN:]
				n = len(inbetween)

				if n > 0:
					pose_start = skeleton_bones_matrices[start_bone_index]
					rest_start_inv = glm.inverse(rest_matrices_object_space[start_bone_index])

					# end's current offset from start
					relative = glm.inverse(pose_start) * skeleton_bones_matrices[end_bone_index]

					for k, bone in enumerate(inbetween, start=1):
						t = k / (n + 1)

						# intermediate bone relative to start in rest pose
						rest_relative = rest_start_inv * rest_matrices_object_space[bone]
						# part of difference between start and end
						distributed = glm_interpolate_mat4(IDENTITY_MAT4, relative, t)
						# mix relative rest and difference
						skeleton_bones_matrices[bone] = pose_start * glm_interpolate_mat4(rest_relative, distributed, t)
						bone_updated[bone] = True

		for bone_index in rig_cache.ik_3_chains:
			control_index = bone_to_control[bone_index]

			constraint = constraints[control_index]
			# IK_3 chain
			if constraint.ik_function_type == IK_Function_Type.IK_3:
				if bone_index not in rig_cache.ik_3_chains:
					raise Invalid_Rig_Error(
						f"{bone_index} should be an end of IK chain, but chain not found"
					)

				chain = rig_cache.ik_3_chains[bone_index]

				start_bone_index = chain.start_bone_index
				middle_bone_index = chain.target_bone_index
				end_bone_index = chain.end_bone_index

				start_matrix = glm.mat4(skeleton_bones_matrices[start_bone_index]) # to copy matrix
				middle_matrix = start_matrix * rest_matrices_parent_space[middle_bone_index]
				end_matrix = middle_matrix * rest_matrices_parent_space[end_bone_index]

				target_matrix = skeleton_bones_matrices[end_bone_index]

				# TODO: add propagate and ik_3_solve_with_pole
				arr = ik_3_solve_no_pole(target_matrix, start_matrix, middle_matrix, end_matrix)

				if arr is None:
					continue

				start_new_matrix, middle_new_matrix, end_new_matrix = arr

				if start_bone_index > 0:
					skeleton_bones_matrices[start_bone_index] = start_new_matrix

				skeleton_bones_matrices[middle_bone_index] = middle_new_matrix
				bone_updated[middle_bone_index] = True
				skeleton_bones_matrices[end_bone_index] = end_new_matrix

		# store frame into converted animation
		for bone_index, updated in enumerate(bone_updated):
			if not updated:
				continue

			bone_matrix = skeleton_bones_matrices[bone_index]

			sc, rot, tr = glm_decompose_mat4(bone_matrix)

			# also if animation_scale is uniform, maybe make it average to reduce error?
			# animation_scale = (sc[0] + sc[1] + sc[2]) / 3.0
			# converted_animation[bone_index].scales[frame] = np.array([animation_scale, animation_scale, animation_scale])
			converted_animation[bone_index].scales[frame] = np.array([sc[0], sc[1], sc[2]])
			# glm uses (w, x, y, z) quat order
			converted_animation[bone_index].rotations[frame] = np.array([rot[1], rot[2], rot[3], rot[0]])  # move w to last position
			converted_animation[bone_index].translations[frame] = np.array([tr[0], tr[1], tr[2]])

	end_time = time.perf_counter()
	logger.info(f"Retarget finished, time: {end_time-start_time:.6f}s")

	return converted_animation
