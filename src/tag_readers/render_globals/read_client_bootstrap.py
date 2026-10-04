from libs.binary_reader import Binary_Reader, Endianness
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tag.tag_array import Tag_Array
from libs.tag.tag_pointers import Base_Vec_Pointer

from src.tag_readers.render_globals.unified_structures import Unified_Client_Bootstrap_Header, Unified_Client_Bootstrap
from src.tag_readers.render_globals.d1_devalpha_structures import Client_Bootstrap_Header_D1_DEVALPHA
from src.tag_readers.render_globals.d1_roi_structures import Client_Bootstrap_Header_D1_ROI
from src.tag_readers.render_globals.d2_eof_structures import Client_Bootstrap_Header_D2_EOF, Client_Bootstrap_Array_Element_D2_EOF
from src.tag_readers.render_globals.common_structures import Client_Bootstrap_Array_Element


def read_client_bootstrap_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_Client_Bootstrap_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(Client_Bootstrap_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(Client_Bootstrap_Header_D1_ROI, override_endianness=endianness).to_unified()
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			return reader.read_struct(Client_Bootstrap_Header_D2_EOF, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError(f"read_client_bootstrap_header is not implemented for {game_version}")


def read_client_bootstrap_array(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, pointer: Base_Vec_Pointer
) -> list[Tag_Handle]:
	match game_version:
		case Game_Version.D1_DEV_ALPHA | Game_Version.D1_ROI:
			return [
				element.handle
				for element in Tag_Array[Client_Bootstrap_Array_Element](
					reader, pointer, Client_Bootstrap_Array_Element, endianness, game_version.pointer_block_bitness()
				)
			]
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			return [
				element.handle.handle_32
				for element in Tag_Array[Client_Bootstrap_Array_Element_D2_EOF](
					reader, pointer, Client_Bootstrap_Array_Element_D2_EOF, endianness, game_version.pointer_block_bitness()
				)
			]
		case _:
			raise NotImplementedError(f"read_client_bootstrap_array is not implemented for {game_version}")


def read_client_bootstrap(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Unified_Client_Bootstrap:
	header = read_client_bootstrap_header(reader, game_version, endianness)

	arr = read_client_bootstrap_array(reader, game_version, endianness, header.arr_pointer)

	return Unified_Client_Bootstrap(header, arr)
