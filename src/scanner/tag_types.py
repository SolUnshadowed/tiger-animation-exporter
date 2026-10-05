from enum import Enum, auto


class Tag_Type(Enum):
	TextureOld = auto()
	Texture2D = auto()
	TextureCube = auto()
	Texture3D = auto()
	TextureSampler = auto()
	TextureLargeBuffer = auto()

	VertexBuffer = auto()
	IndexBuffer = auto()
	ConstantBuffer = auto()
	PixelShader = auto()
	VertexShader = auto()
	GeometryShader = auto()
	ComputeShader = auto()

	WwiseInitBank = auto()
	WwiseBank = auto()
	WwiseStream = auto()

	Havok = auto()
	OtfFontOrUmbraTome = auto()
	CriwareUsm = auto()

	Tag = auto()
	TagGlobal = auto()

	Unknown = auto()


def from_type_subtype_devalpha(tag_type: int, tag_subtype: int) -> Tag_Type:
	if tag_type in (32, 64, 1):
		match tag_subtype:
			case 1:
				return Tag_Type.Texture2D
			case 2:
				return Tag_Type.TextureCube
			case 3:
				return Tag_Type.Texture3D
			case 4:
				return Tag_Type.VertexBuffer
			case 6:
				return Tag_Type.IndexBuffer
			case 8:
				return Tag_Type.PixelShader
			case 9:
				return Tag_Type.VertexShader
			case _:
				return Tag_Type.Unknown

	match (tag_type, tag_subtype):
		case (0, 0) | (16, 0):
			return Tag_Type.Tag
		case (128, 0):
			return Tag_Type.TagGlobal
		case (0, 14):
			return Tag_Type.WwiseInitBank
		case (0, 15):
			return Tag_Type.WwiseBank
		case (2, 16):
			return Tag_Type.WwiseStream
		case _:
			return Tag_Type.Unknown


def from_type_subtype_d1(tag_type: int, tag_subtype: int) -> Tag_Type:
	if tag_type in (32, 1):
		is_header = (tag_type == 32)
		match tag_subtype:
			case 1:
				return Tag_Type.Texture2D
			case 2:
				return Tag_Type.TextureCube
			case 3:
				return Tag_Type.Texture3D
			case 4:
				return Tag_Type.VertexBuffer
			case 6:
				return Tag_Type.IndexBuffer
			# case 7: ConstantBuffer
			case 8:
				return Tag_Type.PixelShader
			case 9:
				return Tag_Type.VertexShader
			case 16:
				return Tag_Type.TextureSampler
			case _:
				return Tag_Type.Unknown

	match (tag_type, tag_subtype):
		case (0, 19):
			return Tag_Type.WwiseInitBank
		case (0, 20):
			return Tag_Type.WwiseBank
		case (8, 21):
			return Tag_Type.WwiseStream
		case (16, 0):
			return Tag_Type.Tag
		case (128, 0):
			return Tag_Type.TagGlobal
		case _:
			return Tag_Type.Unknown


def from_type_subtype_lf(tag_type: int, tag_subtype: int) -> Tag_Type:
	if tag_type in (32, 40):
		match tag_subtype:
			case 1:
				return Tag_Type.Texture2D
			case 2:
				return Tag_Type.TextureCube
			case 3:
				return Tag_Type.Texture3D
			case 4:
				return Tag_Type.VertexBuffer
			case 6:
				return Tag_Type.IndexBuffer
			case 7:
				return Tag_Type.ConstantBuffer
			case _:
				return Tag_Type.Unknown

	if tag_type in (33, 41):
		match tag_subtype:
			case 0:
				return Tag_Type.PixelShader
			case 1:
				return Tag_Type.VertexShader
			case 2:
				return Tag_Type.GeometryShader
			case 6:
				return Tag_Type.ComputeShader
			case _:
				return Tag_Type.Unknown

	if tag_type in (34, 42):
		match tag_subtype:
			case 1:
				return Tag_Type.TextureSampler
			case _:
				return Tag_Type.Unknown


	match (tag_type, tag_subtype):
		case (8, 0):
			return Tag_Type.Tag
		case (16, 0):
			return Tag_Type.TagGlobal
		case (24, 0):
			return Tag_Type.OtfFontOrUmbraTome
		case (26, 5):
			return Tag_Type.WwiseInitBank
		case (26, 6):
			return Tag_Type.WwiseBank
		case (26, 7):
			return Tag_Type.WwiseStream
		case (27, 0):
			return Tag_Type.Havok
		case (27, 1):
			return Tag_Type.CriwareUsm
		case (48, 1):
			return Tag_Type.TextureLargeBuffer
		case _:
			return Tag_Type.Unknown
