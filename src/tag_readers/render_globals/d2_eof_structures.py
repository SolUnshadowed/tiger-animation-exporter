from typing import Annotated
from dataclasses import dataclass


from libs.binary_reader import binary_struct, u8, u64, u32, s32, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_64
from libs.tiger_pkg.tag_handle import Tag_Handle, Wide_Tag_Handle

from src.tag_readers.render_globals.unified_structures import (
	Unified_S_Vertex_Input_Element_Sets_Header, Unified_S_Vertex_Input_Element_Set_Pointer,
	Unified_Client_Bootstrap_Header, Unified_Render_Globals_Header, Unified_S_Vertex_Input_Layouts,
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
