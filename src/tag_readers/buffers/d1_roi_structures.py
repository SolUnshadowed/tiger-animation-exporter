from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, s8, u8, u16, u32, u64

from src.tag_readers.buffers.unified_structures import Unified_Index_Buffer_Header, Unified_Vertex_Buffer_Header


@binary_struct(size=12)
@dataclass
class Vertex_Buffer_Header_D1_ROI:
	data_size: Annotated[int, u32]
	stride: Annotated[int, u16]
	vtype: Annotated[int, u16]
	deadbeef: Annotated[int, u32]

	def to_unified(self) -> Unified_Vertex_Buffer_Header:
		return Unified_Vertex_Buffer_Header(
			data_size=self.data_size,
			vtype=self.vtype,
			stride=self.stride,
		)


@binary_struct()
@dataclass
class Index_Buffer_Header_D1_ROI:
	unk0: Annotated[int, s8]
	is_32bit: Annotated[bool, u8]
	unk1: Annotated[int, u16]
	zero: Annotated[int, u32]
	data_size: Annotated[int, u64]
	deadbeef: Annotated[int, u32]

	def to_unified(self) -> Unified_Index_Buffer_Header:
		return Unified_Index_Buffer_Header(
			is_32bit=self.is_32bit,
			data_size=self.data_size,
		)