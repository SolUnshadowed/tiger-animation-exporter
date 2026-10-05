from libs.binary_reader import Binary_Reader, Endianness, binary_struct
from libs.tiger_pkg.game_version import Game_Version

from src.tag_readers.buffers.d1_devalpha_structures import Vertex_Buffer_Header_D1_DEVALPHA, Index_Buffer_Header_D1_DEVALPHA
from src.tag_readers.buffers.d1_roi_structures import Vertex_Buffer_Header_D1_ROI, Index_Buffer_Header_D1_ROI
from src.tag_readers.buffers.unified_structures import Unified_Index_Buffer_Header, Unified_Vertex_Buffer_Header


def read_vertex_buffer(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Unified_Vertex_Buffer_Header:
	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(Vertex_Buffer_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(Vertex_Buffer_Header_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_vertex_buffer is an unsupported for {game_version}")


def read_index_buffer(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Unified_Index_Buffer_Header:
	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(Index_Buffer_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(Index_Buffer_Header_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_index_buffer is an unsupported for {game_version}")
