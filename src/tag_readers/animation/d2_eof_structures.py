from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, L_Padding, u8, u16, u32, u64

from libs.tag.tag_pointers import Rel_Pointer_64, Vec_Pointer_64
from src.tag_readers.animation.unified_structures import Unified_Animation_Header

from .animation_type import Animation_Type

# also valid for marathon
@binary_struct(size=0x182)
@dataclass
class D2_EOF_Animation_Header:
	file_size: Annotated[int, u64]

	static_bone_data_pointer: Annotated[Rel_Pointer_64, L_Padding(8)]
	animated_bone_data_pointer: Rel_Pointer_64
	extra_data_0: Rel_Pointer_64
	extra_data_1: Rel_Pointer_64
	extra_data_2: Rel_Pointer_64
	extra_data_3: Rel_Pointer_64
	extra_data_4: Rel_Pointer_64
	extra_data_5: Rel_Pointer_64
	extra_data_6: Rel_Pointer_64
	extra_data_7: Rel_Pointer_64

	static_scale_control_map_pointer: Annotated[Vec_Pointer_64, L_Padding(72)]
	static_rotation_control_map_pointer: Vec_Pointer_64
	static_translation_control_map_pointer: Vec_Pointer_64
	animated_scale_control_map_pointer: Vec_Pointer_64
	animated_rotation_control_map_pointer: Vec_Pointer_64
	animated_translation_control_map_pointer: Vec_Pointer_64

	animation_hash: Annotated[int, u32, L_Padding(24)]

	frame_count: Annotated[int, u16, L_Padding(28)]
	node_count: Annotated[int, u16]
	rig_control_count: Annotated[int, u16]

	unk_arr_1_pointer: Annotated[Vec_Pointer_64, L_Padding(10)]
	frame_events_array_pointer: Vec_Pointer_64
	rig_components_array_pointer: Vec_Pointer_64

	animation_type: Annotated[Animation_Type, u8, L_Padding(1)]

	def to_unified(self) -> Unified_Animation_Header:
		return Unified_Animation_Header(
			file_size=self.file_size,
			static_bone_data_pointer=self.static_bone_data_pointer,
			animated_bone_data_pointer=self.animated_bone_data_pointer,
			extra_data_0_pointer=self.extra_data_0,
			extra_data_1_pointer=self.extra_data_1,
			extra_data_2_pointer=self.extra_data_2,
			extra_data_3_pointer=self.extra_data_3,
			extra_data_4_pointer=self.extra_data_4,
			extra_data_5_pointer=self.extra_data_5,
			extra_data_6_pointer=self.extra_data_6,
			extra_data_7_pointer=self.extra_data_7,
			static_scale_control_map_pointer=self.static_scale_control_map_pointer,
			static_rotation_control_map_pointer=self.static_rotation_control_map_pointer,
			static_translation_control_map_pointer=self.static_translation_control_map_pointer,
			animated_scale_control_map_pointer=self.animated_scale_control_map_pointer,
			animated_rotation_control_map_pointer=self.animated_rotation_control_map_pointer,
			animated_translation_control_map_pointer=self.animated_translation_control_map_pointer,
			animation_hash=self.animation_hash,
			frame_count=self.frame_count,
			node_count=self.node_count,
			rig_control_count=self.rig_control_count,
			frame_events_array_pointer=self.frame_events_array_pointer,
			rig_components_array_pointer=self.rig_components_array_pointer,
			animation_type=self.animation_type
		)
