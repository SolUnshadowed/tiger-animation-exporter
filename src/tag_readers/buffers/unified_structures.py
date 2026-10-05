from dataclasses import dataclass


@dataclass
class Unified_Vertex_Buffer_Header:
	data_size: int
	stride: int
	vtype: int


@dataclass
class Unified_Index_Buffer_Header:
	is_32bit: bool
	data_size: int
