from enum import Enum

from libs.binary_reader import Endianness


class Game_Version(str, Enum):
	D1_DEV_ALPHA = "d1_devalpha"	# Xbox 360, BE
	D1_ROI = "d1_roi"				# PS4/Xbox One, LE
	#D2_SK = "d2_sk"				# Win64?, LE
	D2_EOF = "d2_eof"				# Win64?, LE
	MARATHON = "marathon"			# Win64?, LE

	def endianness(self) -> Endianness:
		return game_version_to_endianness[self]

	def pointer_block_bitness(self):
		match self:
			case Game_Version.D1_DEV_ALPHA:
				return 32
			case _:
				return 64


game_version_to_endianness: dict[Game_Version, Endianness] = {
	Game_Version.D1_DEV_ALPHA: Endianness.BE,
	Game_Version.D1_ROI: Endianness.LE,
	#Game_Version.D2_SK: Endianness.LE,
	Game_Version.D2_EOF: Endianness.LE,
	Game_Version.MARATHON: Endianness.LE,
}
