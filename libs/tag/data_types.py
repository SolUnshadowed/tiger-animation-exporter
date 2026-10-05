from dataclasses import dataclass
from typing import Annotated

from libs.binary_reader import binary_struct, Endianness, f32, u32, s32, Array


@binary_struct(size=8)
@dataclass(slots=True)
class Runtime_Rig_Component:
	hash: Annotated[int, u32]
	control_count: Annotated[int, u32, Endianness.LE]  # size is in Little-endian always for some reason


@binary_struct(size=32)
@dataclass(slots=True)
class Transform:
	r: Annotated[tuple[float, float, float, float], Array(f32, 4)]
	ts: Annotated[tuple[float, float, float, float], Array(f32, 4)]


@binary_struct(size=16)
@dataclass(slots=True)
class Skeleton_Node_Def:
	bone_hash: Annotated[int, u32]
	parent_node_index: Annotated[int, s32]
	first_child_node_index: Annotated[int, s32]
	next_sibling_node_index: Annotated[int, s32]


@binary_struct(size=8)
@dataclass(slots=True)
class Vec2:
	data: Annotated[tuple[float, float], Array(f32, 2)]

	@property
	def x(self) -> float:
		return self.data[0]

	@property
	def y(self) -> float:
		return self.data[1]

	def __iter__(self):
		return iter(self.data)

	def __len__(self):
		return 2

	def __getitem__(self, index):
		return self.data[index]


@binary_struct(size=16)
@dataclass(slots=True)
class Vec4:
	data: Annotated[tuple[float, float, float, float], Array(f32, 4)]

	@property
	def x(self) -> float:
		return self.data[0]

	@property
	def y(self) -> float:
		return self.data[1]

	@property
	def z(self) -> float:
		return self.data[2]

	@property
	def w(self) -> float:
		return self.data[3]

	def __iter__(self):
		return iter(self.data)

	def __len__(self):
		return 4

	def __getitem__(self, index):
		return self.data[index]

