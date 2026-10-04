import numpy as np

from dataclasses import dataclass
from pyglm import glm

from libs.tiger_pkg.game_version import Game_Version
from libs.binary_reader import Endianness, Binary_Reader
from libs.matrix_operations import glm_compose_mat4
from libs.tag.tag_pointers import Base_Vec_Pointer, Base_Tag_Pointer
from libs.tag.tag_array import Tag_Array
from libs.tag.data_types import Skeleton_Node_Def, Transform

from src.tag_readers.s_pattern_component.read_s_pattern_component import read_s_pattern_component_header
from src.tag_readers.skeleton.d1_devalpha_structures import D1_DEVALPHA_Skeleton_Main_Struct
from src.tag_readers.skeleton.d1_roi_strucutres import D1_ROI_Skeleton_Main_Struct
from src.tag_readers.skeleton.d2_eof_structures import D2_EOF_Skeleton_Main_Struct
from src.tag_readers.skeleton.marathon_structures import MARATHON_Skeleton_Main_Struct
from src.tag_readers.skeleton.unified_structures import Unified_Skeleton_Main_Struct




def transform_to_glm_mat4(transform: Transform):
	ts = transform.ts
	r = transform.r

	scale = glm.vec3(ts[3], ts[3], ts[3])
	translation = glm.vec3(ts[0], ts[1], ts[2])

	# w is on 0th place (w, x, y, z) in glm quats
	quat = glm.quat(r[3], r[0], r[1], r[2])

	return glm_compose_mat4(translation, quat, scale)


def transform_to_np_matrix(transform: Transform):
	return np.array(transform_to_glm_mat4(transform))


@dataclass(slots=True)
class Skeleton_Main_Struct:
	bone_hierarchy_pointer: Base_Vec_Pointer
	default_obj_space_tr_pointer: Base_Vec_Pointer
	default_inv_obj_space_tr_pointer: Base_Vec_Pointer


class Skeleton:
	__slots__ = [
		"node_defs",
		"default_obj_space_tr",
		"default_inv_obj_space_tr",
		"default_obj_space_matrices",
		"default_inv_obj_space_matrices",
		"bone_to_parent_offset"
	]

	node_defs: list[Skeleton_Node_Def]
	default_obj_space_tr: list[Transform]
	default_inv_obj_space_tr: list[Transform]
	default_obj_space_matrices: list
	default_inv_obj_space_matrices: list
	bone_to_parent_offset: list


	def __init__(
		self,
		node_defs: list[Skeleton_Node_Def],
		default_obj_space_tr: list[Transform],
		default_inv_obj_space_tr: list[Transform]
	):
		self.node_defs = node_defs
		self.default_obj_space_tr = default_obj_space_tr
		self.default_inv_obj_space_tr = default_inv_obj_space_tr

		default_obj_space_tr = default_obj_space_tr
		default_inv_obj_space_tr = default_inv_obj_space_tr

		# compute reference bone matrices
		self.default_obj_space_matrices = [transform_to_glm_mat4(transform) for transform in default_obj_space_tr]
		self.default_inv_obj_space_matrices = [transform_to_glm_mat4(transform) for transform in default_inv_obj_space_tr]
		self.bone_to_parent_offset = []

		# compute bone to parent offsets
		for bone_index, current_bone_matrix in enumerate(self.default_obj_space_matrices):
			bone_relation = node_defs[bone_index]
			parent_bone_index = bone_relation.parent_node_index

			if parent_bone_index > -1:
				parent_bone = self.default_inv_obj_space_matrices[parent_bone_index]
				parent_offset_matrix = parent_bone * current_bone_matrix
				self.bone_to_parent_offset.append(parent_offset_matrix)
			else:
				self.bone_to_parent_offset.append(glm.mat4(current_bone_matrix))


def read_skeleton_main_struct(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, pointer: Base_Tag_Pointer
) -> Unified_Skeleton_Main_Struct:
	reader.seek(pointer.get_address())

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(D1_DEVALPHA_Skeleton_Main_Struct, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(D1_ROI_Skeleton_Main_Struct, override_endianness=endianness).to_unified()
		case Game_Version.D2_EOF:
			return reader.read_struct(D2_EOF_Skeleton_Main_Struct, override_endianness=endianness).to_unified()
		case Game_Version.MARATHON:
			return reader.read_struct(MARATHON_Skeleton_Main_Struct, override_endianness=endianness).to_unified()


def read_skeleton_data(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, main_struct: Unified_Skeleton_Main_Struct
) -> Skeleton:
	bitness = game_version.pointer_block_bitness()

	bone_hierarchy = Tag_Array[Skeleton_Node_Def](
		reader, main_struct.bone_hierarchy_pointer, Skeleton_Node_Def, endianness, bitness
	).payload
	obj_space_tr = Tag_Array[Transform](
		reader, main_struct.obj_space_tr_pointer, Transform, endianness, bitness
	).payload
	inv_obj_space_tr = Tag_Array[Transform](
		reader, main_struct.inv_obj_space_tr_pointer, Transform, endianness, bitness
	).payload

	return Skeleton(
		node_defs=bone_hierarchy,
		default_obj_space_tr=obj_space_tr,
		default_inv_obj_space_tr=inv_obj_space_tr
	)


def read_skeleton(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Skeleton:
	header = read_s_pattern_component_header(reader, game_version, endianness)

	main_struct = read_skeleton_main_struct(reader, game_version, endianness, header.definition_pointer)

	skeleton: Skeleton = read_skeleton_data(reader, game_version, endianness, main_struct)

	return skeleton
