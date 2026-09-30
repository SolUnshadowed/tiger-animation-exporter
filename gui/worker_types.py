import numpy as np

from dataclasses import dataclass

from src.decode_animation.decode_animation import Bone_Tracks
from src.tag_readers.animation.read_animation import Animation_Data
from src.tag_readers.skeleton.read_skeleton import Skeleton


@dataclass(slots=True)
class Package_Model:
	id: int
	name: str

	def id_to_hex(self):
		return "{:04x}".format(self.id)

	def to_line(self) -> str:
		return "{}: {}".format(self.id_to_hex(), self.name)


@dataclass(slots=True)
class Tag_Model:
	handle: int
	size: int
	ref: int
	number: int

	@staticmethod
	def size_to_human(size) -> str:
		if size < 1024:
			return "{:.2f} B".format(size)
		elif size < 1048576:
			return "{:.2f} KB".format(size / 1024)
		elif size < 1073741824:
			return "{:.2f} MB".format(size / 1048576)
		else:
			return "{:.2f} GB".format(size / 1073741824)

	def to_line(self, fmt: str='') -> str:
		if fmt == "handle_and_size":
			return "{:08X} ({})".format(self.handle, self.size_to_human(self.size))

		if fmt == "no_number":
			return "{:08X} (ref {:X})\n({})".format(self.handle, self.ref, self.size_to_human(self.size))

		return "{}: {:08X}\n(ref {:X})\n({})".format(self.number, self.handle, self.ref, self.size_to_human(self.size))


@dataclass(slots=True)
class Animation_Model:
	handle: int
	animation_data: Animation_Data
	tracks: list[Bone_Tracks]


@dataclass(slots=True)
class Model_Properties:
	scale: tuple[float, float, float]
	translation: tuple[float, float, float]
	position_buffer: np.ndarray
	normal_buffer: np.ndarray
	index_buffer: np.ndarray
	skin_weights: np.ndarray | None
	skin_indices: np.ndarray | None


@dataclass(slots=True)
class Render_Data:
	skeleton: Skeleton | None
	model_properties: list[None | Model_Properties]


@dataclass
class Entity_Data:
	entity_handle_int: int
	package_name: str
