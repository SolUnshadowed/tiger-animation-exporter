from typing import Annotated

from dataclasses import dataclass

from libs.binary_reader import binary_struct, s8, u8, s16, u16, u32, u64, L_Padding, Array
from libs.tag.data_types import Vec2, Vec4
from libs.tag.tag_pointers import Vec_Pointer_64
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tiger.common import Primitive_Type
from src.tag_readers.s_entity_model.unified_structures import (
	Unified_S_Entity_Model_Header, Unified_S_Entity_Model_Mesh, Unified_Model_Mesh_Part
)


@binary_struct()
@dataclass
class S_Entity_Model_Header_D1_ROI:
	file_size: Annotated[int, u64]
	s_entity_model_mesh_array_pointer: Annotated[Vec_Pointer_64, L_Padding(8)]

	def to_unified(self) -> Unified_S_Entity_Model_Header:
		return Unified_S_Entity_Model_Header(self.file_size, self.s_entity_model_mesh_array_pointer)


@binary_struct(align=160)
@dataclass
class S_Entity_Model_Mesh_D1_ROI:  # type 80801BBF
	model_scale: Vec4
	model_translation: Vec4
	texcoord_scale: Vec2
	texcoord_translation: Vec2
	vertex_buffer_1_tag_handle: Tag_Handle  # positions
	vertex_buffer_2_tag_handle: Tag_Handle  # normals
	old_weights_tag_handle: Tag_Handle
	vertex_buffer_4_tag_handle: Tag_Handle
	index_buffer_tag_handle: Tag_Handle

	parts_pointer: Annotated[Vec_Pointer_64, L_Padding(4)]
	part_range_per_render_stage: Annotated[list[int], Array(u16, 20)]
	input_layout_per_render_stage: Annotated[list[int], Array(u8, 19)]

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

# S_Render_Model_Mesh_Part_D1_ROI: # type 80801AEF
