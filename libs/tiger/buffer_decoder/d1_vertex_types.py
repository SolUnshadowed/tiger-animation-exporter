import numpy as np

from libs.tiger.buffer_decoder.vertex_type import Tiger_Vertex_Type

d1_devalpha_types = {
	# K_8_8_8_8_UNORM
	5: Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=False,
		is_normalized=True,
		numpy_type=np.dtype("u1"),
	),
	# K_8_8_8_8_UINT
	6 : Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u1"),
	),
	# K_16_16_SNORM
	9 : Tiger_Vertex_Type(
		components_bits=(16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=np.dtype("u2"),
	),
	# K_16_16_16_16_SNORM
	10 : Tiger_Vertex_Type(
		components_bits=(16, 16, 16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=np.dtype("u2"),
	),
	# K_16_16_FLOAT
	11: Tiger_Vertex_Type(
		components_bits=(16, 16),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u2"),
	),
	# K_11_11_10_SNORM
	28 : Tiger_Vertex_Type(
		components_bits=(11, 11, 10),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=None
	),
	#  K_2_10_10_10_SNORM
	29: Tiger_Vertex_Type(
		components_bits=(2, 10, 10, 10),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=None
	),
}
