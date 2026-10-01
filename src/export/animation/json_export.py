import logging
import jsonpickle

from dataclasses import dataclass
from typing import TypedDict

from src.tag_readers.animation.read_animation import Animation_Data
from src.decode_animation.decode_animation import Bone_Tracks, Bone_Track_Dict

logger = logging.getLogger(__name__)


@dataclass
class Runtime_Rig_Component_Dict:
	hash: int
	control_count: int


class Animation_Json(TypedDict):
	bone_tracks: list[Bone_Track_Dict]
	frame_count: int
	node_count: int
	rig_control_count: int
	static_codec_type: int
	animated_codec_type: int
	rig_components: list[Runtime_Rig_Component_Dict]


def add_animation_to_json(
	animations_list: list[Animation_Json],
	animation_data: Animation_Data,
	bone_tracks: list[Bone_Tracks] | list[Bone_Tracks | None]
):
	result = Animation_Json(
		bone_tracks= [
			track.to_typed_dict()
			if track is not None
			else
			Bone_Track_Dict(
				scales=[],
				rotations=[],
				translations=[],
				bone_name_hash=-1
			)
			for track in bone_tracks
		],
		frame_count=animation_data.animation_header.frame_count,
		node_count=animation_data.animation_header.node_count,
		rig_control_count=animation_data.animation_header.rig_control_count,
		static_codec_type=animation_data.static_bones_header.codec_type if animation_data.static_bones_header is not None else -1,
		animated_codec_type=animation_data.animated_bones_header.codec_type if animation_data.animated_bones_header is not None else -1,
		rig_components=[
			Runtime_Rig_Component_Dict(component.hash, component.control_count)
			for component in animation_data.runtime_rig_components
		],
	)

	animations_list.append(result)


def write_json_file(file_name, data, selected_json_indent):
	with open(file_name, "w") as json_file:
		json_file.write(jsonpickle.encode(data, indent=selected_json_indent))
		logger.info(f"Saved json file as {file_name}")
