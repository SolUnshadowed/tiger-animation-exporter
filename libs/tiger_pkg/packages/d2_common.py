from typing import Annotated
from dataclasses import dataclass
from typing import BinaryIO

from libs.binary_reader import binary_struct, Array, u8, u16, u32, u64, Endianness, Binary_Reader
from libs.tiger_pkg import oodle
from libs.tiger_pkg.tag_handle import Tag_Handle, Tag_Handle_64
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.enums import Package_Language
from libs.tiger_pkg.packages.package_common import Unified_Entry_Header, Package
from libs.tiger_pkg.packages.block_flags import Block_Flags
from libs.tiger_pkg.packages.crypto import Package_GCM
from libs.tiger_pkg.packages.block_cache import Block_Cache


@binary_struct()
@dataclass
class Entry_Header:
	reference: Annotated[int, u32]
	_type_info: Annotated[int, u32]
	_block_info: Annotated[int, u64]

	@property
	def file_type(self) -> int:
		return (self._type_info >> 9) & 0x7F  # to u8

	@property
	def file_subtype(self) -> int:
		return (self._type_info >> 6) & 0x7  # to u8

	@property
	def starting_block(self) -> int:
		return self._block_info & 0x3FFF

	@property
	def starting_block_offset(self) -> int:
		return ((self._block_info >> 14) & 0x3FFF) << 4

	@property
	def file_size(self) -> int:
		return (self._block_info >> 28) & 0xFFffFFff


@binary_struct(size=48)
@dataclass
class Block_Header:
	offset: Annotated[int, u32]
	size: Annotated[int, u32]
	patch_id: Annotated[int, u16]
	flags: Annotated[Block_Flags, u16]
	hash: Annotated[list[int], Array(u8, 20)]
	gcm_tag: Annotated[list[int], Array(u8, 16)]


@binary_struct(size=16)
@dataclass
class Hash_Table_Entry:
	handle_64: Tag_Handle_64
	handle_32: Tag_Handle
	reference: Tag_Handle


class Package_Common_D2(Package):
	file: BinaryIO
	reader: Binary_Reader
	version: "Game_Version"
	_package_id: int
	_patch_id: int
	language: Package_Language

	gcm: Package_GCM
	unified_entries: list[Unified_Entry_Header]
	blocks: list[Block_Header]
	wide_hashes: list[Hash_Table_Entry]

	file_path_base: str
	block_cache: Block_Cache

	def __init__(
		self,
		file_path: str,
		file: BinaryIO,
		reader: Binary_Reader,
		version: "Game_Version",
		package_id: int,
		patch_id: int,
		group_id: int,
		entries: list[Entry_Header],
		blocks: list[Block_Header],
		wide_hashes: list[Hash_Table_Entry],
		language: Package_Language,
	):
		super().__init__()

		self.file = file
		self.reader = reader
		self.version = version
		self._package_id = package_id
		self._patch_id = patch_id
		self.language = language
		self.blocks = blocks
		self.wide_hashes = wide_hashes

		self.file_path_base = file_path[:file_path.rfind("_")]

		self.unified_entries = [
			Unified_Entry_Header(
				reference=entry.reference,
				file_type=entry.file_type,
				file_subtype=entry.file_subtype,
				starting_block=entry.starting_block,
				starting_block_offset=entry.starting_block_offset,
				file_size=entry.file_size
			)
			for entry in entries
		]

		self.gcm = Package_GCM(self.version, self.package_id, group_id)

		self.block_cache = Block_Cache()

	@property
	def endianness(self) -> Endianness:
		return Endianness.LE

	def get_raw_block(self, block_index: int) -> bytes:
		block_header = self.blocks[block_index]

		if self._patch_id == block_header.patch_id:
			return self.reader.read(block_header.size, block_header.offset)
		else:
			file_path = f"{self.file_path_base}_{block_header.patch_id}.pkg"

			with open(file_path, 'rb') as file:
				reader = Binary_Reader(file)

				return reader.read(block_header.size, block_header.offset)

	def read_block(self, block_index: int) -> bytes:
		block_header = self.blocks[block_index]

		block_data = self.get_raw_block(block_index)

		if Block_Flags.ENCRYPTED in block_header.flags:
			block_data = self.gcm.decrypt_block(block_header.flags, bytes(block_header.gcm_tag), block_data)

		if Block_Flags.COMPRESSED in block_header.flags:
			match self.version:
				case Game_Version.D1_DEV_ALPHA | Game_Version.D1_ROI:
					return oodle.decompress_3(block_data)
				case Game_Version.D2_EOF | Game_Version.MARATHON:
					return oodle.decompress_9(block_data)
		else:
			return block_data

	def get_block(self, index: int) -> bytes:
		return self.block_cache.get(index, self.read_block)

	def get_entry(self, entry_index: int) -> Unified_Entry_Header:
		return self.unified_entries[entry_index]

	def get_entries(self) -> list[Unified_Entry_Header]:
		return self.unified_entries

	@property
	def package_id(self):
		return self._package_id

	@property
	def patch_id(self):
		return self._patch_id

	def close(self) -> None:
		self.file.close()