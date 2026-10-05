from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, u64
from libs.tag.tag_pointers import Vec_Pointer_64

from src.tag_readers.s_pattern.unified_structures import Unified_S_Pattern_Header


@binary_struct(size=24)
@dataclass
class S_Pattern_Header_D2_EOF:
	file_size: Annotated[int, u64]
	components_array_pointer: Vec_Pointer_64

	def to_unified(self) -> Unified_S_Pattern_Header:
		return Unified_S_Pattern_Header(
			file_size=self.file_size,
			components_array_pointer=self.components_array_pointer
		)
