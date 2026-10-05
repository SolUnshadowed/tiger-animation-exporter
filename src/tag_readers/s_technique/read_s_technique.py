from dataclasses import dataclass

from libs.tiger_pkg.game_version import Game_Version
from libs.binary_reader import Endianness, Binary_Reader

from src.tag_readers.s_technique.d1_devalpha_structures import S_Technique_Header_D1_DEVALPHA
from src.tag_readers.s_technique.unified_structures import Unified_S_Technique_Header


@dataclass
class Technique:
	header: Unified_S_Technique_Header


def read_s_technique_header(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Unified_S_Technique_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Technique_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_s_technique_header is not available for {game_version}")


def read_s_technique(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Technique:
	header = read_s_technique_header(reader, game_version, endianness)

	return Technique(header)