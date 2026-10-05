from dataclasses import dataclass
from typing import Self

from libs.tag.tag_pointers import Base_Rel_Pointer, Base_Vec_Pointer


@dataclass(slots=True)
class Unified_Animation_Header:
	file_size: int
	static_bone_data_pointer: Base_Rel_Pointer
	animated_bone_data_pointer: Base_Rel_Pointer
	extra_data_0_pointer: Base_Rel_Pointer
	extra_data_1_pointer: Base_Rel_Pointer  # some decode_animation like codec header but with shortened error/stream lengths block?
	extra_data_2_pointer: Base_Rel_Pointer  # array pointer, array of some structs (structs can have grip and support string hashes in)
	extra_data_3_pointer: Base_Rel_Pointer  # decode_animation codec? But it seems it has polymorphic header or it is normal for any codec?
	extra_data_4_pointer: Base_Rel_Pointer  # decode_animation codec?
	extra_data_5_pointer: Base_Rel_Pointer  # two array pointer, first of floats second of u32? something quantized?
	extra_data_6_pointer: Base_Rel_Pointer
	extra_data_7_pointer: Base_Rel_Pointer
	static_scale_control_map_pointer: Base_Vec_Pointer
	static_rotation_control_map_pointer: Base_Vec_Pointer
	static_translation_control_map_pointer: Base_Vec_Pointer
	animated_scale_control_map_pointer: Base_Vec_Pointer
	animated_rotation_control_map_pointer: Base_Vec_Pointer
	animated_translation_control_map_pointer: Base_Vec_Pointer
	animation_hash: int
	frame_count: int
	node_count: int
	rig_control_count: int
	frame_events_array_pointer: Base_Vec_Pointer
	rig_components_array_pointer: Base_Vec_Pointer


@dataclass
class Unified_Codec_Common_Header:
	codec_type: int
	scale_stream_count: int
	rotation_stream_count: int
	translation_stream_count: int
	prob_error_value: float
	prob_compression_rate: float


@dataclass
class Unified_Codec_0_Header_Part:
	frame_count: int
	scale_stream_pointer: Base_Vec_Pointer
	rotation_stream_pointer: Base_Vec_Pointer
	translation_stream_pointer: Base_Vec_Pointer


@dataclass
class Unified_Codec_1_Header_Part:
	uncompressed_data_pointer: Base_Vec_Pointer
	compressed_data_pointer: Base_Vec_Pointer
	keyframe_deltas_pointer: Base_Vec_Pointer
	interpolation_data_pointer: Base_Vec_Pointer
	quantization_minimums_pointer: Base_Vec_Pointer
	quantization_extents_pointer: Base_Vec_Pointer
	array_7_pointer: Base_Vec_Pointer


@dataclass
class Unified_Codec_2_Header_Part:
	frame_count: int
	stream_data_pointer: Base_Vec_Pointer
	quantization_minimums_pointer: Base_Vec_Pointer
	quantization_extents_pointer: Base_Vec_Pointer


@dataclass
class Unified_Codec_3_Header_Part:
	frame_count: int
	scale_stream_quantization: list[float]
	translation_stream_quantization: list[list[float]]
	stream_data_pointer: Base_Vec_Pointer


@dataclass
class Unified_Codec_0(Unified_Codec_Common_Header, Unified_Codec_0_Header_Part):
	@classmethod
	def from_parts(
		cls,
		common: Unified_Codec_Common_Header,
		part: Unified_Codec_0_Header_Part
	) -> Self:
		return cls(**vars(common), **vars(part))


@dataclass
class Unified_Codec_1(Unified_Codec_Common_Header, Unified_Codec_1_Header_Part):
	@classmethod
	def from_parts(
		cls,
		common: Unified_Codec_Common_Header,
		part: Unified_Codec_1_Header_Part
	) -> Self:
		return cls(**vars(common), **vars(part))


@dataclass
class Unified_Codec_2(Unified_Codec_Common_Header, Unified_Codec_2_Header_Part):
	@classmethod
	def from_parts(
		cls,
		common: Unified_Codec_Common_Header,
		part: Unified_Codec_2_Header_Part
	) -> Self:
		return cls(**vars(common), **vars(part))


@dataclass
class Unified_Codec_3(Unified_Codec_Common_Header, Unified_Codec_3_Header_Part):
	@classmethod
	def from_parts(
		cls,
		common: Unified_Codec_Common_Header,
		part: Unified_Codec_3_Header_Part
	) -> Self:
		return cls(**vars(common), **vars(part))
