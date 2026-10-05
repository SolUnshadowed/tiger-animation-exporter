from libs.tiger_pkg.game_version import Game_Version
from libs.binary_reader import u32, Endianness, Binary_Reader

from src.tag_readers.s_pattern_component.read_s_pattern_component import read_s_pattern_component_header, Unified_S_Pattern_Component_Header
from src.tag_readers.s_dynamic_model_component.d1_devalpha_structures import Dynamic_Model_Component_Main_Struct_D1_DEVALPHA
from src.tag_readers.s_dynamic_model_component.d1_roi_structures import Dynamic_Model_Component_Main_Struct_D1_ROI
from src.tag_readers.s_dynamic_model_component.unified_structures import Unified_Dynamic_Model_Component


'''
s_pattern component containing a reference to a model

s_entity (s_pattern) -> s_dynamic_model_component -> s_enitiy_model
'''


def read_dynamic_model_component(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_Dynamic_Model_Component:
	header: Unified_S_Pattern_Component_Header = read_s_pattern_component_header(reader, game_version, endianness)

	reader.seek(header.definition_pointer.get_address())
	tag = u32.read_from(reader, endianness)
	reader.seek(header.definition_pointer.get_address())

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(
				Dynamic_Model_Component_Main_Struct_D1_DEVALPHA,
				override_endianness=endianness
			).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(
				Dynamic_Model_Component_Main_Struct_D1_ROI,
	            override_endianness=endianness
			).to_unified()
		case _:
			raise NotImplementedError(f"Dynamic_Model_Component is not implemented for {game_version}")
