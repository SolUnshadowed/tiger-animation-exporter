from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, u32
from libs.tag.tag_pointers import Vec_Pointer_32
from libs.tiger_pkg.tag_handle import Tag_Handle

from src.tag_readers.s_technique.unified_structures import Unified_S_Technique_Header


@binary_struct()
@dataclass
class S_Technique_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]
	textures_handles_array_pointer: Vec_Pointer_32
	prob_channels_array_pointer: Vec_Pointer_32
	unk_14: Annotated[int, u32]
	pixel_shader_handle: Tag_Handle
	vertex_shader_handle: Tag_Handle

	def to_unified(self) -> Unified_S_Technique_Header:
		return Unified_S_Technique_Header(
			file_size=self.file_size,
			textures_handles_array_pointer=self.textures_handles_array_pointer,
			prob_channels_array_pointer=self.prob_channels_array_pointer,
			pixel_shader_handle=self.pixel_shader_handle,
			vertex_shader_handle=self.vertex_shader_handle,
		)
