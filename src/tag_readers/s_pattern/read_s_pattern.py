from dataclasses import dataclass

from libs.binary_reader import Binary_Reader, Endianness, binary_struct
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tag.tag_array import Tag_Array

from src.tag_readers.s_pattern.unified_structures import Unified_S_Pattern_Header
from src.tag_readers.s_pattern.d1_devalpha_structures import S_Pattern_Header_D1_DEVALPHA
from src.tag_readers.s_pattern.d1_roi_structures import S_Pattern_Header_D1_ROI
from src.tag_readers.s_pattern.d2_eof_structures import S_Pattern_Header_D2_EOF


@binary_struct(align=12)
@dataclass
class Component_Entry:
	tag: Tag_Handle


@dataclass
class S_Pattern:
	header: Unified_S_Pattern_Header
	component_tag_handles: list[Tag_Handle]


def read_s_pattern_header(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Unified_S_Pattern_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Pattern_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Pattern_Header_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			return reader.read_struct(S_Pattern_Header_D2_EOF, override_endianness=endianness).to_unified()


def read_s_pattern(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> S_Pattern:
	header = read_s_pattern_header(reader, game_version, endianness)

	components = Tag_Array[Component_Entry](
		reader, header.components_array_pointer, Component_Entry, endianness, bitness=game_version.pointer_block_bitness()
	)

	return S_Pattern(
		header,
		[component.tag for component in components]
	)
