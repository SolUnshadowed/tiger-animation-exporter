from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, u32, L_Padding

from libs.tag.tag_pointers import Vec_Pointer_32
from src.tag_readers.s_pattern.unified_structures import Unified_S_Pattern_Header


@binary_struct(size=32)
@dataclass
class S_Pattern_Header_D1_DEVALPHA:
	file_size: Annotated[int, u32]

	components_array_pointer: Annotated[Vec_Pointer_32, L_Padding(20)]

	def to_unified(self) -> Unified_S_Pattern_Header:
		return Unified_S_Pattern_Header(
			file_size=self.file_size,
			components_array_pointer=self.components_array_pointer
		)
