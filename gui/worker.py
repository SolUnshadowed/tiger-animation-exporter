import logging
import numpy as np

from PySide6.QtCore import Signal, QObject, Slot
from pathlib import Path
from dataclasses import dataclass

from libs.tiger_pkg.manager.package_manager import Package_Manager, PROGRESS as Package_Manager_Progress
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.enums import Package_Platform
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.binary_reader import Binary_Reader, u32
from libs.tiger.buffer_decoder.d1_vertex_types import d1_devalpha_types
from libs.tiger.buffer_decoder.buffer_decoder import decode_vertex_buffer
from libs.tiger.shaders.input_layouts import Input_Semantics
from libs.tiger.common import Primitive_Type

from src.tag_readers.skeleton.read_skeleton import read_skeleton, Skeleton
from src.tag_readers.runtime_rig.read_runtime_rig import read_runtime_rig, Runtime_Rig_Data
from src.tag_readers.animation.read_animation import read_animation, Animation_Data
from src.tag_readers.s_pattern.read_s_pattern import read_s_pattern
from src.tag_readers.s_pattern_component.read_s_pattern_component import read_s_pattern_component_header
from src.tag_readers.s_dynamic_model_component.read_s_dynamic_model_component import read_dynamic_model_component
from src.tag_readers.s_entity_model.read_s_entity_model import read_s_entity_model
from src.tag_readers.buffers.read_buffers import read_index_buffer, read_vertex_buffer
from src.tag_readers.render_globals.read_client_bootstrap import read_client_bootstrap
from src.tag_readers.render_globals.read_render_globals import read_render_globals_header
from src.tag_readers.render_globals.read_s_vertex_input_layouts import read_s_vertex_input_layouts
from src.tag_readers.render_globals.read_s_vertex_input_element_sets import read_s_vertex_element_sets, S_Vertex_Input_Element_Set
from src.tag_readers.render_globals.read_s_vertex_input_layout_mapping import read_s_vertex_input_layout_mapping, S_Vertex_Layout

from src.decode_animation.decode_animation import decode_animation, Bone_Tracks
from src.export.animation_export.convert_animation_object_to_local import convert_obj_to_local
from src.export.animation_export.gltf_export import create_gltf, add_animation, save_gltf
from src.export.animation_export.export_animation import animation_to_json, write_json_file
from src.export.animation_export.enums import Bone_Name_Convention, Animation_Space, Export_Target
from src.runtime_rig.rig_retarget import rig_retarget
from src.scanner.animation_scanner import Animation_Scanner, PROGRESS as Animation_Scanner_Progress
from src.scanner.classes import s_pattern_refs, s_dynamic_model_component_secondary_classes
from src.buffers.vertex_buffer import Vertex_Buffer
from src.buffers.index_buffer import Index_Buffer

from gui.worker_types import Tag_Model, Package_Model, Animation_Model, Model_Properties, Render_Data, Entity_Data


logger = logging.getLogger(__name__)


@dataclass
class Export_Settings:
	name_convention: Bone_Name_Convention
	animation_space: Animation_Space
	export_target: Export_Target
	json_indent: None | int


@dataclass
class Cached_Animation:
	animation_handle: int
	animation_data: Animation_Data
	raw_animation: list[Bone_Tracks | None]
	object_space_animation: list[Bone_Tracks]
	local_space_animation: list[Bone_Tracks]


@dataclass
class State:
	skeleton: Skeleton
	rig: Runtime_Rig_Data
	animation: None | Cached_Animation


@dataclass
class Vertex_Data:
	element_sets: list[S_Vertex_Input_Element_Set]
	layouts: list[S_Vertex_Layout]


@dataclass
class Worker_Data:
	cache_path: Path
	packages_path: Path
	game_version: Game_Version
	platform: Package_Platform | None


class Package_Worker(QObject):
	package_list_ready_emitter = Signal(list)
	non_redacted_entities_for_package_ready_emitter = Signal(list)
	entity_data_emitter = Signal(object)
	animations_list_emitter = Signal(list)
	render_data_emitter = Signal(object)
	animation_emitter = Signal(object)
	worker_started = Signal(bool)
	loading_waiting = Signal(str)
	loading_progress = Signal(object)
	loading_hide = Signal()

	state: State | None
	manager: Package_Manager
	scanner: Animation_Scanner
	vertex_data: Vertex_Data | None
	vertex_data_2: Vertex_Data | None
	export_settings: Export_Settings
	export_path: Path

	def __init__(self,export_settings: Export_Settings):
		super().__init__()
		self.export_settings = export_settings

	def set_data(self, data: Worker_Data):
		self.loading_progress.emit(Package_Manager_Progress)
		self.manager = Package_Manager(data.game_version, data.platform, data.packages_path, data.cache_path)
		self.loading_progress.emit(Animation_Scanner_Progress)
		self.scanner = Animation_Scanner(self.manager, data.cache_path)
		self.loading_waiting.emit("Continue misc tasks")
		self.export_path = data.cache_path / "exports"
		self.vertex_data = None
		self.state = None

		try:
			self.vertex_data = self.get_vertex_layouts()
			self.vertex_data_2 = self.get_vertex_layouts(2)
			logger.info("Vertex element sets are loaded")
		except Exception:
			logger.warning("Vertex element sets were not loaded")

		self.worker_started.emit(True)

	def get_vertex_layouts(self, layout_index: int = 1) -> Vertex_Data | None:
		game_version = self.manager.version

		client_bootstrap_tag_handle = self.manager.get_named_tag("client_bootstrap_patchable")

		if client_bootstrap_tag_handle is None:
			return None

		endianness = self.manager.get_or_load_pkg(client_bootstrap_tag_handle.package_id).endianness
		client_bootstrap_reader = Binary_Reader(self.manager.read_tag(client_bootstrap_tag_handle))
		client_bootstrap = read_client_bootstrap(client_bootstrap_reader, game_version, endianness)

		render_globals_tag_handle = client_bootstrap.array[1].handle
		render_globals_reader = Binary_Reader(self.manager.read_tag(render_globals_tag_handle))
		render_globals_header = read_render_globals_header(render_globals_reader, game_version, endianness)

		input_layouts_tag_handle = render_globals_header.input_layouts_tag_handle
		input_layouts_reader = Binary_Reader(self.manager.read_tag(input_layouts_tag_handle))
		input_layouts = read_s_vertex_input_layouts(input_layouts_reader, game_version, endianness)

		elements_handle = input_layouts.elements_1_tag_handle if layout_index == 1 else input_layouts.elements_2_tag_handle
		element_sets_reader = Binary_Reader(self.manager.read_tag(elements_handle))
		element_sets = read_s_vertex_element_sets(element_sets_reader, game_version, endianness)

		element_mappings_handle = input_layouts.element_mappings
		element_mappings_reader = Binary_Reader(self.manager.read_tag(element_mappings_handle))
		element_mappings = read_s_vertex_input_layout_mapping(element_mappings_reader, game_version, endianness)

		return Vertex_Data(element_sets, element_mappings.layouts)

	@Slot(list)
	def get_packages_list(self):
		self.loading_waiting.emit("Loading")

		self.package_list_ready_emitter.emit(
			[
				Package_Model(package_id, package_path.filename)
				for package_id, package_path in sorted(
					self.manager.package_paths.items(), key=lambda x: x[0]
				)
			]
		)

		self.loading_hide.emit()

	@Slot(list)
	def get_non_redacted_entities_for_package(self, package_id: int):
		self.loading_waiting.emit("Loading")

		self.non_redacted_entities_for_package_ready_emitter.emit(
			[
				Tag_Model(
					Tag_Handle.new(package_id, entry_index).value,
					entry_header.file_size,
					entry_header.reference,
					entry_index
				)
				for entry_index, entry_header in self.manager.get_or_load_pkg(package_id).get_all_by_reference(
					s_pattern_refs[self.manager.version]
				)
				if Tag_Handle.new(package_id, entry_index).value in self.scanner.cache.entities
			]
		)

		self.loading_hide.emit()

	def get_model_buffers(self, entity_handle: Tag_Handle) -> list[None | Model_Properties]:
		game_version = self.manager.version
		endianness = self.manager.get_or_load_pkg(entity_handle.package_id).endianness

		if self.manager.version is not Game_Version.D1_DEV_ALPHA:
			return []

		try:
			entity_reader = Binary_Reader(self.manager.read_tag(entity_handle))

			s_pattern = read_s_pattern(entity_reader, game_version, endianness)

			dynamic_model_component_handle = None

			for component_handle in s_pattern.component_tag_handles:
				component_reader = Binary_Reader(self.manager.read_tag(component_handle))
				component_header = read_s_pattern_component_header(component_reader, game_version, endianness)

				component_reader.seek(component_header.default_instance_pointer.get_address() - 4)

				val = u32.read_from(component_reader, endianness)

				if val == s_dynamic_model_component_secondary_classes[self.manager.version]:

					dynamic_model_component_handle = component_handle
					break

			if dynamic_model_component_handle is None:
				logger.warning("dynamic_model_component_handle is none")
				return []

			dynamic_model_component_reader = Binary_Reader(self.manager.read_tag(dynamic_model_component_handle))
			model_component = read_dynamic_model_component(dynamic_model_component_reader, game_version, endianness)

			model_handle = model_component.model_handle
			model_reader = Binary_Reader(self.manager.read_tag(model_handle))

			model = read_s_entity_model(model_reader, game_version, endianness)
			model_buffers = [None for _ in model.meshes]

			for mesh_index, mesh in enumerate(model.meshes):
				vertex_buffers: list[None | Vertex_Buffer] = [None, None, None, None]

				layout_index = mesh.get_input_layout_for_stage(0)
				layout = self.vertex_data.layouts[layout_index - self.vertex_data.layouts[0].index]

				buffers_data: list[tuple[Tag_Handle, int]] = [
					(mesh.vertex_buffer_0_tag_handle, layout.buffer_0_element_set_index),
					(mesh.vertex_buffer_1_tag_handle, layout.buffer_1_element_set_index),
					(mesh.vertex_buffer_2_tag_handle, layout.buffer_2_element_set_index),
					(mesh.vertex_buffer_3_tag_handle, layout.buffer_3_element_set_index),
				]

				for buffer_index, (buffer_handle, element_set_index) in enumerate(buffers_data):
					if buffer_handle.is_valid and element_set_index != -1:
						buffer_reader = Binary_Reader(self.manager.read_tag(buffer_handle))
						buffer_header = read_vertex_buffer(buffer_reader, game_version, endianness)

						entry_header = self.manager.get_entry(buffer_handle)
						buffer_byte_data = self.manager.read_tag(Tag_Handle(entry_header.reference))

						vertex_buffers[buffer_index] = Vertex_Buffer(
							buffer_header,
							buffer_byte_data,
							self.vertex_data.element_sets[element_set_index]
						)

						logger.info(f"buffer {buffer_index} layout: {vertex_buffers[buffer_index].element_set}")
					else:
						logger.info(f"buffer {buffer_index} is not present")

				# mesh_index buffer
				buffer_reader = Binary_Reader(self.manager.read_tag(mesh.index_buffer_tag_handle))
				buffer_header = read_index_buffer(buffer_reader, game_version, endianness)

				entry_header = self.manager.get_entry(mesh.index_buffer_tag_handle)
				buffer_byte_data = self.manager.read_tag(Tag_Handle(entry_header.reference))

				index_buffer: Index_Buffer = Index_Buffer(buffer_header, buffer_byte_data)

				part_list = model.parts[mesh_index]

				ranges: list[tuple[int, int, Primitive_Type]] = []

				for i, part in enumerate(part_list):
					if part.lod_category in [0, 1, 2, 3]:
						ranges.append((part.index_offset, part.index_count, part.primitive_type))

				if len(ranges) == 0:
					continue

				semantic_data: dict[tuple[Input_Semantics, int], np.ndarray] = dict()

				for vertex_buffer in vertex_buffers:
					if vertex_buffer is not None:
						stride = vertex_buffer.header.stride
						offset = 0

						for input_element in vertex_buffer.element_set:
							try:
								vertex_type = d1_devalpha_types[input_element.format]

								data = decode_vertex_buffer(vertex_buffer.data, vertex_type, endianness, stride, offset)
								semantic_data[(input_element.semantic, input_element.semantic_index)] = data

								offset += vertex_type.byte_size
							except Exception:
								raise NotImplementedError(f"input element format {input_element.format} is not implemented")

				position_buffer = None
				normals_buffer = None
				skin_weights = None
				skin_indices = None

				if (Input_Semantics.POSITION, 0) in semantic_data:
					t = semantic_data[(Input_Semantics.POSITION, 0)]  #[:, [1, 2, 0]]
					if game_version == Game_Version.D1_DEV_ALPHA:
						t = np.column_stack((t[:, 1], t[:, 0], t[:, 2]))
					else:
						t = np.column_stack((t[:, 1], t[:, 2], t[:, 0]))
					position_buffer = t

				if (Input_Semantics.NORMAL, 0) in semantic_data:
					t = semantic_data[(Input_Semantics.NORMAL, 0)]  # [:, [1, 2, 0]]
					if game_version == Game_Version.D1_DEV_ALPHA:
						t = np.column_stack((t[:, 1], t[:, 0], t[:, 2]))
					else:
						t = np.column_stack((t[:, 1], t[:, 2], t[:, 0]))
					normals_buffer = t

				if (Input_Semantics.BLENDWEIGHT, 0) in semantic_data:
					skin_weights = semantic_data[(Input_Semantics.BLENDWEIGHT, 0)]

				if (Input_Semantics.BLENDINDICES, 0) in semantic_data:
					skin_indices = semantic_data[(Input_Semantics.BLENDINDICES, 0)]

				if (Input_Semantics.BLENDINDICES, 0) in semantic_data and (Input_Semantics.BLENDWEIGHT, 0) not in semantic_data:
					data = semantic_data[(Input_Semantics.BLENDINDICES, 0)]
					if data[0][0] + data[0][1] == 255:  # indices and weights in one buffer
						skin_weights = np.zeros((data.shape[0], 4), dtype=np.float32)
						skin_indices = np.zeros((data.shape[0], 4), dtype=np.uint32)

						skin_weights[:, :2] = data[:, :2] / 255.0
						skin_indices[:, :2] = data[:, 2:4]

				if (Input_Semantics.TEXCOORD, 0) in semantic_data:
					data = semantic_data[(Input_Semantics.TEXCOORD, 0)]

					if (
						data.shape[1] == 4 and
						(Input_Semantics.BLENDINDICES, 0) not in semantic_data and
						(Input_Semantics.BLENDWEIGHT, 0) not in semantic_data
					):
						data = semantic_data[(Input_Semantics.TEXCOORD, 0)]

						skin_indices = np.zeros((len(data), 4), dtype=np.uint32)
						skin_weights = np.zeros((len(data), 4), dtype=np.float32)

						skin_indices[:, 0] = data[:, 3] * 32768
						skin_weights[:, 0] = 1.0

				index_buffer_np_arr = index_buffer.get_np_array(endianness, ranges)

				model_scale = mesh.model_scale.data
				model_translation = mesh.model_translation.data

				model_scale = (model_scale[1], model_scale[2], model_scale[0])
				model_translation = (model_translation[1], model_translation[2], model_translation[0])

				if position_buffer is not None and normals_buffer is not None:
					model_buffers[mesh_index] = Model_Properties(
						model_scale, model_translation,
						position_buffer, normals_buffer, index_buffer_np_arr, skin_weights, skin_indices
					)
			return model_buffers

		except Exception as e:
			logger.error(e)
			return []

	@Slot("quint32")
	def select_entity(self, entity_handle_int: int):
		self.loading_waiting.emit("Loading")

		self.state = None

		entity_handle = Tag_Handle(entity_handle_int)
		entity_data = self.scanner.cache.entities.get(entity_handle_int)

		rig = None
		skeleton = None
		animation_tags = []
		game_version = self.manager.version
		entity_package = self.manager.get_or_load_pkg(entity_handle.package_id)
		endianness = entity_package.endianness

		if entity_data is None:
			logger.error(f"No cache entry for entity {hex(entity_handle_int)}")
			return

		rig_handle = entity_data.rig_tag_handle
		skeleton_handle = entity_data.skeleton_tag_handle

		try:
			# read skeleton
			reader = Binary_Reader(self.manager.read_tag(skeleton_handle))
			skeleton = read_skeleton(reader, game_version, endianness)

			# read rig
			reader = Binary_Reader(self.manager.read_tag(rig_handle))
			rig = read_runtime_rig(reader, game_version, endianness)

		except Exception as e:
			logger.error(f"Error while reading entity {hex(entity_handle_int)}, {e}")
			return

		components_hashes = [component.hash for component in rig.rig_components]

		animations_handles = self.scanner.cache.prefix_tree.find_full(components_hashes)
		animation_tags = []

		for animation_handle_int in animations_handles:
			handle = Tag_Handle(animation_handle_int)
			header = self.manager.get_entry(handle)

			animation_tags.append(
				Tag_Model(
					animation_handle_int,
					header.file_size,
					header.reference,
					handle.entry_index
				)
			)

		if rig is None or skeleton is None:
			logger.error(f"No skeleton or runtime rig for entity {hex(entity_handle_int)}")
			return

		self.state = State(skeleton, rig, None)

		model_buffers = self.get_model_buffers(entity_handle)

		self.animations_list_emitter.emit(animation_tags)
		self.entity_data_emitter.emit(
			Entity_Data(
				entity_handle_int,
				self.manager.package_paths[entity_handle.package_id].filename
			)
		)
		self.render_data_emitter.emit(
			Render_Data(
				skeleton,
				model_buffers
			)
		)

		self.loading_hide.emit()

	@Slot("quint32")
	def get_animation(self, animation_handle_int: int):
		if self.state is None:
			logger.error("No skeleton and rig selected")
			return

		self.loading_waiting.emit("Loading")

		animation_handle = Tag_Handle(animation_handle_int)

		try:
			reader = Binary_Reader(self.manager.read_tag(animation_handle))

			animation = read_animation(
				reader,
			   	self.manager.version,
				self.manager.get_or_load_pkg(animation_handle.package_id).endianness
			)

			tracks = decode_animation(animation)

			retargeted_animation = rig_retarget(animation, tracks, self.state.skeleton, self.state.rig)

			local_tracks = convert_obj_to_local(animation, retargeted_animation, self.state.skeleton)

			self.state.animation = Cached_Animation(
				animation_handle=animation_handle_int,
				animation_data=animation,
				raw_animation=tracks,
				object_space_animation=retargeted_animation,
				local_space_animation=local_tracks
			)

			self.animation_emitter.emit(
				Animation_Model(
					animation_handle_int,
					animation,
					local_tracks
				)
			)
		except Exception as e:
			logger.error(e)

		self.loading_hide.emit()

	def export_animation(self):
		if self.export_path is None:
			logger.error("No export path")
			return

		if self.state is None:
			logger.error("No skeleton and rig selected")
			return

		if self.state.animation is None:
			logger.error("No animation selected")
			return

		self.loading_waiting.emit("Loading")

		if not self.export_path.exists():
			self.export_path.mkdir(parents=True, exist_ok=True)

		export_target = self.export_settings.export_target
		animation_data = self.state.animation.animation_data
		animation_handle = self.state.animation.animation_handle

		if export_target == Export_Target.JSON_RAW:
			logger.info(f"Used export target: {Export_Target.JSON_RAW.value}")

			result_filename = f"s_animation_clip_{animation_handle:08X}_raw.json"
			# no bones annotations, because these are controls
			animation_json = animation_to_json(animation_data, self.state.animation.raw_animation)
			write_json_file(self.export_path / result_filename, animation_json, self.export_settings.json_indent)

		else:
			logger.info(f"Used export target: {export_target.value}")

			result_tracks = self.state.animation.object_space_animation \
				if self.export_settings.animation_space == Animation_Space.OBJECT \
				else self.state.animation.local_space_animation

			if export_target == Export_Target.JSON_RETARGET:
				result_filename =  f"s_animation_clip_{animation_handle:08X}.json"
				animation_json = animation_to_json(animation_data, result_tracks)
				write_json_file(self.export_path / result_filename, animation_json, self.export_settings.json_indent)

			elif export_target == Export_Target.GLTF_RETARGET:
				result_filename = f"s_animation_clip_{animation_handle:08X}.gltf"

				gltf, indices = create_gltf(self.state.skeleton, self.export_settings.animation_space, self.export_settings.name_convention)

				add_animation(gltf, indices, result_tracks, self.export_settings.name_convention, f"{animation_handle:08X}")

				save_gltf(gltf, self.export_path / result_filename)

		self.loading_hide.emit()
