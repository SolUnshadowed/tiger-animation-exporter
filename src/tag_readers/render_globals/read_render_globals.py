from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tag.tag_array import Tag_Array

from src.tag_readers.render_globals.d1_devalpha_structures import S_Render_Globals_Header_D1_DEVALPHA
from src.tag_readers.render_globals.d1_roi_structures import S_Render_Globals_Header_D1_ROI
from src.tag_readers.render_globals.d2_eof_structures import S_Render_Globals_Header_D2_EOF, Element_8080870F
from src.tag_readers.render_globals.unified_structures import Unified_Render_Globals


def read_render_globals(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_Render_Globals:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Render_Globals_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Render_Globals_Header_D1_ROI, override_endianness=endianness).to_unified()
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			render_globals_header = reader.read_struct(S_Render_Globals_Header_D2_EOF, override_endianness=endianness)

			array = Tag_Array[Element_8080870F](
				reader, render_globals_header.array, Element_8080870F,
				endianness, game_version.pointer_block_bitness()
			)

			return Unified_Render_Globals(render_globals_header.file_size, array[0].wide_hash.handle_32)
		case _:
			raise NotImplementedError(f"read_render_globals_header is not implemented for {game_version}")
