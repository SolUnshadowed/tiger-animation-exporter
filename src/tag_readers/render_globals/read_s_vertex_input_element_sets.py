from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version
from libs.tag.tag_array import Tag_Array
from libs.tag.tag_pointers import Base_Tag_Pointer

from src.tag_readers.render_globals.d1_devalpha_structures import S_Vertex_Input_Element_Sets_Header_D1_DEVALPHA, S_Vertex_Input_Element_Set_D1_DEVALPHA
from src.tag_readers.render_globals.d1_roi_structures import S_Vertex_Input_Element_Set_D1_ROI, S_Vertex_Input_Element_Sets_Header_D1_ROI
from src.tag_readers.render_globals.unified_structures import Unified_S_Vertex_Input_Element_Sets_Header, Unified_S_Vertex_Input_Element_Set_Pointer
from src.tag_readers.render_globals.common_structures import S_Vertex_Input_Element


type S_Vertex_Input_Element_Set = list[S_Vertex_Input_Element]   # basically a layout of a single vertex buffer


def read_s_vertex_input_element_sets_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_S_Vertex_Input_Element_Sets_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Vertex_Input_Element_Sets_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Vertex_Input_Element_Sets_Header_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_s_vertex_input_element_sets_header is not supported for {game_version}")


def read_s_vertex_element_set_pointers(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, pointer: Base_Tag_Pointer
) -> list[Unified_S_Vertex_Input_Element_Set_Pointer]:

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return [
				element_set.to_unified()
				for element_set in Tag_Array[S_Vertex_Input_Element_Set_D1_DEVALPHA](
					reader, pointer, S_Vertex_Input_Element_Set_D1_DEVALPHA, endianness,
					bitness=game_version.pointer_block_bitness()
				)
			]
		case _:
			return [
				element_set.to_unified()
				for element_set in Tag_Array[S_Vertex_Input_Element_Set_D1_ROI](
					reader, pointer, S_Vertex_Input_Element_Set_D1_ROI, endianness,
					bitness=game_version.pointer_block_bitness()
				)
			]


def read_s_vertex_element_sets_data(
	reader: Binary_Reader, game_version: Game_Version,
	endianness: Endianness, element_sets: list[Unified_S_Vertex_Input_Element_Set_Pointer]
) -> list[S_Vertex_Input_Element_Set]:
	layouts = []

	for element_set in element_sets:
		layouts.append(
			[
				element
				for element in Tag_Array[S_Vertex_Input_Element](
					reader, element_set.elements_pointer, S_Vertex_Input_Element, endianness,
					bitness=game_version.pointer_block_bitness()
				)
			]
		)

	return layouts


def read_s_vertex_element_sets(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> list[S_Vertex_Input_Element_Set]:
	header = read_s_vertex_input_element_sets_header(reader, game_version, endianness)

	element_sets = read_s_vertex_element_set_pointers(reader, game_version, endianness, header.sets_pointer)

	return read_s_vertex_element_sets_data(reader, game_version, endianness, element_sets)
