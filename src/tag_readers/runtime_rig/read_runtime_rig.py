from dataclasses import dataclass

from libs.binary_reader import Binary_Reader, Endianness, s16
from libs.tiger_pkg.game_version import Game_Version

from libs.tag.tag_pointers import Base_Tag_Pointer
from libs.tag.tag_array import Tag_Array
from libs.tag.data_types import Runtime_Rig_Component, Transform

from src.tag_readers.runtime_rig.d1_devalpha_structures import D1_DEVALPHA_Runtime_Rig_Main_Struct, Constraint_D1
from src.tag_readers.runtime_rig.d1_roi_structures import D1_ROI_Runtime_Rig_Main_Struct
from src.tag_readers.runtime_rig.d2_eof_structures import D2_EOF_Runtime_Rig_Main_Struct, Constraint_D2
from src.tag_readers.runtime_rig.unified_structures import Unified_Constraint, Unified_Runtime_Rig_Main_Struct

from src.tag_readers.s_pattern_component.read_s_pattern_component import read_s_pattern_component_header



@dataclass(slots=True)
class Runtime_Rig_Data:
	rig_components: Tag_Array[Runtime_Rig_Component]
	controls_relations: list[Unified_Constraint]
	controls_transforms: Tag_Array[Transform]
	bone_to_control: Tag_Array[int]
	control_to_bone: Tag_Array[int]
	control_name_to_bone_index: Tag_Array[Runtime_Rig_Component]


def read_runtime_rig_main_struct(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, pointer: Base_Tag_Pointer
) -> Unified_Runtime_Rig_Main_Struct:
	reader.seek(pointer.get_address())

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(
				D1_DEVALPHA_Runtime_Rig_Main_Struct, override_endianness=endianness
			).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(
				D1_ROI_Runtime_Rig_Main_Struct, override_endianness=endianness
			).to_unified()
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			return reader.read_struct(
				D2_EOF_Runtime_Rig_Main_Struct, override_endianness=endianness
			).to_unified()


def read_runtime_rig_data(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, main_struct: Unified_Runtime_Rig_Main_Struct
) -> Runtime_Rig_Data:
	bitness = game_version.pointer_block_bitness()

	rig_components = Tag_Array[Runtime_Rig_Component](
		reader, main_struct.rig_components_pointer, Runtime_Rig_Component, endianness, bitness
	)

	match game_version:
		case Game_Version.D1_DEV_ALPHA | Game_Version.D1_ROI:
			controls_relations = Tag_Array[Constraint_D1](
				reader, main_struct.controls_relations_pointer, Constraint_D1, endianness, bitness
			)
		case _:
			controls_relations = Tag_Array[Constraint_D2](
				reader, main_struct.controls_relations_pointer, Constraint_D2, endianness, bitness
			)

	controls_transforms = Tag_Array[Transform](
		reader, main_struct.controls_transforms_pointer, Transform, endianness, bitness
	)
	bone_to_control = Tag_Array[int](reader, main_struct.bone_to_control_pointer, s16, endianness, bitness)
	control_to_bone = Tag_Array[int](reader, main_struct.control_to_bone_pointer, s16, endianness, bitness)
	control_name_to_bone_index = Tag_Array(
		reader, main_struct.control_name_to_bone_index_pointer, Runtime_Rig_Component, endianness, bitness
	)

	return Runtime_Rig_Data(
		rig_components=rig_components,
		controls_relations=[constraint.to_unified() for constraint in controls_relations],
		controls_transforms=controls_transforms,
		bone_to_control=bone_to_control,
		control_to_bone=control_to_bone,
		control_name_to_bone_index=control_name_to_bone_index
	)


def read_runtime_rig(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Runtime_Rig_Data:
	header = read_s_pattern_component_header(reader, game_version, endianness)

	main_struct = read_runtime_rig_main_struct(reader, game_version, endianness, header.definition_pointer)

	runtime_rig_data = read_runtime_rig_data(reader, game_version, endianness, main_struct)

	return runtime_rig_data