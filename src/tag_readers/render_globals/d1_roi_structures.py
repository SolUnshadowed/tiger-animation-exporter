from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, u64, u32, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_64
from libs.tiger_pkg.tag_handle import Tag_Handle

from src.tag_readers.render_globals.unified_structures import (
	Unified_S_Vertex_Input_Element_Sets_Header, Unified_S_Vertex_Input_Element_Set_Pointer,
	Unified_Client_Bootstrap_Header, Unified_Render_Globals, Unified_S_Vertex_Input_Layouts,
	Unified_S_Vertex_Input_Layout_Mapping_Header
)

# ref 8106000E
@binary_struct()
@dataclass
class Client_Bootstrap_Header_D1_ROI:
	file_size: Annotated[int, u64]
	arr_pointer: Vec_Pointer_64  # second element in this array points to render_globals

	def to_unified(self) -> Unified_Client_Bootstrap_Header:
		return Unified_Client_Bootstrap_Header(self.file_size, self.arr_pointer)


# ref 80801BB0
@binary_struct()
@dataclass
class S_Render_Globals_Header_D1_ROI:
	file_size: Annotated[int, u64]
	input_layouts_tag_handle: Tag_Handle

	def to_unified(self) -> Unified_Render_Globals:
		return Unified_Render_Globals(self.file_size, self.input_layouts_tag_handle)


# ref 80801B63
@binary_struct(size=44)
@dataclass
class S_Vertex_Input_Layouts_D1_ROI:
	file_size: Annotated[int, u64]

	elements_1_tag_handle: Annotated[Tag_Handle, L_Padding(4)]
	elements_2_tag_handle: Tag_Handle

	element_mappings: Annotated[Tag_Handle, L_Padding(20)]  # should be the last tag

	def to_unified(self) -> Unified_S_Vertex_Input_Layouts:
		return Unified_S_Vertex_Input_Layouts(
			self.file_size,
			self.elements_1_tag_handle,
			self.elements_2_tag_handle,
			self.element_mappings
		)


# ref
@binary_struct()
@dataclass
class S_Vertex_Input_Layout_Mapping_Header_D1_ROI:
	file_size: Annotated[int, u64]
	arr_pointer: Vec_Pointer_64  # to array of S_Vertex_Layout

	def to_unified(self) -> Unified_S_Vertex_Input_Layout_Mapping_Header:
		return Unified_S_Vertex_Input_Layout_Mapping_Header(self.file_size, self.arr_pointer)


# ref 80801BDE
@binary_struct()
@dataclass
class S_Vertex_Input_Element_Sets_Header_D1_ROI:
	file_size: Annotated[int, u64]
	sets_pointer: Vec_Pointer_64

	def to_unified(self) -> Unified_S_Vertex_Input_Element_Sets_Header:
		return Unified_S_Vertex_Input_Element_Sets_Header(
			self.file_size,
			self.sets_pointer
		)


# ref 80801A98
@binary_struct()
@dataclass
class S_Vertex_Input_Element_Set_D1_ROI:
	elements_pointer: Vec_Pointer_64 # points to an array of S_Vertex_Input_Element

	def to_unified(self) -> Unified_S_Vertex_Input_Element_Set_Pointer:
		return Unified_S_Vertex_Input_Element_Set_Pointer(self.elements_pointer)