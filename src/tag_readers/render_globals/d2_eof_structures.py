from typing import Annotated
from dataclasses import dataclass


from libs.binary_reader import binary_struct, u8, u64, u32, s32, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_64
from libs.tiger_pkg.tag_handle import Tag_Handle, Wide_Tag_Handle

from src.tag_readers.render_globals.unified_structures import (
    Unified_S_Vertex_Input_Element_Sets_Header, Unified_S_Vertex_Input_Element_Set_Pointer,
    Unified_Client_Bootstrap_Header, Unified_Render_Globals, Unified_S_Vertex_Input_Layouts,
    Unified_S_Vertex_Input_Layout_Mapping_Header
)


# ref 8080978C
@binary_struct()
@dataclass
class Client_Bootstrap_Header_D2_EOF:
    file_size: Annotated[int, u64]
    arr_pointer: Vec_Pointer_64  # second element in this array points to render_globals

    def to_unified(self) -> Unified_Client_Bootstrap_Header:
        return Unified_Client_Bootstrap_Header(self.file_size, self.arr_pointer)


@binary_struct()
@dataclass
class Client_Bootstrap_Array_Element_D2_EOF:
    unk_0: Annotated[int, u32]
    unk_4: Annotated[int, u32]
    handle: Wide_Tag_Handle


# ref 8080978C
@binary_struct()
@dataclass
class S_Render_Globals_Header_D2_EOF:
    file_size: Annotated[int, u64]
    array: Vec_Pointer_64 # array where input_layouts_tag is located


# ref 808067A8
# render globals same as in d1

# type 8080870F
@binary_struct()
@dataclass
class Element_8080870F:
    hash: Annotated[int, u32]
    unk_4: Annotated[int, u32]
    wide_hash: Wide_Tag_Handle


# ref 80806D78
@binary_struct()
@dataclass
class S_Vertex_Input_Layouts_D2_EOF:
    file_size: Annotated[int, u64]

    elements_1_tag_handle: Annotated[Tag_Handle, L_Padding(4)]
    elements_2_tag_handle: Tag_Handle

    element_mappings: Annotated[Tag_Handle, L_Padding(28)]  # should be the last tag

    def to_unified(self) -> Unified_S_Vertex_Input_Layouts:
        return Unified_S_Vertex_Input_Layouts(
            self.file_size,
            self.elements_1_tag_handle,
            self.elements_2_tag_handle,
            self.element_mappings
        )


# ref 80806D7F
@binary_struct()
@dataclass
class S_Vertex_Input_Element_Sets_Header_D2_EOF:
    file_size: Annotated[int, u64]
    sets_pointer: Vec_Pointer_64

    def to_unified(self) -> Unified_S_Vertex_Input_Element_Sets_Header:
        return Unified_S_Vertex_Input_Element_Sets_Header(
            self.file_size,
            self.sets_pointer
        )


# type 80806D81
@binary_struct()
@dataclass
class S_Vertex_Input_Element_Set_D2_EOF:
    elements_pointer: Vec_Pointer_64 # points to an array of S_Vertex_Input_Element

    def to_unified(self) -> Unified_S_Vertex_Input_Element_Set_Pointer:
        return Unified_S_Vertex_Input_Element_Set_Pointer(self.elements_pointer)


# ref 80806D7B
@binary_struct()
@dataclass
class S_Vertex_Input_Layout_Mapping_Header_D2_EOF:
    file_size: Annotated[int, u64]
    arr_pointer: Vec_Pointer_64  # to array of S_Vertex_Layout

    def to_unified(self) -> Unified_S_Vertex_Input_Layout_Mapping_Header:
        return Unified_S_Vertex_Input_Layout_Mapping_Header(self.file_size, self.arr_pointer)
