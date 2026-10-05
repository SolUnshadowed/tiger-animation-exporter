from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, u8, u32, s32, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_32
from libs.tiger_pkg.tag_handle import Tag_Handle

from src.tag_readers.render_globals.unified_structures import (
	Unified_S_Vertex_Input_Element_Sets_Header, Unified_S_Vertex_Input_Element_Set_Pointer,
	Unified_Client_Bootstrap_Header, Unified_Render_Globals_Header, Unified_S_Vertex_Input_Layouts,
	Unified_S_Vertex_Input_Layout_Mapping_Header
)


# ref ????????
@binary_struct()
@dataclass
class Client_Bootstrap_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]
	arr_pointer: Vec_Pointer_32  # second element in this array points to render_globals

	def to_unified(self) -> Unified_Client_Bootstrap_Header:
		return Unified_Client_Bootstrap_Header(self.file_size, self.arr_pointer)



# ref 80802373
@binary_struct()
@dataclass
class S_Render_Globals_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]
	input_layouts_tag_handle: Tag_Handle

	def to_unified(self) -> Unified_Render_Globals_Header:
		return Unified_Render_Globals_Header(self.file_size, self.input_layouts_tag_handle)


# ref 808022EE
@binary_struct(size=40)
@dataclass
class S_Vertex_Input_Layouts_D1_DEVALPHA:
	file_size: Annotated[int, u32]

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


# ref 808022E9
@binary_struct()
@dataclass
class S_Vertex_Input_Layout_Mapping_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]
	arr_pointer: Vec_Pointer_32  # to array of S_Vertex_Layout

	def to_unified(self) -> Unified_S_Vertex_Input_Layout_Mapping_Header:
		return Unified_S_Vertex_Input_Layout_Mapping_Header(self.file_size, self.arr_pointer)


# ref 808022E6
@binary_struct()
@dataclass
class S_Vertex_Input_Element_Sets_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]
	sets_pointer: Vec_Pointer_32

	def to_unified(self) -> Unified_S_Vertex_Input_Element_Sets_Header:
		return Unified_S_Vertex_Input_Element_Sets_Header(
			self.file_size,
			self.sets_pointer
		)


# type 808022E4
@binary_struct()
@dataclass
class S_Vertex_Input_Element_Set_D1_DEVALPHA:
	elements_pointer: Vec_Pointer_32 # points to an array of S_Vertex_Input_Element

	def to_unified(self) -> Unified_S_Vertex_Input_Element_Set_Pointer:
		return Unified_S_Vertex_Input_Element_Set_Pointer(self.elements_pointer)