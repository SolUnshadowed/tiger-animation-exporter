from dataclasses import dataclass

from libs.binary_reader import Binary_Reader, Endianness, binary_struct
from libs.tag.tag_pointers import Base_Tag_Pointer
from libs.tiger_pkg.game_version import Game_Version
from libs.tag.tag_array import Tag_Array

from src.tag_readers.s_entity_model.d1_devalpha_structures import (
	S_Entity_Model_Header_D1_DEVALPHA, S_Entity_Model_Mesh_D1_DEVALPHA,
	S_Render_Model_Mesh_Part_D1_DEVALPHA
)
from src.tag_readers.s_entity_model.d1_roi_structures import (
	S_Entity_Model_Mesh_D1_ROI, S_Entity_Model_Header_D1_ROI,
)
from src.tag_readers.s_entity_model.unified_structures import (
	Unified_S_Entity_Model_Header, Unified_S_Entity_Model_Mesh,
	Unified_Model_Mesh_Part
)


@dataclass
class Mesh_Additional_Data:
	index_buffer_element_length: int


@dataclass
class Entity_Mesh_Data:
	header: Unified_S_Entity_Model_Header
	meshes: list[Unified_S_Entity_Model_Mesh]
	parts: list[list[Unified_Model_Mesh_Part]]
	additional_mesh_data: list[Mesh_Additional_Data]


def read_s_entity_model_header(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Unified_S_Entity_Model_Header:
	reader.seek(0)

	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return reader.read_struct(S_Entity_Model_Header_D1_DEVALPHA, override_endianness=endianness).to_unified()
		case Game_Version.D1_ROI:
			return reader.read_struct(S_Entity_Model_Header_D1_ROI, override_endianness=endianness).to_unified()
		case _:
			raise NotImplementedError("s_entity_model_header is d1 devalpha only")


def read_s_entity_model_meshes(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness,
	pointer: Base_Tag_Pointer
) -> list[Unified_S_Entity_Model_Mesh]:
	match game_version:
		case Game_Version.D1_DEV_ALPHA:
			return [
				mesh.to_unified()
				for mesh in Tag_Array[S_Entity_Model_Mesh_D1_DEVALPHA](
					reader, pointer, S_Entity_Model_Mesh_D1_DEVALPHA, endianness, bitness=game_version.pointer_block_bitness()
				)
			]
		case Game_Version.D1_ROI:
			return [
				mesh.to_unified()
				for mesh in Tag_Array[S_Entity_Model_Mesh_D1_ROI](
					reader, pointer, S_Entity_Model_Mesh_D1_ROI, endianness,
					bitness=game_version.pointer_block_bitness()
				)
			]
		case _:
			raise NotImplementedError("s_entity_model_meshes are d1 devalpha only")


def read_parts(
	reader: Binary_Reader, game_version: Game_Version, endianness: Endianness,
	meshes: list[Unified_S_Entity_Model_Mesh]
) -> list[list[Unified_Model_Mesh_Part]]:
	parsed_parts = []

	for mesh in meshes:
		match game_version:
			case Game_Version.D1_DEV_ALPHA | Game_Version.D1_ROI:
				mesh_parts = Tag_Array[S_Render_Model_Mesh_Part_D1_DEVALPHA](
					reader, mesh.parts_pointer, S_Render_Model_Mesh_Part_D1_DEVALPHA,
					endianness, bitness=game_version.pointer_block_bitness()
				)

				parsed_parts.append(
					[
						part.to_unified()
						for part in mesh_parts
					]
				)
			case _:
				raise NotImplementedError("read_parts are d1 devalpha only")

	return parsed_parts


def read_s_entity_model(reader: Binary_Reader, game_version: Game_Version, endianness: Endianness) -> Entity_Mesh_Data:
	header = read_s_entity_model_header(reader, game_version, endianness)

	meshes = read_s_entity_model_meshes(reader, game_version, endianness, header.s_entity_model_mesh_array_pointer)

	meshes_parts = read_parts(reader, game_version, endianness, meshes)

	additional_data = []

	for index, mesh in enumerate(meshes):
		mesh_parts = meshes_parts[index]
		index_buffer_element_length = 0

		for part in mesh_parts:
			t = part.index_offset + part.index_count
			if t > index_buffer_element_length:
				index_buffer_element_length = t

		additional_data.append(Mesh_Additional_Data(index_buffer_element_length))

	return Entity_Mesh_Data(
		header,
		meshes,
		meshes_parts,
		additional_data
	)
