from dataclasses import dataclass

from libs.tag.tag_pointers import Base_Vec_Pointer

@dataclass
class Unified_Skeleton_Main_Struct:
	bone_hierarchy_pointer: Base_Vec_Pointer
	obj_space_tr_pointer: Base_Vec_Pointer
	inv_obj_space_tr_pointer: Base_Vec_Pointer