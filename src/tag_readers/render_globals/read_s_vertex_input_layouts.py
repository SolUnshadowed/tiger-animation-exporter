from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version

from src.tag_readers.render_globals.d1_devalpha_structures import S_Vertex_Input_Layouts_D1_DEVALPHA
from src.tag_readers.render_globals.d1_roi_structures import S_Vertex_Input_Layouts_D1_ROI
from src.tag_readers.render_globals.unified_structures import Unified_S_Vertex_Input_Layouts


def read_s_vertex_input_layouts(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_S_Vertex_Input_Layouts:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Vertex_Input_Layouts_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Vertex_Input_Layouts_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_s_vertex_input_layouts is not implemented for game_version {game_version}")
