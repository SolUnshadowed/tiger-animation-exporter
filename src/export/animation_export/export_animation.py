import logging
import jsonpickle

from dataclasses import asdict

from src.tag_readers.animation.read_animation import Animation_Data
from src.decode_animation.decode_animation import Bone_Tracks

logger = logging.getLogger(__name__)


def animation_to_json(
	animation_data: Animation_Data, bone_tracks: list[Bone_Tracks] | list[Bone_Tracks | None]
) -> list[dict]:
	result = [
		{
			"bone_tracks": [
				{
					"scales": track.scales.tolist(),
					"rotations": track.rotations.tolist(),
					"translations": track.translations.tolist(),
					"bone_name_hash": track.bone_name_hash

				}
				if track is not None
				else
				{
					"scales": [],
					"rotations": [],
					"translations": [],
					"bone_name_hash": -1

				}
				for track in bone_tracks
			],
			"frame_count": animation_data.animation_header.frame_count,
			"node_count": animation_data.animation_header.node_count,
			"rig_control_count": animation_data.animation_header.rig_control_count,
			"static_codec_type": animation_data.static_bones_header.codec_type if animation_data.static_bones_header is not None else -1,
			"animated_codec_type": animation_data.animated_bones_header.codec_type if animation_data.animated_bones_header is not None else -1,
			"rig_components": [asdict(x) for x in animation_data.runtime_rig_components],
		}
	]

	return result


def write_json_file(file_name, data, selected_json_indent):
	with open(file_name, "w") as json_file:
		json_file.write(jsonpickle.encode(data, indent=selected_json_indent))
		logger.info(f"Saved json file as {file_name}")

