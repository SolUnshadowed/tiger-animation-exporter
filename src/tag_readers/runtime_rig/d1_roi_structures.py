from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, u32, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_64
from src.tag_readers.runtime_rig.unified_structures import Unified_Runtime_Rig_Main_Struct


@binary_struct()
@dataclass
class D1_ROI_Runtime_Rig_Main_Struct:

	rig_components_pointer: Annotated[Vec_Pointer_64, L_Padding(128)]
	controls_relations_pointer: Vec_Pointer_64
	controls_transforms_pointer: Vec_Pointer_64
	ik_controls_pointer: Vec_Pointer_64
	some_tag: Annotated[int, u32]

	bone_to_control_pointer: Annotated[Vec_Pointer_64, L_Padding(4)]
	control_to_bone_pointer: Vec_Pointer_64

	control_name_to_bone_index_pointer: Annotated[Vec_Pointer_64, L_Padding(24)]

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