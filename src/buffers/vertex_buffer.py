from dataclasses import dataclass

from src.tag_readers.buffers.unified_structures import Unified_Vertex_Buffer_Header
from src.tag_readers.render_globals.read_s_vertex_input_element_sets import S_Vertex_Input_Element_Set


@dataclass
class Vertex_Buffer:
	header: Unified_Vertex_Buffer_Header
	data: bytes
	element_set: S_Vertex_Input_Element_Set
