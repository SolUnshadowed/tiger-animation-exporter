from typing import BinaryIO

from libs.binary_reader import Binary_Reader, Endianness

from libs.tiger_pkg import oodle
from libs.tiger_pkg.enums import Package_Platform
from libs.tiger_pkg.packages.package_common import Unified_Entry_Header, Package, Package_Named_Tag_Entry, Unified_Hash_Table_Entry
from libs.tiger_pkg.packages.d1_roi.structures import Package_Header, Block_Header, Entry_Header, Named_Tag_Entry_D1
from libs.tiger_pkg.packages.block_cache import Block_Cache


class Package_D1_ROI(Package):
	file: BinaryIO
	reader: Binary_Reader
	file_path_base: str = ""
	header: Package_Header

	unified_entries: list[Unified_Entry_Header]
	blocks: list[Block_Header]

	named_tags: list[Package_Named_Tag_Entry]

	block_cache: Block_Cache

	def __init__(self, file_path: str):
		super().__init__()
		self.file_path = file_path
		self.file = open(file_path, 'rb')

		self.reader = Binary_Reader(self.file)

		self.header = self.reader.read_struct(Package_Header, override_endianness=self.endianness)

		self.reader.seek(self.header.entry_table_offset)
		entries: list[Entry_Header] = self.reader.read_struct_array(
			Entry_Header,
			self.header.entry_table_size,
			override_endianness=self.endianness
		)

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

		self.reader.seek(self.header.named_tag_table_offset)
		named_tags: list[Named_Tag_Entry_D1] = self.reader.read_struct_array(
			Named_Tag_Entry_D1,
			self.header.named_tag_table_size,
			override_endianness=self.endianness
		)

		self.named_tags = [
			Package_Named_Tag_Entry(
				handle=entry_d1.handle,
				class_hash=entry_d1.class_hash,
				name=bytes(entry_d1.name).rstrip(b"\0").decode("utf-8", errors="replace")
			)
			for entry_d1 in named_tags
		]

		self.reader.seek(self.header.block_table_offset)
		self.blocks: list[Block_Header] = self.reader.read_struct_array(
			Block_Header,
			self.header.block_table_size,
			override_endianness=self.endianness
		)

		self.file_path_base = file_path[:file_path.rfind("_")]

		self.block_cache = Block_Cache()


	def get_entry(self, entry_index: int) -> Unified_Entry_Header:
		return self.unified_entries[entry_index]

	def get_entries(self) -> list[Unified_Entry_Header]:
		return self.unified_entries

	def get_raw_block(self, block_index: int) -> bytes:
		block_header = self.blocks[block_index]

		if self.header.patch_id == block_header.patch_id:
			return self.reader.read(block_header.size, block_header.offset)
		else:
			file_path = f"{self.file_path_base}_{block_header.patch_id}.pkg"

			with open(file_path, 'rb') as file:
				reader = Binary_Reader(file)

				return reader.read(block_header.size, block_header.offset)

	def read_block(self, block_index: int) -> bytes:
		block_header = self.blocks[block_index]

		raw = self.get_raw_block(block_index)

		if block_header.flags & 0x1 != 0:
			return oodle.decompress_3(raw)
		else:
			return raw

	def get_block(self, index: int) -> bytes:
		return self.block_cache.get(index, self.read_block)

	def get_named_tags(self) -> list[Package_Named_Tag_Entry]:
		return self.named_tags

	def get_handle_64_table(self) -> list[Unified_Hash_Table_Entry]:
		return []

	@property
	def package_id(self) -> int:
		return self.header.pkg_id

	@property
	def patch_id(self) -> int:
		return 0

	@property
	def endianness(self) -> Endianness:
		return Endianness.LE

	@property
	def platform(self) -> Package_Platform:
		return self.header.package_platform

	def close(self) -> None:
		self.file.close()
