from dataclasses import dataclass, field

from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tag.data_types import Vec2, Vec4
from libs.tag.tag_pointers import Base_Vec_Pointer
from libs.tiger.common import Primitive_Type


@dataclass
class Unified_S_Entity_Model_Header:
	file_size: int
	s_entity_model_mesh_array_pointer: Base_Vec_Pointer


@dataclass
class Unified_S_Entity_Model_Mesh:
	vertex_buffer_0_tag_handle: Tag_Handle
	index_buffer_tag_handle: Tag_Handle
	parts_pointer: Base_Vec_Pointer
	part_range_per_render_stage: list[int]
	input_layout_per_render_stage: list[int]

	model_scale: Vec4 = field(
		default_factory=lambda: Vec4((1, 1, 1, 1))
	)
	model_translation: Vec4 = field(
		default_factory=lambda: Vec4((0, 0, 0, 0))
	)
	texcoord_scale: Vec2 = field(
		default_factory=lambda: Vec2((1, 1))
	)
	texcoord_translation: Vec2 = field(
		default_factory=lambda: Vec2((0, 0))
	)

	vertex_buffer_1_tag_handle: Tag_Handle = field(
		default_factory=lambda: Tag_Handle(0xffffffff)
	)
	vertex_buffer_2_tag_handle: Tag_Handle = field(
		default_factory=lambda: Tag_Handle(0xffffffff)
	)
	vertex_buffer_3_tag_handle: Tag_Handle = field(
		default_factory=lambda: Tag_Handle(0xffffffff)
	)
	vertex_color_tag_handle: Tag_Handle = field(
		default_factory=lambda: Tag_Handle(0xffffffff)
	)
	single_pass_skin_buffer_tag_handle: Tag_Handle = field(
		default_factory=lambda: Tag_Handle(0xffffffff)
	)

	def get_range_for_stage(self, stage: int) -> tuple[int, int]:
		start = self.part_range_per_render_stage[stage]
		end = self.part_range_per_render_stage[stage + 1]
		return start, end

	def get_input_layout_for_stage(self, stage: int) -> int:
		return self.input_layout_per_render_stage[stage]


@dataclass
class Unified_Model_Mesh_Part:
	technique_handle: Tag_Handle
	variant_shader_index: int
	primitive_type: Primitive_Type
	index_offset: int
	index_count: int
	external_id: int
	flags:  int
	gear_dye_change_color_index: int
	lod_category: int
	lod_run: int