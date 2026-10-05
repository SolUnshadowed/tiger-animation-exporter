from dataclasses import dataclass

from libs.tag.tag_pointers import Base_Vec_Pointer
from libs.tiger_pkg.tag_handle import Tag_Handle


@dataclass
class Unified_S_Technique_Header:
	file_size: int
	textures_handles_array_pointer: Base_Vec_Pointer
	prob_channels_array_pointer: Base_Vec_Pointer
	pixel_shader_handle: Tag_Handle
	vertex_shader_handle: Tag_Handle
