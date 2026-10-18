from dataclasses import dataclass
from typing import Annotated

from src.tag_readers.runtime_rig.enums import Space_Type, Constraint_Type, IK_Function_Type
from libs.binary_reader import binary_struct, Endianness, s16
from libs.tag.tag_pointers import Base_Vec_Pointer


@binary_struct(size=6)
@dataclass(slots=True)
class Space_Def:
	bone_index_0: Annotated[int, s16]
	bone_index_1: Annotated[int, s16]
	space_type: Annotated[Space_Type, s16, Endianness.LE]


@dataclass(slots=True)
class Unified_Constraint:
	hash: int
	rot_space_0: Space_Def
	rot_space_1: Space_Def
	aim_influence: float
	prob_flags_0: int
	tr_space_0: Space_Def
	tr_space_1: Space_Def
	coof_1: float
	prob_flags_1: int
	bone_index: int
	ik_chain_start_bone_index: int
	constraint_type: Constraint_Type
	ik_function_type: IK_Function_Type
	pole_axis: int
	unk_1: int


@dataclass
class Unified_Runtime_Rig_Main_Struct:
	rig_components_pointer: Base_Vec_Pointer
	controls_relations_pointer: Base_Vec_Pointer
	controls_transforms_pointer: Base_Vec_Pointer
	ik_controls_pointer: Base_Vec_Pointer
	bone_to_control_pointer: Base_Vec_Pointer
	control_to_bone_pointer: Base_Vec_Pointer
	control_name_to_bone_index_pointer: Base_Vec_Pointer
	use_pole_axes: bool


