from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, u8, s32, u32, L_Padding
from libs.tiger.shaders.input_layouts import Input_Semantics
from libs.tiger_pkg.tag_handle import Tag_Handle


# dev alpha type: 80800427
# roi type: 808005D7
@binary_struct()
@dataclass
class Client_Bootstrap_Array_Element:
	hash: Annotated[int, u32]
	handle: Tag_Handle


# d1_devalpha type: 808022E1
# d1_roi type: 80801BD7
# d2_eof type: 808022E1
@binary_struct()
@dataclass
class S_Vertex_Input_Element:
	semantic: Annotated[Input_Semantics, u8]
	semantic_index: Annotated[int, u8]
	format: Annotated[int, u8]


# basically a layout for all buffers
# d1_devalpha type: 808022E7
# d1_roi type: 80801A89
@binary_struct(size=28)
@dataclass
class S_Vertex_Layout:
	index: Annotated[int, u8]

	buffer_0_element_set_index: Annotated[int, s32, L_Padding(7)]
	buffer_1_element_set_index: Annotated[int, s32]
	buffer_2_element_set_index: Annotated[int, s32]
	buffer_3_element_set_index: Annotated[int, s32]

	buffer_0_instanced: Annotated[bool, u8]
	buffer_1_instanced: Annotated[bool, u8]
	buffer_2_instanced: Annotated[bool, u8]
	buffer_3_instanced: Annotated[bool, u8]
