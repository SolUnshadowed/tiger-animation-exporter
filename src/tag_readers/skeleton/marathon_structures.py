from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, L_Padding
from libs.tag.tag_pointers import Vec_Pointer_64
from src.tag_readers.skeleton.unified_structures import Unified_Skeleton_Main_Struct


@binary_struct(size=240)
@dataclass
class MARATHON_Skeleton_Main_Struct:
	bone_hierarchy_pointer: Annotated[Vec_Pointer_64, L_Padding(192)]
	obj_space_tr_pointer: Vec_Pointer_64
	inv_obj_space_tr_pointer: Vec_Pointer_64

	def to_unified(self) -> Unified_Skeleton_Main_Struct:
		return Unified_Skeleton_Main_Struct(
			bone_hierarchy_pointer=self.bone_hierarchy_pointer,
			obj_space_tr_pointer=self.obj_space_tr_pointer,
			inv_obj_space_tr_pointer=self.inv_obj_space_tr_pointer
		)
