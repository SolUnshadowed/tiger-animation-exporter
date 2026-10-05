from dataclasses import dataclass
from libs.tag.tag_pointers import Base_Rel_Pointer


@dataclass
class Unified_S_Pattern_Component_Header:
	file_size: int
	default_instance_pointer: Base_Rel_Pointer
	definition_pointer: Base_Rel_Pointer