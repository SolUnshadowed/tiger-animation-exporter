from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version

from src.tag_readers.s_pattern_component.d1_devalpha_structures import S_Pattern_Component_Header_D1_DEVALPHA
from src.tag_readers.s_pattern_component.d1_roi_strucutres import S_Pattern_Component_Header_D1_ROI
from src.tag_readers.s_pattern_component.unified_structures import Unified_S_Pattern_Component_Header


def read_s_pattern_component_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_S_Pattern_Component_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			header = reader.read_struct(S_Pattern_Component_Header_D1_DEVALPHA, override_endianness=endianness)
			return header.to_unified()
		case _:
			header = reader.read_struct(S_Pattern_Component_Header_D1_ROI, override_endianness=endianness)
			return header.to_unified()
