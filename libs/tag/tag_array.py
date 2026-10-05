import logging
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from typing import Iterator, Any, Annotated, Literal

from libs.binary_reader import (
	binary_struct,
	s8, u8, s16, u16, u32, s32, s64, u64, f32,
	Endianness, Binary_Reader
)
from .tag_pointers import Base_Tag_Pointer


logger = logging.getLogger(__name__)

@dataclass
class Type_Record:
	bin_type: Any
	np_type: npt.DTypeLike


@binary_struct(align=16)
@dataclass
class Tag_Array_32_Header:
	length: Annotated[int, u32]
	type: Annotated[int, u32]


@binary_struct(align=16)
@dataclass
class Tag_Array_64_Header:
	length: Annotated[int, u64]
	type: Annotated[int, u64]


# primitive types
auto_types = {
	# 0x80800004: Type_Record(bool, np.bool)
	0x80800005: Type_Record(s8, np.int8),
	0x80800006: Type_Record(s16, np.int16), # array 7, compressed/uncompressed data
	0x80800007: Type_Record(s32, np.int32),  # array 7
	0x80800008: Type_Record(s64, np.int64),
	0x80800009: Type_Record(u8, np.uint32),  # keyframe deltas and interp data
	0x8080000A: Type_Record(u16, np.uint16), # control maps
	0x8080000B: Type_Record(u32, np.uint32),
	0x8080000C: Type_Record(u64, np.uint64),
	0x8080000F: Type_Record(f32, np.float32), # floats
	# additional
	0x80800047: Type_Record(s16, np.int16), # array 7, compressed/uncompressed data | dev alpha
}


class Tag_Array[T]:
	length: int
	type: int
	payload: list[T]
	payload_start: int

	def __init__(
		self,
		reader: "Binary_Reader",
		pointer: "Base_Tag_Pointer",
		element_type: Any,
		endianness: Endianness,
		bitness: Literal[32, 64] = 32
	):
		address = pointer.get_address()
		reader.seek(address)

		header_class = Tag_Array_32_Header if bitness == 32 else Tag_Array_64_Header
		header = reader.read_struct(header_class, endianness)

		self.length = header.length
		self.type = header.type
		self.payload = []

		if self.length > 0:
			self.payload_start = reader.stream.tell()

			if element_type is not None:
				self.payload = [
					reader.read_type(element_type, endianness)
					for _ in range(self.length)
				]
			elif self.type in auto_types:
				self.payload = [
					reader.read_type(auto_types[self.type].bin_type, endianness)
					for _ in range(self.length)
				]
			else:
				raise ValueError(f"BIN: No auto type for {hex(self.type)}")
		else:
			logger.info(f"Empty array at: {hex(address)}")

	def __str__(self) -> str:
		return f"length: {self.length}, type: {hex(self.type)}"

	def read_vec(self, offset: int, amount: int) -> tuple[list[T], int]:
		new_offset = offset + amount
		return self.payload[offset: new_offset], new_offset

	def read_single(self, offset: int) -> T:
		return self.payload[offset]

	def __getitem__(self, index: int) -> T:
		return self.payload[index]

	def __iter__(self) -> Iterator[T]:
		return iter(self.payload)

	def __len__(self) -> int:
		return self.length


class Tag_Array_NP:
	length: int
	type: int
	data: npt.NDArray[Any]
	payload_start: int

	def __init__(
		self,
		reader: "Binary_Reader",
		pointer: "Base_Tag_Pointer",
		dtype: npt.DTypeLike | None,
		endianness: Endianness,
		inner_size: int = 1,
		bitness: Literal[32, 64] = 32
	):
		address = pointer.get_address()
		reader.seek(address)

		header_class = Tag_Array_32_Header if bitness == 32 else Tag_Array_64_Header
		header = reader.read_struct(header_class, endianness)

		self.length = header.length
		self.type = header.type

		if self.length > 0:
			self.payload_start = reader.tell()

			if dtype is None and self.type in auto_types:
				dtype = auto_types[self.type].np_type
			elif dtype is None and self.type not in auto_types:
				raise ValueError(f"NP: No auto type for {hex(self.type)}")

			byte_order = "<" if endianness == Endianness.LE else ">"
			base_dtype = np.dtype(dtype).newbyteorder(byte_order)

			total_scalars = self.length * inner_size
			bytes_to_read = total_scalars * base_dtype.itemsize

			raw_bytes = reader.read(bytes_to_read)

			if len(raw_bytes) != bytes_to_read:
				raise EOFError(f"Unexpected end of stream: expected {bytes_to_read} bytes, got {len(raw_bytes)}")

			raw_data = np.frombuffer(raw_bytes, dtype=base_dtype).copy()

			if inner_size > 1:
				self.data = raw_data.reshape((self.length, inner_size))
			else:
				self.data = raw_data
		else:
			self.data = np.array([], dtype=dtype)
			if inner_size > 1:
				self.data = self.data.reshape((0, inner_size))

			logger.info(f"Empty array at: {hex(address)}")

	def read_vec(self, offset: int, amount: int) -> tuple[np.ndarray, int]:
		new_offset = int(offset) + amount
		return self.data[offset: new_offset], new_offset

	def read_scalar(self, offset: int) -> tuple[Any, int]:
		return self.data[offset], offset + 1

	def __len__(self) -> int:
		return self.length

	def __getitem__(self, index: int) -> Any:
		return self.data[index]

	def __iter__(self) -> Iterator[Any]:
		return iter(self.data)
