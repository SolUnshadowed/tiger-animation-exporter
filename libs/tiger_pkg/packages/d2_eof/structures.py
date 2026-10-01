from dataclasses import dataclass
from libs.tiger_pkg.enums import Package_Platform, Package_Language
from typing import Annotated

from libs.binary_reader import (
	binary_struct, u8, u16, u32, u64, Seek_From_Start
)


@binary_struct(size=292)
@dataclass
class Package_Header:
	version: Annotated[int, u16]
	package_platform: Annotated[Package_Platform, u16]

	group_id: Annotated[int, u64, Seek_From_Start(0x8)]

	package_id: Annotated[int, u16, Seek_From_Start(0x10)]

	is_unpatchable: Annotated[bool, u8]

	build_time: Annotated[int, u64, Seek_From_Start(0x20)]

	patch_id: Annotated[int, u16, Seek_From_Start(0x30)]
	language: Annotated[Package_Language, u16]

	header_signature_offset: Annotated[int, u32, Seek_From_Start(0x40)]

	entry_table_size: Annotated[int, u32, Seek_From_Start(0x60)]
	entry_table_offset: Annotated[int, u32]
	block_table_size: Annotated[int, u32]
	block_table_offset: Annotated[int, u32]

	named_tag_table_size: Annotated[int, u32, Seek_From_Start(0x78)]
	named_tag_table_offset: Annotated[int, u32]

	h64_table_size: Annotated[int, u32, Seek_From_Start(0xB8)]
	h64_table_offset: Annotated[int, u32]

	file_size: Annotated[int, u32, Seek_From_Start(0x120)]
