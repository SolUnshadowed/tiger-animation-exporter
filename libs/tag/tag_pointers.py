import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, Calculated, u32, u64

logger = logging.getLogger(__name__)


class Base_Tag_Pointer(ABC):
	@abstractmethod
	def get_address(self) -> int:
		pass

	@abstractmethod
	def is_zero(self) -> bool:
		pass


class Base_Rel_Pointer(Base_Tag_Pointer):
	pass


class Base_Vec_Pointer(Base_Tag_Pointer):
	@abstractmethod
	def get_length(self) -> int:
		pass


@binary_struct()
@dataclass
class Rel_Pointer_32(Base_Rel_Pointer):
	offset: Annotated[int, u32]
	offset_address: Annotated[int, Calculated(target_field="offset", attribute="address")]

	def get_address(self) -> int:
		return self.offset_address + self.offset

	def is_zero(self) -> bool:
		return self.offset == 0

	def __str__(self) -> str:
		return f"offset: {self.offset} [{hex(self.offset)}], points to: {hex(self.get_address())}"


@binary_struct()
@dataclass
class Rel_Pointer_64(Base_Rel_Pointer):
	offset: Annotated[int, u64]
	offset_address: Annotated[int, Calculated(target_field="offset", attribute="address")]

	def get_address(self) -> int:
		return self.offset_address + self.offset

	def is_zero(self) -> bool:
		return self.offset == 0

	def __str__(self) -> str:
		return f"offset: {self.offset} [{hex(self.offset)}], points to: {hex(self.get_address())}"


@binary_struct()
@dataclass
class Vec_Pointer_32(Base_Vec_Pointer):
	length: Annotated[int, u32]
	length_address: Annotated[int, Calculated(target_field="length", attribute="address")]
	offset: Annotated[int, u32]
	offset_address: Annotated[int, Calculated(target_field="offset", attribute="address")]

	def get_address(self) -> int:
		return self.offset_address + self.offset

	def get_length(self) -> int:
		return self.length

	def is_zero(self) -> bool:
		return self.offset == 0

	def __str__(self) -> str:
		return f"address: {self.length_address} [{hex(self.length_address)}], length: {self.length} [{hex(self.length)}], offset: {self.offset} [{hex(self.offset)}], points to: {hex(self.get_address())}"


@binary_struct()
@dataclass
class Vec_Pointer_64(Base_Vec_Pointer):
	length: Annotated[int, u64]
	length_address: Annotated[int, Calculated(target_field="length", attribute="address")]
	offset: Annotated[int, u64]
	offset_address: Annotated[int, Calculated(target_field="offset", attribute="address")]

	def get_address(self) -> int:
		return self.offset_address + self.offset

	def get_length(self) -> int:
		return self.length

	def is_zero(self) -> bool:
		return self.offset == 0

	def __str__(self) -> str:
		return f"address: {self.length_address} [{hex(self.length_address)}], length: {self.length} [{hex(self.length)}], offset: {self.offset} [{hex(self.offset)}], points to: {hex(self.get_address())}"
