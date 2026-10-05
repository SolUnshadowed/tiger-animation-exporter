from typing import Annotated

from dataclasses import dataclass

from libs.binary_reader import binary_struct, s8, u8, u16, s16, u32, L_Padding, Array
from libs.tag.data_types import Vec2, Vec4
from libs.tag.tag_pointers import  Vec_Pointer_32
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tiger.common import Primitive_Type

from src.tag_readers.s_entity_model.unified_structures import (
	Unified_S_Entity_Model_Header, Unified_S_Entity_Model_Mesh, Unified_Model_Mesh_Part
)


@binary_struct()
@dataclass
class S_Entity_Model_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]
	s_entity_model_mesh_array_pointer: Annotated[Vec_Pointer_32, L_Padding(4)]

	def to_unified(self) -> Unified_S_Entity_Model_Header:
		return Unified_S_Entity_Model_Header(self.file_size, self.s_entity_model_mesh_array_pointer)


@binary_struct(align=144)
@dataclass
class S_Entity_Model_Mesh_D1_DEVALPHA:  # type 8080201E
	model_scale: Vec4
	model_translation: Vec4
	texcoord_scale: Vec2
	texcoord_translation: Vec2
	vertex_buffer_1_tag_handle: Tag_Handle
	vertex_buffer_2_tag_handle: Tag_Handle
	old_weights_tag_handle: Tag_Handle
	vertex_buffer_4_tag_handle: Tag_Handle
	index_buffer_tag_handle: Tag_Handle
	parts_pointer: Vec_Pointer_32
	part_range_per_render_stage: Annotated[list[int], Array(u16, 19)]
	input_layout_per_render_stage: Annotated[list[int], Array(u8, 18)]


	def to_unified(self) -> Unified_S_Entity_Model_Mesh:
		return Unified_S_Entity_Model_Mesh(
			model_scale = self.model_scale,
			model_translation = self.model_translation,
			texcoord_scale=self.texcoord_scale,
			texcoord_translation=self.texcoord_translation,
			vertex_buffer_0_tag_handle=self.vertex_buffer_1_tag_handle,
			vertex_buffer_1_tag_handle=self.vertex_buffer_2_tag_handle,
			vertex_buffer_2_tag_handle=self.old_weights_tag_handle,
			vertex_buffer_3_tag_handle=self.vertex_buffer_4_tag_handle,
			index_buffer_tag_handle=self.index_buffer_tag_handle,
			parts_pointer=self.parts_pointer,
			part_range_per_render_stage=self.part_range_per_render_stage,
			input_layout_per_render_stage=self.input_layout_per_render_stage,
		)


@binary_struct(align=0x24)
@dataclass
class S_Render_Model_Mesh_Part_D1_DEVALPHA:  # type 80802019
	material: Tag_Handle
	variant_shader_index: Annotated[int, s16]
	primitive_type: Annotated[Primitive_Type, s16]
	index_offset: Annotated[int, u32]
	index_count: Annotated[int, u32]

	external_id: Annotated[int, u16, L_Padding(8)]

	flags: Annotated[int, u16, L_Padding(2)]
	gear_dye_change_color_index: Annotated[int, s8]
	lod_category: Annotated[int, s8]

	lod_run: Annotated[int, s8, L_Padding(1)]

	def to_unified(self) -> Unified_Model_Mesh_Part:
		return Unified_Model_Mesh_Part(
			technique_handle=self.material,
			variant_shader_index=self.variant_shader_index,
			primitive_type=self.primitive_type,
			index_offset=self.index_offset,
			index_count=self.index_count,
			external_id=self.external_id,
			flags=self.flags,
			gear_dye_change_color_index=self.gear_dye_change_color_index,
			lod_category=self.lod_category,
			lod_run=self.lod_run,
		)
