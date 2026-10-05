import numpy as np
from dataclasses import dataclass

from libs.tiger.common import Primitive_Type
from libs.binary_reader import Endianness

from src.tag_readers.buffers.unified_structures import Unified_Index_Buffer_Header


# Triangle winding order
EVEN_ORDER = (0, 1, 2)
ODD_ORDER = (1, 0, 2)
SEPARATOR = 0xFFFF


def calculate_triangles_in_strip(data: np.ndarray, start: int, count: int):
	triangle_count = 0
	segment_length = 0

	for i in range(start, start + count):
		if data[i] == SEPARATOR:
			triangle_count += max(0, segment_length - 2)
			segment_length = 0
		else:
			segment_length += 1

	# not forget the last segment
	triangle_count += max(0, segment_length - 2)

	return triangle_count


def decode_triangle_strip(data: np.ndarray, start: int, count: int):
	triangle_count = calculate_triangles_in_strip(data, start, count)
	buffer = np.empty(triangle_count * 3, dtype=np.uint32)

	output_index = 0
	strip_length = 0
	previous_index = 0
	previous_previous_index = 0

	for i in range(start, start + count):
		index = data[i]
		if index == SEPARATOR:
			strip_length = 0
			continue

		if strip_length >= 2:
			if strip_length % 2 == 0:
				buffer[output_index:output_index + 3] = (
					previous_previous_index,
					previous_index,
					index,
				)
			else:
				buffer[output_index:output_index + 3] = (
					previous_index,
					previous_previous_index,
					index,
				)

			output_index += 3

		previous_previous_index = previous_index
		previous_index = index
		strip_length += 1

	return buffer

@dataclass
class Index_Buffer:
	header: Unified_Index_Buffer_Header
	data: bytes

	def get_np_array(self, endianness: Endianness, ranges: list[tuple[int, int, Primitive_Type]] | None = None) -> np.ndarray:
		if self.header.is_32bit:
			data = np.frombuffer(
				self.data,
				dtype=np.dtype(f"{endianness.value}u4"),
			)
		else:
			data = np.frombuffer(
				self.data,
				dtype=np.dtype(f"{endianness.value}u2"),
			).astype(np.uint32)

		if ranges is not None:
			data = np.concatenate(
				[
					decode_triangle_strip(data, start, count)
					if primitive_type == Primitive_Type.TRIANGLE_STRIP
					else data[start:start + count]
					for start, count, primitive_type in ranges
				]
			)

		return data.reshape(-1, 3)
