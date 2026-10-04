from dataclasses import dataclass
from typing import Annotated
from libs.binary_reader import binary_struct, u32, u64


@binary_struct()
@dataclass
class Tag_Handle:
	value: Annotated[int, u32]

	@classmethod
	def new(cls, package_id: int, entry: int):
		return cls(
			0x80800000
			+ (package_id << 13)
			+ (entry % 8192)
		)

	@property
	def is_valid(self) -> bool:
		return 0x80800000 < self.value <= 0x81FFFFFF

	@property
	def is_none(self) -> bool:
		return self.value == 0xFFFFFFFF

	@property
	def package_id(self) -> int:
		return ((self.value - 0x80800000) >> 13) & 0xFFFF

	@property
	def entry_index(self) -> int:
		return self.value & 0x1FFF

	def __int__(self) -> int:
		return self.value

	def __repr__(self) -> str:
		return f"0x{self.value:08X}"


@binary_struct()
@dataclass
class Tag_Handle_64:
	value: Annotated[int, u64]

	def __repr__(self) -> str:
		return f"0x{self.value:016X}"


@binary_struct()
@dataclass
class Wide_Tag_Handle:
	handle_32: Tag_Handle
	is_32_bit: Annotated[bool, u32]
	handle_64: Tag_Handle_64

	def get_value(self) -> Tag_Handle | Tag_Handle_64:
		if self.is_32_bit:
			return self.handle_32
		else:
			return self.handle_64

	def __repr__(self) -> str:
		return self.get_value().__repr__()
