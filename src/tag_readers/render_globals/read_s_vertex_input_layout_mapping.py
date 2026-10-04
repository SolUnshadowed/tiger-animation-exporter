from dataclasses import dataclass

from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version
from libs.tag.tag_array import Tag_Array
from libs.tag.tag_pointers import Base_Vec_Pointer

from src.tag_readers.render_globals.d1_devalpha_structures import S_Vertex_Input_Layout_Mapping_Header_D1_DEVALPHA
from src.tag_readers.render_globals.d1_roi_structures import S_Vertex_Input_Layout_Mapping_Header_D1_ROI
from src.tag_readers.render_globals.d2_eof_structures import S_Vertex_Input_Layout_Mapping_Header_D2_EOF
from src.tag_readers.render_globals.unified_structures import Unified_S_Vertex_Input_Layout_Mapping_Header
from src.tag_readers.render_globals.common_structures import S_Vertex_Layout


@dataclass
class S_Vertex_Input_Layout_Mapping:
	header: Unified_S_Vertex_Input_Layout_Mapping_Header
	layouts: list[S_Vertex_Layout]


def read_s_vertex_input_layout_mapping_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_S_Vertex_Input_Layout_Mapping_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Vertex_Input_Layout_Mapping_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Vertex_Input_Layout_Mapping_Header_D1_ROI, override_endianness=endianness).to_unified()
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			return reader.read_struct(S_Vertex_Input_Layout_Mapping_Header_D2_EOF, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_s_vertex_input_element_sets_header is not supported for {game_version}")


def read_s_vertex_input_layout_mapping_layouts(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness,
	pointer: Base_Vec_Pointer
) -> list[S_Vertex_Layout]:
	return [
		element
		for element in Tag_Array[S_Vertex_Layout](
			reader, pointer, S_Vertex_Layout, endianness,
			bitness=game_version.pointer_block_bitness()
		)
	]


def read_s_vertex_input_layout_mapping(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> S_Vertex_Input_Layout_Mapping:
	header = read_s_vertex_input_layout_mapping_header(reader, game_version, endianness)

	layouts = read_s_vertex_input_layout_mapping_layouts(reader, game_version, endianness, header.arr_pointer)
	
	return S_Vertex_Input_Layout_Mapping(header, layouts)

