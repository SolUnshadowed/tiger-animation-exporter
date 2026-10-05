import json

from fnv_hashes.bones_names import hash_to_bungie_name
from tag_readers.skeleton.read_skeleton import Skeleton


def create_api_like_skeleton(skeleton_data: Skeleton):
	nodes = []

	for node_def in skeleton_data.node_defs:

		res = {
			"name": {
				"hash": node_def.bone_hash,
				"string":  hash_to_bungie_name[node_def.bone_hash] if node_def.bone_hash in hash_to_bungie_name else "???"
			},
			"parent_node_index": node_def.parent_node_index,
			"first_child_node_index": node_def.first_child_node_index,
			"next_sibling_node_index": node_def.next_sibling_node_index,
		}

		nodes.append(res)

	default_object_space_transforms = []

	for node_def in skeleton_data.default_obj_space_tr:
		default_object_space_transforms.append(node_def)

	default_inverse_object_space_transforms = []

	for node_def in skeleton_data.default_inv_obj_space_tr:
		default_inverse_object_space_transforms.append(node_def)

	return {
		"definition": {
			"nodes": nodes,
			"default_object_space_transforms": default_object_space_transforms,
			"default_inverse_object_space_transforms": default_inverse_object_space_transforms
		}
	}


def save_api_like_skeleton(file_name, data):
	with open(file_name, "w") as json_file:
		json.dump(data, json_file, indent=2)
