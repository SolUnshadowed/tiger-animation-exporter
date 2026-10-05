from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, u64, L_Padding
from libs.tag.tag_pointers import Rel_Pointer_64
from src.tag_readers.s_pattern_component.unified_structures import Unified_S_Pattern_Component_Header


@binary_struct(size=32)
@dataclass
class S_Pattern_Component_Header_D1_ROI:
	file_size: Annotated[int, u64]
	rel_pointer_0: Rel_Pointer_64
	default_instance_pointer: Rel_Pointer_64
	definition_pointer: Rel_Pointer_64

	def to_unified(self) -> Unified_S_Pattern_Component_Header:
		return Unified_S_Pattern_Component_Header(
			file_size=self.file_size,
			default_instance_pointer=self.default_instance_pointer,
			definition_pointer=self.definition_pointer,
		)
