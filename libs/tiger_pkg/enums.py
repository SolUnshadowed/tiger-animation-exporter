from collections import defaultdict
from enum import IntEnum


class Package_Platform(IntEnum):
	TOOl_32 = 0
	WIN_32 = 1
	WIN_64 = 2
	X360 = 3
	PS3 = 4
	TOOL_64 = 5
	WIN_64_V1 = 6
	PS4 = 7
	XBOX_ONE = 8
	STADIA = 9
	PS5 = 10
	SCARLETT = 11

	@property
	def fmt(self):
		match self:
			case Package_Platform.TOOl_32:
				return 'tool32'
			case Package_Platform.WIN_32:
				return 'win32'
			case Package_Platform.WIN_64:
				return 'win64'
			case Package_Platform.X360:
				return 'x360'
			case Package_Platform.PS3:
				return 'ps3'
			case Package_Platform.TOOL_64:
				return 'tool64'
			case Package_Platform.WIN_64_V1:
				return 'win64'
			case Package_Platform.PS4:
				return 'ps4'
			case Package_Platform.XBOX_ONE:
				return 'xboxone'
			case Package_Platform.STADIA:
				return 'stadia'
			case Package_Platform.PS5:
				return 'ps5'
			case Package_Platform.SCARLETT:
				return 'scarlett'

	@classmethod
	def from_fmt(cls, fmt: str) -> "Package_Platform":
		match fmt:
			case 'tool32':
				return Package_Platform.TOOl_32
			case 'win32':
				return Package_Platform.WIN_32
			case 'win64':
				return Package_Platform.WIN_64
			case 'x360':
				return Package_Platform.X360
			case 'ps3':
				return Package_Platform.PS3
			case 'tool64':
				return Package_Platform.TOOL_64
			case 'ps4':
				return Package_Platform.PS4
			case 'xboxone':
				return Package_Platform.XBOX_ONE
			case 'stadia':
				return Package_Platform.STADIA
			case 'ps5':
				return Package_Platform.PS5
			case 'scarlett':
				return Package_Platform.SCARLETT
			case _:
				raise Exception(f'Unknown platform: {fmt}')


class Package_Language(IntEnum):
	NONE = 0
	ENGLISH = 1
	FRENCH = 2
	ITALIAN = 3
	GERMAN = 4
	SPANISH = 5
	JAPANESE = 6
	PORTUGUESE = 7
	RUSSIAN = 8
	POLISH = 9
	SIMPLIFIED_CHINESE = 10
	TRADITIONAL_CHINESE = 11
	SPANISH_LAT_AM = 12
	KOREAN = 13
