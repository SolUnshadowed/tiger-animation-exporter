from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, Endianness, u16, f32
from src.tag_readers.animation.unified_structures import Unified_Codec_Common_Header


@binary_struct(size=16)
@dataclass(slots=True)
class Codec_Common_Header:
	codec_type: Annotated[int, u16, Endianness.LE]  # codec type is in Little-endian always
	scale_stream_count: Annotated[int, u16]
	rotation_stream_count: Annotated[int, u16]
	translation_stream_count: Annotated[int, u16]
	prob_error_value: Annotated[int, f32]
	prob_compression_rate: Annotated[int, f32]

	def to_unified(self) -> Unified_Codec_Common_Header:
		return Unified_Codec_Common_Header(
			codec_type=self.codec_type,
			scale_stream_count=self.scale_stream_count,
			rotation_stream_count=self.rotation_stream_count,
			translation_stream_count=self.translation_stream_count,
			prob_error_value=self.prob_error_value,
			prob_compression_rate=self.prob_compression_rate
		)


