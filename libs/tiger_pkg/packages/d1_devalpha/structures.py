from dataclasses import dataclass
from libs.tiger_pkg.enums import Package_Platform, Package_Language
from typing import Annotated

from libs.binary_reader import (
	L_Padding, Array, binary_struct, Fixed_String, u8, u16, u32, u64
)


@binary_struct(size=312)
@dataclass
class Package_Header:
	version: Annotated[int, u16]
	package_platform: Annotated[Package_Platform, u16]
	pkg_id: Annotated[int, u16]
	patch: Annotated[int, u16]
	unk_8: Annotated[int, u64]
	build_time: Annotated[int, u64]
	unk_build_id: Annotated[int, u32]
	unk_1C: Annotated[int, u16]
	package_language: Annotated[Package_Language, u16]
	tool_string : Annotated[str, Fixed_String(128)]

	entry2_table_size: Annotated[int, u32, L_Padding(4)]
	entry2_table_offset: Annotated[int, u32]
	named_tag_table_size: Annotated[int, u32]
	named_tag_table_offset: Annotated[int, u32]
	entry2_table_hash: Annotated[list[int], Array(u8, 20)]

	entry_table_size: Annotated[int, u32, L_Padding(56)]
	entry_table_offset: Annotated[int, u32]
	entry_table_hash: Annotated[list[int], Array(u8, 20)]
	block_table_size: Annotated[int, u32]
	block_table_offset: Annotated[int, u32]
	block_table_hash: Annotated[list[int], Array(u8, 20)]


@binary_struct(size=16)
@dataclass
class Entry_Header:
	reference: Annotated[int, u32]
	thing: Annotated[int, u32]
	block_info: Annotated[int, u64]

	@property
	def file_type(self) -> int:
		return (self.thing >> 18) & 0xFF  # to u8

	@property
	def file_subtype(self) -> int:
		return (self.thing & 0xff) & 0xFF  # to u8

	@property
	def starting_block(self) -> int:
		return self.block_info & 0x3FFF

	@property
	def starting_block_offset(self) -> int:
		return ((self.block_info >> 14) & 0x3FFF) << 4

	@property
	def file_size(self) -> int:
		return (self.block_info >> 28) & 0x3FFFFFFF


@binary_struct(size=32)
@dataclass
class Block_Header:
	offset: Annotated[int, u32]
	size: Annotated[int, u32]
	flags: Annotated[int, u16]
	patch_id: Annotated[int, u16]
	hash: Annotated[list[int], Array(u8, 20)]
