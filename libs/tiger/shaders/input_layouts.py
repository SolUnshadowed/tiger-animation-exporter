from enum import IntEnum


class Input_Semantics(IntEnum):
	POSITION = 0
	BLENDWEIGHT = 1
	BLENDINDICES = 2
	NORMAL = 3
	PSIZE = 4
	TEXCOORD = 5
	TANGENT = 6
	BINORMAL = 7
	COLOR = 8