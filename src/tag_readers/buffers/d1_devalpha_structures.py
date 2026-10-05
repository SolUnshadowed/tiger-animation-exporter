from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, s8, u8, u16, u32, L_Padding

from src.tag_readers.buffers.unified_structures import Unified_Index_Buffer_Header, Unified_Vertex_Buffer_Header

# Buffer header's ref is a handle of Buffer Data
@binary_struct()
@dataclass
class Vertex_Buffer_Header_D1_DEVALPHA:
	data_size: Annotated[int, u32, L_Padding(32)] # 32 bytes of unknown
	vtype: Annotated[int, u16] # type and stride order seems to be reversed compared to d1_roi
	stride: Annotated[int, u16]
	deadbeef: Annotated[int, u32]

	def to_unified(self) -> Unified_Vertex_Buffer_Header:
		return Unified_Vertex_Buffer_Header(
			data_size=self.data_size,
			vtype=self.vtype,
			stride=self.stride,
		)


@binary_struct()
@dataclass
class Index_Buffer_Header_D1_DEVALPHA:
	data_size_0: Annotated[int, u32, L_Padding(28)] # seems to be u32
	unk0: Annotated[int, s8]
	is_32bit: Annotated[bool, u8]  # verified on spider tank
	unk1: Annotated[int, u16]
	data_size_1: Annotated[int, u32]
	deadbeef: Annotated[int, u32]

	def to_unified(self) -> Unified_Index_Buffer_Header:
		return Unified_Index_Buffer_Header(
			is_32bit=self.is_32bit,
			data_size=self.data_size_0,
		)
