from dataclasses import dataclass

from libs.tag.tag_pointers import Base_Vec_Pointer
from libs.tiger_pkg.tag_handle import Tag_Handle

from src.tag_readers.render_globals.common_structures import Client_Bootstrap_Array_Element


@dataclass
class Unified_Client_Bootstrap_Header:
	file_size: int
	arr_pointer: Base_Vec_Pointer  # second element in this array points to render_globals


@dataclass
class Unified_Client_Bootstrap:
	header: Unified_Client_Bootstrap_Header

	array: list[Tag_Handle]


@dataclass
class Unified_Render_Globals:
	file_size: int
	input_layouts_tag_handle: Tag_Handle


@dataclass
class Unified_S_Vertex_Input_Layouts:
	file_size: int

	elements_1_tag_handle: Tag_Handle
	elements_2_tag_handle: Tag_Handle

	element_mappings: Tag_Handle


@dataclass
class Unified_S_Vertex_Input_Layout_Mapping_Header:
	file_size: int
	arr_pointer: Base_Vec_Pointer  # to array of S_Vertex_Layout


@dataclass
class Unified_S_Vertex_Input_Element_Sets_Header:
	file_size: int
	sets_pointer: Base_Vec_Pointer


@dataclass
class Unified_S_Vertex_Input_Element_Set_Pointer:
	elements_pointer: Base_Vec_Pointer  # points to an array of S_Vertex_Input_Element
