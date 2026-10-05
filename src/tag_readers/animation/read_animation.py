import numpy as np

from dataclasses import dataclass

from libs.binary_reader import Binary_Reader, Endianness, u8, u16
from libs.tiger_pkg.game_version import Game_Version
from libs.tag.tag_pointers import Base_Tag_Pointer
from libs.tag.tag_array import Tag_Array, Tag_Array_NP
from libs.tag.data_types import Runtime_Rig_Component
from src.tag_readers.animation import exceptions as err
from src.tag_readers.animation.common_structures import Codec_Common_Header
from src.tag_readers.animation.d1_devalpha_structures import (
	D1_DEVALPHA_Animation_Header, D1_DEVALPHA_Codec_0, D1_DEVALPHA_Codec_1, D1_DEVALPHA_Codec_2, D1_DEVALPHA_Codec_3
)
from src.tag_readers.animation.d1_roi_structures import (
	D1_ROI_Animation_Header, D1_ROI_Codec_0, D1_ROI_Codec_1, D1_ROI_Codec_2, D1_ROI_Codec_3
)
from src.tag_readers.animation.d2_eof_structures import D2_EOF_Animation_Header
from src.tag_readers.animation.unified_structures import (
	Unified_Animation_Header, Unified_Codec_Common_Header,
	Unified_Codec_0, Unified_Codec_1, Unified_Codec_2, Unified_Codec_3
)


CODEC_REGISTRY = {
    Game_Version.D1_DEV_ALPHA: {
        0: (D1_DEVALPHA_Codec_0, Unified_Codec_0),
        1: (D1_DEVALPHA_Codec_1, Unified_Codec_1),
        2: (D1_DEVALPHA_Codec_2, Unified_Codec_2),
        3: (D1_DEVALPHA_Codec_3, Unified_Codec_3),
    },
    "DEFAULT": {
        0: (D1_ROI_Codec_0, Unified_Codec_0),
        1: (D1_ROI_Codec_1, Unified_Codec_1),
        2: (D1_ROI_Codec_2, Unified_Codec_2),
        3: (D1_ROI_Codec_3, Unified_Codec_3),
    }
}


@dataclass(slots=True)
class Control_Maps:
	static_scale_control_map: Tag_Array[int]
	static_rotation_control_map: Tag_Array[int]
	static_translation_control_map: Tag_Array[int]
	animated_scale_control_map: Tag_Array[int]
	animated_rotation_control_map: Tag_Array[int]
	animated_translation_control_map: Tag_Array[int]



@dataclass(slots=True)
class Codec_0_Buffers:
	animated_scale_stream: Tag_Array_NP
	animated_rotation_stream: Tag_Array_NP
	animated_translation_stream: Tag_Array_NP


@dataclass(slots=True)
class Codec_1_Buffers:
	uncompressed_data: Tag_Array_NP
	compressed_data: Tag_Array_NP
	keyframe_deltas: Tag_Array_NP
	interpolation_data: Tag_Array_NP
	quantization_minimums: Tag_Array_NP
	quantization_extents: Tag_Array_NP
	array_7: Tag_Array_NP


@dataclass(slots=True)
class Codec_2_Buffers:
	stream_data: Tag_Array_NP
	quantization_minimums: Tag_Array_NP
	quantization_extents: Tag_Array_NP


@dataclass(slots=True)
class Codec_3_Buffers:
	stream_data: Tag_Array_NP


type Codec_Buffers_Union = Codec_0_Buffers | Codec_1_Buffers | Codec_2_Buffers | Codec_3_Buffers


@dataclass(slots=True)
class Animation_Data:
	animation_header: Unified_Animation_Header
	static_bones_header: Unified_Codec_Common_Header | None
	static_bones_buffers: Codec_Buffers_Union | None
	animated_bones_header: Unified_Codec_Common_Header | None
	animated_bones_buffers: Codec_Buffers_Union | None
	control_maps: Control_Maps
	runtime_rig_components: Tag_Array[Runtime_Rig_Component]


def read_animation_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness
) -> Unified_Animation_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(D1_DEVALPHA_Animation_Header, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(D1_ROI_Animation_Header, override_endianness=endianness).to_unified()
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			return reader.read_struct(D2_EOF_Animation_Header, override_endianness=endianness).to_unified()


def read_control_maps(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, animation_header: Unified_Animation_Header
) -> Control_Maps:

	match game_version:
		case Game_Version.D1_DEV_ALPHA | Game_Version.D1_ROI:
			read_type = u8
		case Game_Version.D2_EOF | Game_Version.MARATHON:
			read_type = u16

	bitness = game_version.pointer_block_bitness()

	# static
	static_scale_control_map = Tag_Array[int](
		reader, animation_header.static_scale_control_map_pointer, read_type, endianness, bitness=bitness
	)
	static_rotation_control_map = Tag_Array[int](
		reader, animation_header.static_rotation_control_map_pointer, read_type, endianness, bitness=bitness
	)
	static_translation_control_map = Tag_Array[int](
		reader, animation_header.static_translation_control_map_pointer, read_type, endianness, bitness=bitness
	)
	# animated
	animated_scale_control_map = Tag_Array[int](
		reader, animation_header.animated_scale_control_map_pointer, read_type, endianness, bitness=bitness
	)
	animated_rotation_control_map = Tag_Array[int](
		reader, animation_header.animated_rotation_control_map_pointer, read_type, endianness, bitness=bitness
	)
	animated_translation_control_map = Tag_Array[int](
		reader, animation_header.animated_translation_control_map_pointer, read_type, endianness, bitness=bitness
  	)

	return Control_Maps(
		static_scale_control_map=static_scale_control_map,
		static_rotation_control_map=static_rotation_control_map,
		static_translation_control_map=static_translation_control_map,
		animated_scale_control_map=animated_scale_control_map,
		animated_rotation_control_map=animated_rotation_control_map,
		animated_translation_control_map=animated_translation_control_map
	)


def read_runtime_rig_components(
	reader: Binary_Reader, game_version: Game_Version,
	endianness: Endianness, pointer: Base_Tag_Pointer
) -> Tag_Array[Runtime_Rig_Component]:

	return Tag_Array[Runtime_Rig_Component](
		reader, pointer, Runtime_Rig_Component, endianness, bitness=game_version.pointer_block_bitness()
	)

def read_codec_header(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, pointer: Base_Tag_Pointer
) -> Unified_Codec_Common_Header | None:
	reader.seek(pointer.get_address())

	common_header = reader.read_struct(Codec_Common_Header, override_endianness=endianness).to_unified()
	version_map = CODEC_REGISTRY.get(game_version, CODEC_REGISTRY["DEFAULT"])

	if common_header.codec_type not in version_map:
		raise err.Unknown_Codec_Error(f"Unknown codec type {common_header.codec_type}")

	raw_class, unified_class = version_map[common_header.codec_type]

	return unified_class.from_parts(
		common_header,
		reader.read_struct(raw_class, override_endianness=endianness).to_unified()
	)

def read_codec_0_buffers(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, codec_header: Unified_Codec_0
) -> Codec_0_Buffers:
	bitness = game_version.pointer_block_bitness()
	animated_scale_stream = Tag_Array_NP(reader, codec_header.scale_stream_pointer, np.float32, endianness, bitness=bitness)
	animated_rotation_stream = Tag_Array_NP(reader, codec_header.rotation_stream_pointer, np.float32, endianness, 4, bitness=bitness)
	animated_translation_stream = Tag_Array_NP(reader, codec_header.translation_stream_pointer, np.float32, endianness, 4, bitness=bitness)

	return Codec_0_Buffers(animated_scale_stream, animated_rotation_stream, animated_translation_stream)


def read_codec_1_buffers(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, codec_header: Unified_Codec_1
) -> Codec_1_Buffers:
	bitness = game_version.pointer_block_bitness()
	uncompressed_data = Tag_Array_NP(reader, codec_header.uncompressed_data_pointer, np.int16, endianness, bitness=bitness)
	compressed_data = Tag_Array_NP(reader, codec_header.compressed_data_pointer, np.int16, endianness, bitness=bitness)
	keyframe_deltas = Tag_Array_NP(reader, codec_header.keyframe_deltas_pointer, np.uint8, endianness, bitness=bitness)
	interpolation_data = Tag_Array_NP(reader, codec_header.interpolation_data_pointer, np.uint8, endianness, bitness=bitness)
	quantization_minimums = Tag_Array_NP(reader, codec_header.quantization_minimums_pointer, np.float32, endianness, bitness=bitness)
	quantization_extents = Tag_Array_NP(reader, codec_header.quantization_extents_pointer, np.float32, endianness, bitness=bitness)
	array_7 = Tag_Array_NP(reader, codec_header.array_7_pointer, None, endianness, bitness=bitness)  # Array will decide type

	return Codec_1_Buffers(
		uncompressed_data,
		compressed_data,
		keyframe_deltas,
		interpolation_data,
		quantization_minimums,
		quantization_extents,
		array_7
	)


def read_codec_2_buffers(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, codec_header: Unified_Codec_2
) -> Codec_2_Buffers:
	bitness = game_version.pointer_block_bitness()
	stream_data = Tag_Array_NP(reader, codec_header.stream_data_pointer, np.uint16, endianness, bitness=bitness)
	quantization_minimums = Tag_Array_NP(reader, codec_header.quantization_minimums_pointer, np.float32, endianness, bitness=bitness)
	quantization_extents = Tag_Array_NP(reader, codec_header.quantization_extents_pointer, np.float32, endianness, bitness=bitness)

	return Codec_2_Buffers(stream_data, quantization_minimums, quantization_extents)


def read_codec_3_buffers(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness, codec_header: Unified_Codec_3
) -> Codec_3_Buffers:
	bitness = game_version.pointer_block_bitness()

	stream_data = Tag_Array_NP(reader, codec_header.stream_data_pointer, np.uint16, endianness, bitness=bitness)

	return Codec_3_Buffers(stream_data)

def read_codec_buffers(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness,
	codec_header: Unified_Codec_Common_Header | None
) -> Codec_Buffers_Union | None:
	if isinstance(codec_header, Unified_Codec_0):
		return read_codec_0_buffers(reader, game_version, endianness, codec_header)
	elif isinstance(codec_header, Unified_Codec_1):
		return read_codec_1_buffers(reader, game_version, endianness, codec_header)
	elif isinstance(codec_header, Unified_Codec_2):
		return read_codec_2_buffers(reader, game_version, endianness, codec_header)
	elif isinstance(codec_header, Unified_Codec_3):
		return read_codec_3_buffers(reader, game_version, endianness, codec_header)
	else:
		return None


def read_animation(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Animation_Data:
	# read general codec
	animation_header: Unified_Animation_Header = read_animation_header(reader, game_version, endianness)

	# parse control maps
	control_maps = read_control_maps(reader, game_version, endianness, animation_header)

	rig_components = read_runtime_rig_components(reader, game_version, endianness, animation_header.rig_components_array_pointer)

	# read static data header
	static_bones_header = None
	static_bones_buffers = None

	if not animation_header.static_bone_data_pointer.is_zero():
		static_bones_header = read_codec_header(reader, game_version, endianness, animation_header.static_bone_data_pointer)

		if static_bones_header is not None:
			if static_bones_header.codec_type != 3:
				raise err.Unknown_Codec_Error(f"Static codec {static_bones_header.codec_type} is not supported")

			static_bones_buffers = read_codec_buffers(reader, game_version, endianness, static_bones_header)

	animated_bones_header = None
	animated_bones_buffers = None

	if not animation_header.animated_bone_data_pointer.is_zero():
		# read animated data header
		animated_bones_header = read_codec_header(reader, game_version, endianness, animation_header.animated_bone_data_pointer)

		if animated_bones_header is not None:
			if animated_bones_header.codec_type > 3 or animated_bones_header.codec_type < 0:
				raise err.Unknown_Codec_Error(f"Animated codec {animated_bones_header.codec_type} is not supported")

			animated_bones_buffers = read_codec_buffers(reader, game_version, endianness, animated_bones_header)

	return Animation_Data(
		animation_header,
		static_bones_header,
		static_bones_buffers,
		animated_bones_header,
		animated_bones_buffers,
		control_maps,
		rig_components
	)