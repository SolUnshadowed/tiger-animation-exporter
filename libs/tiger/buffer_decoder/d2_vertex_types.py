import numpy as np

from libs.tiger.buffer_decoder.vertex_type import Tiger_Vertex_Type

d2_types = {

	# R32_FLOAT
	1: Tiger_Vertex_Type(
		components_bits=(32),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("f4")
	),
	# R32G32_FLOAT
	2: Tiger_Vertex_Type(
		components_bits=(32, 32),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("f4")
	),
	# R32G32B32_FLOAT
	3: Tiger_Vertex_Type(
		components_bits=(32, 32, 32),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("f4")
	),
	# R32G32B32A32_FLOAT
	4: Tiger_Vertex_Type(
		components_bits=(32, 32, 32, 32),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("f4")
	),
	# R8G8B8A8_UNORM
	5: Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=False,
		is_normalized=True,
		numpy_type=np.dtype("u1")
	),
	# R8G8B8A8_UINT
	6: Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u1")
	),
	# R16G16_SINT
	7: Tiger_Vertex_Type(
		components_bits=(16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i2")
	),
	# R16G16B16A16_SINT
	8: Tiger_Vertex_Type(
		components_bits=(16, 16, 16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i2")
	),
	# R16G16B16A16_UINT
	9: Tiger_Vertex_Type(
		components_bits=(16, 16, 16, 16),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u2")
	),
	# R16G16_SNORM
	10: Tiger_Vertex_Type(
		components_bits=(16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=np.dtype("u2")
	),
	# R16G16B16A16_SNORM
	11: Tiger_Vertex_Type(
		components_bits=(16, 16, 16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=np.dtype("u2")
	),
	# R16G16_FLOAT
	12: Tiger_Vertex_Type(
		components_bits=(16, 16),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u2")
	),
	# R16G16B16A16_FLOAT
	13: Tiger_Vertex_Type(
		components_bits=(16, 16, 16, 16),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u2")
	),
	# R8G8B8A8_SINT
	14: Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i1")
	),
	# R8G8B8A8_SNORM
	15: Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=np.dtype("u1")
	),
	# R10G10B10A2_UINT
	16: Tiger_Vertex_Type(
		components_bits=(10, 10, 10, 2),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=None
	),
	# R10G10B10A2_UNORM
	17: Tiger_Vertex_Type(
		components_bits=(10, 10, 10, 2),
		is_float=False,
		is_signed=False,
		is_normalized=True,
		numpy_type=None
	),
	# R32_SINT
	18: Tiger_Vertex_Type(
		components_bits=(32),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i4"),
	),
	# R32G32_SINT
	19: Tiger_Vertex_Type(
		components_bits=(32, 32),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i4"),
	),
	# R32G32B32A32_SINT
	20: Tiger_Vertex_Type(
		components_bits=(32, 32, 32, 32),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i4")
	),
	# R32_UINT
	21: Tiger_Vertex_Type(
		components_bits=(32),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u4")
	),
	# R32G32_UINT
	22: Tiger_Vertex_Type(
		components_bits=(32, 32),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u4")
	),
	# R32G32B32A32_UINT
	23: Tiger_Vertex_Type(
		components_bits=(32, 32, 32, 32),
		is_float=False,
		is_signed=False,
		is_normalized=False,
		numpy_type=np.dtype("u4")
	),
	# R16_SINT
	24: Tiger_Vertex_Type(
		components_bits=(16),
		is_float=False,
		is_signed=True,
		is_normalized=False,
		numpy_type=np.dtype("i2")
	),
	# R8_UNORM
	25: Tiger_Vertex_Type(
		components_bits=(8),
		is_float=False,
		is_signed=False,
		is_normalized=True,
		numpy_type=np.dtype("u1")
	),
	# R8G8B8A8_UNORM_SRGB
	31: Tiger_Vertex_Type(
		components_bits=(8, 8, 8, 8),
		is_float=False,
		is_signed=False,
		is_normalized=True,
		numpy_type=np.dtype("u1")
	),
	# R11G11B10_FLOAT
	32: Tiger_Vertex_Type(
		components_bits=(11, 11, 10),
		is_float=True,
		is_signed=False,
		is_normalized=False,
		numpy_type=None
	),
	# R16G16B16A16_SNORM
	33: Tiger_Vertex_Type(
		components_bits=(16, 16, 16, 16),
		is_float=False,
		is_signed=True,
		is_normalized=True,
		numpy_type=np.dtype("u2")
	),
}
