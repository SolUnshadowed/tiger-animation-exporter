import numpy as np

from libs.tiger.buffer_decoder.vertex_type import Tiger_Vertex_Type


def sign_extend_array(values: np.ndarray, bits: int) -> np.ndarray:
	values = values.astype(np.int32, copy=False)
	shift = 32 - bits
	return (values << shift) >> shift


def unpack_packed(packed: np.ndarray, components_bits: tuple[int, ...]) -> np.ndarray:
	"""
	unpacks components from packed uint32 values.
	components_bits defines component order from MSB to LSB.

	components_bits = (2, 10, 10, 10)
	uint32:
	31              30 29                    20 19                    10 9                     0
	│   component 0   │      component 1       │      component 2       │      component 3       │
	│      2 bit      │        10 bit          │        10 bit          │        10 bit          │
	"""

	component_count = len(components_bits)

	result = np.empty(
		(len(packed), component_count),
		dtype=np.uint32,
	)

	shift = 32
	for component_index, bits in enumerate(components_bits):
		shift -= bits
		mask = (1 << bits) - 1
		result[:, component_index] = (packed >> shift) & mask

	return result


def normalize(values: np.ndarray, components_bits: tuple[int, ...], is_signed: bool) -> np.ndarray:
	"""
	UNORM: [0, 2^bits - 1] -> [0, 1]
	SNORM: [-2^(bits-1), 2^(bits-1)-1] -> [-1, 1]
	"""

	result = np.empty(
		values.shape,
		dtype=np.float32,
	)

	for component_index, bits in enumerate(components_bits):
		if is_signed:
			max_value = (1 << (bits - 1)) - 1
			result[:, component_index] = np.maximum(values[:, component_index] / max_value, -1.0,)

		else:
			max_value = (1 << bits) - 1
			result[:, component_index] = (values[:, component_index] / max_value)

	return result


def extract_elements(
	data: bytes, stride: int, offset: int, element_size: int,
) -> np.ndarray:
	count = len(data) // stride

	return np.ndarray(
		shape=(count, element_size),
		dtype=np.uint8,
		buffer=data,
		offset=offset,
		strides=(stride, 1),
	).reshape(-1)


def decode_vertex_buffer(
	data: bytes, vertex_type: Tiger_Vertex_Type, endian: str, stride: int, offset: int,
) -> np.ndarray:
	raw = extract_elements(
		data=data,
		stride=stride,
		offset=offset,
		element_size=vertex_type.byte_size,
	)

	vertex_count = len(data) // stride

	if vertex_type.is_packed:  # u32 packed formats
		if vertex_type.bit_size != 32:
			raise NotImplementedError("Packed formats other than 32-bit are not supported")

		packed_dtype = np.dtype(endian + "u4")
		packed = raw.view(packed_dtype)
		values = unpack_packed(packed, vertex_type.components_bits)

	else:
		dtype = vertex_type.numpy_type.newbyteorder(endian)

		values = raw.view(dtype).reshape(
			vertex_count,
			vertex_type.component_count,
		)

	if vertex_type.is_float:  # if float just return
		return values.astype(np.float32)

	if vertex_type.is_signed:
		signed_values = np.empty(values.shape, dtype=np.int32)

		for component_index, bits in enumerate(vertex_type.components_bits):
			signed_values[:, component_index] = sign_extend_array(
				values[:, component_index],
				bits,
			)

		values = signed_values

	if not vertex_type.is_normalized:
		return values.astype(np.uint32)

	return normalize(
		values,
		vertex_type.components_bits,
		vertex_type.is_signed,
	)
