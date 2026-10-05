from dataclasses import dataclass
from libs.tag.tag_pointers import Base_Vec_Pointer


@dataclass
class Unified_S_Pattern_Header:
	file_size: int
	components_array_pointer: Base_Vec_Pointer