from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version

from src.tag_readers.render_globals.d1_devalpha_structures import S_Render_Globals_Header_D1_DEVALPHA
from src.tag_readers.render_globals.d1_roi_structures import S_Render_Globals_Header_D1_ROI
from src.tag_readers.render_globals.unified_structures import Unified_Render_Globals_Header

def read_render_globals_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_Render_Globals_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Render_Globals_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Render_Globals_Header_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_render_globals_header is not implemented for {game_version}")
