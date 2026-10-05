from typing import Annotated
from dataclasses import dataclass

from libs.binary_reader import binary_struct, L_Padding
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tag.tag_pointers import Vec_Pointer_32

from src.tag_readers.s_dynamic_model_component.unified_structures import Unified_Dynamic_Model_Component


@binary_struct()
@dataclass
class Dynamic_Model_Component_Main_Struct_D1_DEVALPHA:
	entity_model_handle: Annotated[Tag_Handle, L_Padding(0x138)]

	#external_materials_map: Annotated[Vec_Pointer_32, L_Padding()]

	#external_materials: Annotated[Vec_Pointer_32, L_Padding()]

	def to_unified(self):
		return Unified_Dynamic_Model_Component(self.entity_model_handle)
