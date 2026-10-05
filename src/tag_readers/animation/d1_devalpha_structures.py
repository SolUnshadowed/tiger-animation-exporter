from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import (
	binary_struct, L_Padding, Array, u8, u16, u32, f32
)
from libs.tag.tag_pointers import Rel_Pointer_32, Vec_Pointer_32
from src.tag_readers.animation.unified_structures import (
	Unified_Animation_Header, Unified_Codec_0_Header_Part, Unified_Codec_1_Header_Part, Unified_Codec_2_Header_Part, Unified_Codec_3_Header_Part
)


@binary_struct()
@dataclass(slots=True)
class D1_DEVALPHA_Animation_Header:
	file_size: Annotated[int, u32]

	static_bone_data_pointer: Annotated[Rel_Pointer_32, L_Padding(12)]
	animated_bone_data_pointer: Rel_Pointer_32
	extra_data_0: Rel_Pointer_32
	extra_data_1: Rel_Pointer_32
	extra_data_2: Rel_Pointer_32
	extra_data_3: Rel_Pointer_32
	extra_data_4: Rel_Pointer_32
	extra_data_5: Rel_Pointer_32
	extra_data_6: Rel_Pointer_32
	extra_data_7: Rel_Pointer_32

	static_scale_control_map_pointer: Annotated[Vec_Pointer_32, L_Padding(56)]
	static_rotation_control_map_pointer: Vec_Pointer_32
	static_translation_control_map_pointer: Vec_Pointer_32
	animated_scale_control_map_pointer: Vec_Pointer_32
	animated_rotation_control_map_pointer: Vec_Pointer_32
	animated_translation_control_map_pointer: Vec_Pointer_32

	animation_hash: Annotated[int, u32, L_Padding(24)]

	frame_count: Annotated[int, u16, L_Padding(20)]
	node_count: Annotated[int, u8]
	rig_control_count: Annotated[int, u8]

	unk_arr_1_pointer: Annotated[Vec_Pointer_32, L_Padding(12)]
	frame_events_array_pointer: Vec_Pointer_32
	rig_components_array_pointer: Vec_Pointer_32

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
			rig_components_array_pointer=self.rig_components_array_pointer
		)


@binary_struct()
@dataclass(slots=True)
class D1_DEVALPHA_Codec_0:
	frame_count: Annotated[int, u32]
	scale_stream_pointer:  Vec_Pointer_32
	rotation_stream_pointer:  Vec_Pointer_32
	translation_stream_pointer:  Vec_Pointer_32

	def to_unified(self) -> Unified_Codec_0_Header_Part:
		return Unified_Codec_0_Header_Part(
			frame_count=self.frame_count,
			scale_stream_pointer=self.scale_stream_pointer,
			rotation_stream_pointer=self.rotation_stream_pointer,
			translation_stream_pointer=self.translation_stream_pointer
		)


@binary_struct()
@dataclass(slots=True)
class D1_DEVALPHA_Codec_1:
	uncompressed_data_pointer: Vec_Pointer_32
	compressed_data_pointer: Vec_Pointer_32
	keyframe_deltas_pointer: Vec_Pointer_32
	interpolation_data_pointer: Vec_Pointer_32
	quantization_minimums_pointer: Vec_Pointer_32
	quantization_extents_pointer: Vec_Pointer_32
	array_7_pointer: Vec_Pointer_32

	def to_unified(self) -> Unified_Codec_1_Header_Part:
		return Unified_Codec_1_Header_Part(
			uncompressed_data_pointer=self.uncompressed_data_pointer,
			compressed_data_pointer=self.compressed_data_pointer,
			keyframe_deltas_pointer=self.keyframe_deltas_pointer,
			interpolation_data_pointer=self.interpolation_data_pointer,
			quantization_minimums_pointer=self.quantization_minimums_pointer,
			quantization_extents_pointer=self.quantization_extents_pointer,
			array_7_pointer=self.array_7_pointer
		)


@binary_struct()
@dataclass(slots=True)
class D1_DEVALPHA_Codec_2:
	frame_count: Annotated[int, u32]
	stream_data_pointer: Vec_Pointer_32
	quantization_minimums: Vec_Pointer_32
	quantization_extents: Vec_Pointer_32

	def to_unified(self) -> Unified_Codec_2_Header_Part:
		return Unified_Codec_2_Header_Part(
			frame_count=self.frame_count,
			stream_data_pointer=self.stream_data_pointer,
			quantization_minimums_pointer=self.quantization_minimums,
			quantization_extents_pointer=self.quantization_extents
		)


@binary_struct()
@dataclass(slots=True)
class D1_DEVALPHA_Codec_3:
	frame_count: Annotated[int, u32]
	scale_stream_quantization: Annotated[list[float], Array(f32, 2)]
	translation_stream_quantization: Annotated[list[list[float]], Array(Array(f32, 3), 2)]
	stream_pointer: Vec_Pointer_32

	def to_unified(self) -> Unified_Codec_3_Header_Part:
		return Unified_Codec_3_Header_Part(
			frame_count=self.frame_count,
			scale_stream_quantization=self.scale_stream_quantization,
			translation_stream_quantization=self.translation_stream_quantization,
			stream_data_pointer=self.stream_pointer
		)
