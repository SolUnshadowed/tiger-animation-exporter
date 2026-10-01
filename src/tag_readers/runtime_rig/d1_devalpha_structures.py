from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, Endianness, s8, s16, s32, u32, f32, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_32
from src.tag_readers.runtime_rig.unified_structures import Space_Def, IK_Function_Type, Constraint_Type, Unified_Constraint, Unified_Runtime_Rig_Main_Struct


@binary_struct()
@dataclass
class D1_DEVALPHA_Runtime_Rig_Main_Struct:

	rig_components_pointer: Annotated[Vec_Pointer_32, L_Padding(68)]
	controls_relations_pointer: Vec_Pointer_32
	controls_transforms_pointer: Vec_Pointer_32
	ik_controls_pointer: Vec_Pointer_32 # ik controls pointer
	some_tag: Annotated[int, u32]
	bone_to_control_pointer: Vec_Pointer_32
	control_to_bone_pointer: Vec_Pointer_32

	control_name_to_bone_index_pointer: Annotated[Vec_Pointer_32, L_Padding(12)]

	def to_unified(self) -> Unified_Runtime_Rig_Main_Struct:
		return Unified_Runtime_Rig_Main_Struct(
			rig_components_pointer=self.rig_components_pointer,
			controls_relations_pointer=self.controls_relations_pointer,
			controls_transforms_pointer=self.controls_transforms_pointer,
			ik_controls_pointer=self.ik_controls_pointer,
			bone_to_control_pointer=self.bone_to_control_pointer,
			control_to_bone_pointer=self.control_to_bone_pointer,
			control_name_to_bone_index_pointer=self.control_name_to_bone_index_pointer,
		)

@binary_struct(size=48)
@dataclass(slots=True)
class Constraint_D1:
	rot_space_0: Space_Def
	rot_space_1: Space_Def
	aim_influence: Annotated[float, f32]
	prob_flags_0: Annotated[int, s32, Endianness.LE]
	tr_space_0: Space_Def
	tr_space_1: Space_Def
	coof_1: Annotated[float, f32]
	prob_flags_1: Annotated[int, s32, Endianness.LE]
	bone_index: Annotated[int, s16]
	ik_chain_start_bone_index: Annotated[int, s16]
	constraint_type: Annotated[Constraint_Type, s8]
	ik_function_type: Annotated[IK_Function_Type, s8]
	unk_0: Annotated[int, s8]
	unk_1: Annotated[int, s8]

	def to_unified(self) -> Unified_Constraint:
		return Unified_Constraint(
			hash=0,
			rot_space_0=self.rot_space_0,
			rot_space_1=self.rot_space_1,
			aim_influence=self.aim_influence,
			prob_flags_0=self.prob_flags_0,
			tr_space_0=self.tr_space_0,
			tr_space_1=self.tr_space_1,
			coof_1=self.coof_1,
			prob_flags_1=self.prob_flags_1,
			bone_index=self.bone_index,
			ik_chain_start_bone_index=self.ik_chain_start_bone_index,
			constraint_type=self.constraint_type,
			ik_function_type=self.ik_function_type,
			unk_0=self.unk_0,
			unk_1=self.unk_1,
		)