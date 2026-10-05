from dataclasses import dataclass, field

@dataclass(slots=True)
class Animation_Scan:
	animation_tag: int
	rig_component_hashes: list[int]


@dataclass(slots=True)
class Prefix_Node:
	children: dict[int, int] = field(default_factory=dict)
	animation_handles: list[int] = field(default_factory=list)


class Animation_Prefix_Tree:
	nodes: list[Prefix_Node]

	def __init__(self):
		# node 0 is root
		self.nodes: list[Prefix_Node] = [
			Prefix_Node()
		]

	def add(self, anim: Animation_Scan):
		node_index = 0

		for component_hash in anim.rig_component_hashes:
			node = self.nodes[node_index]

			child_index = node.children.get(component_hash)

			if child_index is None:
				child_index = len(self.nodes)
				node.children[component_hash] = child_index
				self.nodes.append(Prefix_Node())

			node_index = child_index

		self.nodes[node_index].animation_handles.append(anim.animation_tag)


	def find_full(self, components: list[int]) -> list[int]:
		node_index = 0

		for component in components:
			node = self.nodes[node_index]

			if component not in node.children:
				return []

			node_index = node.children[component]

		return self.nodes[node_index].animation_handles


	def find_matching_prefixes(self, components: list[int]) -> list[int]:
		matched_handles = []
		node_index = 0

		for component in components:
			node = self.nodes[node_index]

			if component not in node.children:
				break

			node_index = node.children[component]
			current_node = self.nodes[node_index]

			if current_node.animation_handles:
				matched_handles.extend(current_node.animation_handles)

		return matched_handles

	def find_with_subtrees(self, components: list[int]) -> list[int]:
		matched_handles = set()
		node_index = 0

		for component in components:
			node = self.nodes[node_index]

			if component not in node.children:
				break

			node_index = node.children[component]

			stack = [node_index]
			while stack:
				current_index = stack.pop()
				current_node = self.nodes[current_index]

				if current_node.animation_handles:
					matched_handles.update(current_node.animation_handles)

				for child_index in current_node.children.values():
					stack.append(child_index)

		return list(matched_handles)



