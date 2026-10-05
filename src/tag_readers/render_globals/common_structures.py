from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, u8, s32, u32, L_Padding
from libs.tiger.shaders.input_layouts import Input_Semantics
from libs.tiger_pkg.tag_handle import Tag_Handle


'''
common have the same layouts for all games, while unified serve as type annotation erasure
'''


'''
dev 8091C000
roi 80AF2000

	SRenderGlobals
	dev 8091C002
	roi 80AF2001 
	
		SVertexInputLayouts	
		dev 8091C005
		roi 80AF2004
		
			SVertexInputElementSets  
			dev 8091C008 ref 808022E6
			roi 80AF2007
			
				SVertexInputElementSet: array types: dev: 808022E4, roi: 80801A98
				elements are basically vec_pointer to arrays of S_Vertex_Input_Element
'''


# dev alpha type: 80800427
# roi type: 808005D7
@binary_struct()
@dataclass
class Client_Bootstrap_Array_Element:
	hash: Annotated[int, u32]
	handle: Tag_Handle


# d1_devalpha ref: 808022E1
# d1_roi ref: 80801BD7
@binary_struct()
@dataclass
class S_Vertex_Input_Element:
	semantic: Annotated[Input_Semantics, u8]
	semantic_index: Annotated[int, u8]
	format: Annotated[int, u8]


# basically a layout for each buffer
# d1_devalpha ref: 808022E7
# d1_roi ref: 80801A89
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
