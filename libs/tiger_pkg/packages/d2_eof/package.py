from libs.tiger_pkg.enums import Package_Platform
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.packages.package_common import Package_Named_Tag_Entry, Unified_Hash_Table_Entry
from libs.tiger_pkg.packages.d2_common import Package_Common_D2, Entry_Header, Block_Header, Hash_Table_Entry
from libs.tiger_pkg.packages.d2_eof.structures import Package_Header
from libs.binary_reader import Binary_Reader, s64


class Package_D2_EOF(Package_Common_D2):
	header: Package_Header
	named_tags: list[Package_Named_Tag_Entry]

	def __init__(self, file_path: str):
		file = open(file_path, 'rb')

		reader = Binary_Reader(file)
		header = reader.read_struct(Package_Header, override_endianness=self.endianness)

		reader.seek(header.entry_table_offset)

		entries: list[Entry_Header] = reader.read_struct_array(
			Entry_Header,
			header.entry_table_size,
			override_endianness=self.endianness
		)

		reader.seek(header.named_tag_table_offset + 0x30)
		named_tags: list[Package_Named_Tag_Entry] = reader.read_struct_array(
			Package_Named_Tag_Entry,
			header.named_tag_table_size,
			override_endianness=self.endianness
		)

		reader.seek(header.block_table_offset)
		blocks: list[Block_Header] = reader.read_struct_array(
			Block_Header,
			header.block_table_size,
			override_endianness=self.endianness
		)

		wide_hashes = []

		if header.h64_table_size > 0:
			reader.seek(header.h64_table_offset + 0x10)
			offset = reader.read_type(s64, self.endianness)
			reader.seek(header.h64_table_offset + 0x20 + offset)
			wide_hashes = reader.read_struct_array(Hash_Table_Entry, header.h64_table_size)

		Package_Common_D2.__init__(
			self,
			file_path,
			file,
			reader,
			Game_Version.D2_EOF,
			package_id=header.package_id,
			patch_id=header.patch_id,
			group_id=header.group_id,
			entries=entries,
			blocks=blocks,
			wide_hashes=wide_hashes,
			language=header.language,
		)

		self.header = header
		self.named_tags = named_tags

	@property
	def platform(self) -> Package_Platform:
		return self.header.package_platform

	def get_named_tags(self) -> list[Package_Named_Tag_Entry]:
		return self.named_tags

	def get_hash64_table(self) -> list[Unified_Hash_Table_Entry]:
		return [
			Unified_Hash_Table_Entry(
				handle_64=entry.hash64,
				handle_32=entry.hash32,
				reference=entry.reference,
			)
			for entry in self.wide_hashes
		]
