from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Annotated

from libs.binary_reader import Endianness, binary_struct, Binary_Readable, u64, u32
from libs.tiger_pkg.tag_handle import Tag_Handle, Tag_Handle_64
from libs.tiger_pkg.packages import exceptions as err
from libs.tiger_pkg.enums import Package_Platform


# reads u8 offset and jumps at position
# reads C-string and returns back
class C_String_At_Offset(Binary_Readable):

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> str:
		# save position
		start_of_field = reader.stream.tell()
		# read offset
		offset = reader.read_type(u64, endianness)
		# save checkpoint
		pos_save = reader.stream.tell()
		# jump
		reader.seek(start_of_field + offset)
		# read C-string
		buffer = bytearray()
		while (char := reader.read(1)) != b"\0":
			buffer.extend(char)

		# return back
		reader.seek(pos_save)

		return buffer.decode("utf-8", errors="replace")


@dataclass(slots=True)
class Unified_Entry_Header:
	reference: int
	file_type: int
	file_subtype: int
	starting_block: int
	starting_block_offset: int
	file_size: int


@dataclass(slots=True)
class Unified_Hash_Table_Entry:
	handle_64: Tag_Handle_64
	handle_32: Tag_Handle
	reference: Tag_Handle


@binary_struct()
@dataclass(slots=True)
class Package_Named_Tag_Entry:
	handle: Tag_Handle
	class_hash: Annotated[int, u32]
	name: Annotated[str, C_String_At_Offset]


class Package(ABC):
	@abstractmethod
	def close(self) -> None:
		pass

	@property
	@abstractmethod
	def endianness(self) -> Endianness:
		pass

	@property
	@abstractmethod
	def package_id(self) -> int:
		pass

	@property
	@abstractmethod
	def patch_id(self) -> int:
		pass

	@property
	@abstractmethod
	def platform(self) -> Package_Platform:
		pass

	@abstractmethod
	def get_entry(self, index: int) -> Unified_Entry_Header:
		pass

	@abstractmethod
	def get_entries(self) -> list[Unified_Entry_Header]:
		pass

	@abstractmethod
	def read_block(self, index: int) -> bytes:
		pass

	@abstractmethod
	def get_block(self, index: int) -> bytes:
		pass

	@abstractmethod
	def get_hash64_table(self) -> list[Unified_Hash_Table_Entry]:
		pass

	@abstractmethod
	def get_named_tags(self)-> list[Package_Named_Tag_Entry]:
		pass

	def read_tag(self, tag: Tag_Handle) -> bytes:
		if tag.package_id != self.package_id:
			raise err.Tag_Handle_Mismatch_Error(f"Tag [{tag.package_id}] and package [{self.package_id}] ids mismatch")

		return self.read_entry(tag.entry_index)

	def read_entry(self, entry_index: int) -> bytes:
		entry_header = self.get_entry(entry_index)

		buffer = bytearray()
		current_offset = 0
		current_block = entry_header.starting_block

		while current_offset < entry_header.file_size:
			remaining_bytes = entry_header.file_size - current_offset
			block_data = self.get_block(current_block)

			block_view = memoryview(block_data)
			if current_block == entry_header.starting_block:
				block_start_offset = entry_header.starting_block_offset
				block_remaining = len(block_data) - block_start_offset
				copy_size = block_remaining if block_remaining < remaining_bytes else remaining_bytes

				buffer.extend(block_view[block_start_offset: block_start_offset + copy_size])

				current_offset += copy_size

			elif remaining_bytes < len(block_data):
				# Original comment: If the block has more bytes than we need, it means we're on the last block
				buffer.extend(block_view[:remaining_bytes])
				current_offset += remaining_bytes
			else:
				# Original comment: If the previous 2 conditions failed, it means this whole block belongs to the file
				buffer.extend(block_view)
				current_offset += len(block_data)

			current_block += 1

		return bytes(buffer)

	def get_all_by_reference(self, reference: int) -> list[tuple[int, Unified_Entry_Header]]:
		return [
			(index, header)
			for index, header in enumerate(self.get_entries())
			if header.reference == reference
		]
