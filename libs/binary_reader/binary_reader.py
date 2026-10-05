import io
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Any, Callable, get_args, get_origin, get_type_hints


IGNORED_TYPES = (int, float, str, bytes, bool, list, dict, set, tuple)

def needs_conversion(t: Any) -> bool:
	return (
		isinstance(t, type)
		and t not in IGNORED_TYPES
		and not hasattr(t, "__binary_meta__")
	)

def build_converter(python_type: Any) -> Callable[[Any], Any] | None:
	if get_origin(python_type) is list:
		args = get_args(python_type)
		if args and needs_conversion(args[0]):
			inner = args[0]
			return lambda value: [inner(v) for v in value]
		return None

	if needs_conversion(python_type):
		return lambda value: value if isinstance(value, python_type) else python_type(value)

	return None


class Endianness(str, Enum):
	LE = "<"
	BE = ">"

	def __str__(self):
		return "%s" % self.value

	@property
	def py_name(self) -> str:
		return "little" if self == Endianness.LE else "big"


# field metadata
@dataclass
class Binary_Meta:
	layout: list[Any]
	endianness: Endianness
	size: int
	align: int = 1


# modifiers
class Field_Modifier:
	def apply(self, reader: "Binary_Reader") -> None:
		pass


class L_Padding(Field_Modifier):
	def __init__(self, size: int):
		self.size = size

	def apply(self, reader: "Binary_Reader") -> None:
		reader.read(self.size)


class Seek_From_Start(Field_Modifier):
	def __init__(self, offset: int):
		self.offset = offset

	def apply(self, reader: "Binary_Reader") -> None:
		reader.seek(self.offset)


@dataclass
class Calculated:
	target_field: str
	attribute: str


# base interface
class Binary_Readable:
	@classmethod
	def get_static_size(cls) -> int:
		return getattr(cls, "size", 0)

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> Any:
		raise NotImplementedError

	def get_size(self) -> int:  # for instances
		return getattr(self, "size", 0)


def get_static_size(binary_type: Any) -> int:
	# if class
	if isinstance(binary_type, type):
		if hasattr(binary_type, "__binary_meta__"):
			return binary_type.__binary_meta__.size
		if hasattr(binary_type, "get_static_size"):
			return binary_type.get_static_size()

	# if class instance
	else:
		if hasattr(binary_type, "get_size"):
			return binary_type.get_size()
		if hasattr(binary_type, "__binary_meta__"):
			return binary_type.__binary_meta__.size

	return 0

# datatypes

# primitives (used as classes, not instances)
class S_Int_64(Binary_Readable):
	size = 8

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=True)


class U_Int_64(Binary_Readable):
	size = 8

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=False)


class S_Int_32(Binary_Readable):
	size = 4

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=True)


class U_Int_32(Binary_Readable):
	size = 4

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=False)


class S_Int_16(Binary_Readable):
	size = 2

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=True)


class U_Int_16(Binary_Readable):
	size = 2

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=False)


class U_Int_8(Binary_Readable):
	size = 1

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=False)


class S_Int_8(Binary_Readable):
	size = 1

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> int:
		data = reader.read(cls.size)
		return int.from_bytes(data, byteorder=endianness.py_name, signed=True)


class Float_32(Binary_Readable):
	size = 4

	@classmethod
	def read_from(cls, reader: "Binary_Reader", endianness: Endianness) -> float:
		data = reader.read(cls.size)
		return struct.unpack(f"{endianness.value}f", data)[0]


# aliases
u8 = U_Int_8
u16 = U_Int_16
u32 = U_Int_32
u64 = U_Int_64

s8 = S_Int_8
s16 = S_Int_16
s32 = S_Int_32
s64 = S_Int_64

f32 = Float_32

# Complex types (used as class instances)
class Array(Binary_Readable):
	def __init__(self, element_binary_type: Any, element_count: int):
		self.element_binary_type = element_binary_type
		self.element_count = element_count

	def get_size(self) -> int:
		return get_static_size(self.element_binary_type) * self.element_count

	def read_from(self, reader: "Binary_Reader", endianness: Endianness) -> list[Any]:
		return [reader.read_type(self.element_binary_type, endianness) for _ in range(self.element_count)]


class Tuple(Binary_Readable):
	def __init__(self, *element_binary_types: Any):
		self.element_binary_types = element_binary_types

	@classmethod
	def repeat(cls, element_binary_type: Any, count: int) -> "Tuple":  # like an array
		return cls(*(element_binary_type,) * count)

	def get_size(self) -> int:
		return sum(get_static_size(t) for t in self.element_binary_types)

	def read_from(self, reader: "Binary_Reader", endianness: Endianness) -> tuple[Any, ...]:
		return tuple(
			reader.read_type(binary_type, endianness)
			for binary_type in self.element_binary_types
		)


class Fixed_String(Binary_Readable):
	def __init__(self, size: int):
		self.size = size

	def get_size(self) -> int:
		return self.size

	def read_from(self, reader: "Binary_Reader", endianness: Endianness) -> str:
		return reader.read(self.size).rstrip(b"\0").decode("utf-8", errors="replace")


# layout fields

@dataclass
class Layout_Field:
	name: str
	binary_type: Any
	modifiers: list[Any]
	python_type: type
	endianness: Endianness | None = None
	pre_read: tuple[Field_Modifier, ...] = ()
	converter: Callable[[Any], Any] | None = None


@dataclass
class Layout_Field_Calculated:
	name: str
	target_field: str
	attribute: str
	python_type: type


# structure decorator
def binary_struct[T](
	*, endianness: Endianness = Endianness.BE, size=None, align: int = 1
) -> Callable[[type[T]], type[T]]:

	def decorator(cls: type[T]) -> type[T]:
		# methods to inject into decorated class
		@classmethod
		def _struct_read_from(cls_struct, reader: "Binary_Reader", field_endian: Endianness) -> T:
			return reader.read_struct(cls_struct, override_endianness=field_endian)

		@classmethod
		def _struct_get_static_size(cls_struct) -> int:
			return cls_struct.__binary_meta__.size

		# inject methods
		cls.read_from = _struct_read_from
		cls.get_static_size = _struct_get_static_size

		layout = []
		calculated_size = 0

		for name, annotation in get_type_hints(cls, include_extras=True).items():
			python_type, metadata = (
				(get_args(annotation)[0], get_args(annotation)[1:])
				if get_origin(annotation) is Annotated
				else (annotation, [])
			)

			binary_type = None
			calc_modifier = None
			modifiers: list[Any] = []

			for meta in metadata:  # parse metadata
				is_binary_type = hasattr(meta, "read_from")
				if is_binary_type:  # if type
					binary_type = meta
				elif isinstance(meta, Calculated):  # calculated modifier
					calc_modifier = meta
				elif isinstance(meta, Endianness):  # endianness modifier
					modifiers.append(meta)
				elif isinstance(meta, Field_Modifier):  # other modifiers
					modifiers.append(meta)

			if calc_modifier:  # calculated fields are not read
				layout.append(
					Layout_Field_Calculated(
						name=name,
						target_field=calc_modifier.target_field,
						attribute=calc_modifier.attribute,
						python_type=python_type
					)
				)
				continue

			for modifier in modifiers:
				if isinstance(modifier, L_Padding):  # padding adds to size
					calculated_size += modifier.size
				elif isinstance(modifier, Seek_From_Start):  # check for negative
					if modifier.offset < calculated_size:
						raise ValueError("Seek From Start points backwards.")
					calculated_size = modifier.offset

			if not binary_type:
				is_binary_struct = (
					hasattr(python_type, "__binary_meta__") or
					(isinstance(python_type, type) and hasattr(python_type, "read_from"))
					# isinstance(python_type, type) checks if it is a class, hasattr(python_type, "read_from") if it is class instance
				)
				if is_binary_struct:  # structures are both python type and binary type
					binary_type = python_type

			if binary_type:
				layout.append(
					Layout_Field(
						name=name,
						binary_type=binary_type,
						modifiers=modifiers,
						python_type=python_type,
						endianness=next((m for m in modifiers if isinstance(m, Endianness)), None),
						pre_read=tuple(m for m in modifiers if isinstance(m, Field_Modifier)),
						converter=build_converter(python_type),
					)
				)
				calculated_size += get_static_size(binary_type)
			else:  # if neither python base type + annotation nor structure -> error
				raise RuntimeError(f"Field {name} is neither binary structure, nor Binary_Readable")

		if align > 1:
			remainder = calculated_size % align
			if remainder != 0:
				calculated_size += align - remainder

		if size is not None and calculated_size != size:
			raise ValueError(f"Expected size: {size}, got: {calculated_size}")

		# save layout to internal field
		cls.__binary_meta__ = Binary_Meta(
			layout=layout,
			endianness=endianness,
			size=calculated_size,
			align=align
		)
		return cls

	return decorator

# reader
class Binary_Reader:
	def __init__(self, source: bytes | bytearray | io.IOBase):
		self.stream = io.BytesIO(source) if isinstance(source, (bytes, bytearray)) else source

	# reads bytes
	def read(self, size: int, offset: int | None = None, whence: int = 0) -> bytes:
		if offset is not None:
			self.seek(offset, whence)

		data = self.stream.read(size)
		if len(data) != size:
			raise EOFError("Unexpected end of stream")
		return data

	# just wrappers
	def seek(self, offset: int, whence: int = 0) -> None:
		self.stream.seek(offset, whence)

	def tell(self):
		return self.stream.tell()

	def read_type(self, target: Any, endianness: Endianness) -> Any:
		return target.read_from(self, endianness)

	def read_struct[T](
		self,
		cls: type[T],
		override_endianness: Endianness | None = None,
		offset: int | None = None,
		whence: int = 0
	) -> T:
		if offset is not None:  # seek
			self.seek(offset, whence)

		start_offset = self.stream.tell()  # structure address in stream
		result = {}
		field_offsets = {}
		calculated_fields = []
		meta: Binary_Meta = cls.__binary_meta__

		struct_endian = override_endianness or meta.endianness

		for entry in meta.layout:
			if isinstance(entry, Layout_Field_Calculated):  # deferring calculated fields
				calculated_fields.append(entry)
				continue

			for modifier in entry.pre_read:  # Padding, Seek_From_Start - just read bytes
				modifier.apply(self)

			# field address in stream
			field_offsets[entry.name] = self.stream.tell()

			# read type
			value = entry.binary_type.read_from(self, entry.endianness or struct_endian)

			# convert to python type
			if entry.converter is not None:
				value = entry.converter(value)

			result[entry.name] = value

		# after the whole structure is read, fill calculated fields
		for calc in calculated_fields:
			if calc.attribute == "address":  # using saved field_offset find address in stream
				val = field_offsets.get(calc.target_field, 0)
			else:
				raise NotImplementedError(f"Attribute {calc.attribute} is not supported yet")

			result[calc.name] = calc.python_type(val)

		# align
		if meta.align > 1:
			end_offset = start_offset + meta.size
			current = self.stream.tell()
			if current < end_offset:
				self.read(end_offset - current)
			elif current > end_offset:
				raise ValueError(
					f"Struct {cls.__name__} read past its aligned size "
					f"({current - start_offset} > {meta.size})"
				)

		return cls(**result)

	def read_struct_array[T](
		self,
		cls: type[T],
		count: int,
		override_endianness: Endianness | str | None = None,
		offset: int | None = None,
		whence: int = 0,
	) -> list[T]:
		if offset is not None:
			self.seek(offset, whence)

		return [self.read_struct(cls, override_endianness=override_endianness) for _ in range(count)]
