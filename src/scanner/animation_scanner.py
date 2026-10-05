import sys
import time
import pickle
import logging

from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from libs.tiger_pkg.manager.package_manager import Package_Manager, game_version_to_package
from libs.tiger_pkg.packages import exceptions as package_err
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.tag_handle import Tag_Handle
from libs.tiger_pkg.packages.package_path import Package_Path

from libs.binary_reader import Binary_Reader, u32

from src.tag_readers.animation.read_animation import read_animation_header, read_runtime_rig_components
from src.tag_readers.s_pattern.read_s_pattern import read_s_pattern
from src.tag_readers.s_pattern_component.read_s_pattern_component import read_s_pattern_component_header

from src.scanner.classes import (
	s_animation_clip_refs, s_pattern_component_refs,
	s_skeleton_spec_secondary_classes, s_runtime_rig_configuration_spec_secondary_classes,
	s_pattern_refs
)
from src.scanner.animations_prefix_tree import Animation_Prefix_Tree, Animation_Scan


logger = logging.getLogger(__name__)


CACHE_VERSION = 1
CACHE_FILE_NAME_TEMPLATE = "animations_cache_{}.bin"


@dataclass(slots=True)
class Package_Scan_Result:
	package_id: int
	animations: list[Animation_Scan]
	rigs: set[int]
	skeletons: set[int]
	entities: list[int]


@dataclass(slots=True)
class Entity_Scan:
	skeleton_tag_handle: Tag_Handle
	rig_tag_handle: Tag_Handle


@dataclass(slots=True)
class Animation_Cache:
	version: int
	timestamp: int
	prefix_tree: Animation_Prefix_Tree
	entities: dict[int, Entity_Scan]


def _process_single_package(args: tuple[int, Package_Path, Game_Version]) -> Package_Scan_Result:
	package_id, package_path, version = args
	package = game_version_to_package[version](package_path.to_str())

	s_animation_clip_ref = s_animation_clip_refs[version]
	animations = package.get_all_by_reference(s_animation_clip_ref)

	animation_scans = []

	for entry_id, entry_header in animations:
		handle = Tag_Handle.new(package_id, entry_id)

		try:
			reader = Binary_Reader(package.read_entry(entry_id))

			animation_header = read_animation_header(reader, version, package.endianness)
			components = read_runtime_rig_components(reader, version, package.endianness, animation_header.rig_components_array_pointer)

			animation_scans.append(
				Animation_Scan(
					handle.value,
					[component.hash for component in components]
				)
			)
		except package_err.Package_Decrypt_Error as e:  # if fails same as if it never existed
			logger.debug(f"Failed to read redacted animation: {handle}")

	s_pattern_component_ref = s_pattern_component_refs[version]
	rigs = set()
	skeletons = set()

	patterns_components = package.get_all_by_reference(s_pattern_component_ref)

	for entry_id, entry_header in patterns_components:
		if entry_header.reference == s_pattern_component_ref:  # if it is pattern component
			try:
				component_reader = Binary_Reader(package.read_entry(entry_id))

				component_header = read_s_pattern_component_header(component_reader, version, package.endianness)

				component_reader.seek(component_header.default_instance_pointer.get_address() - 4)

				val = u32.read_from(component_reader, package.endianness)

				if val == s_runtime_rig_configuration_spec_secondary_classes[version]:
					rigs.add(Tag_Handle.new(package_id, entry_id).value)

				if val == s_skeleton_spec_secondary_classes[version]:
					skeletons.add(Tag_Handle.new(package_id, entry_id).value)

			except package_err.Package_Decrypt_Error as e: # if fails same as if it never existed
				logger.debug(f"Failed to read redacted pattern component: {Tag_Handle.new(package_id, entry_id)}")

	s_pattern_ref = s_pattern_refs[version]
	patterns = package.get_all_by_reference(s_pattern_ref)

	package.close() # to release file

	return Package_Scan_Result(
		package_id,
		animation_scans,
		rigs,
		skeletons,
		[
			Tag_Handle.new(package_id, entry_id).value for entry_id, _ in patterns
		]
	)


class Animation_Scanner:
	cache: Animation_Cache | None
	cache_path: Path
	manager: Package_Manager


	def __init__(self, manager: Package_Manager, cache_path: Path):
		self.manager = manager
		self.cache_path = cache_path

		self.cache = self.read_animations_cache()

		if (
			self.cache is None or
			self.cache.version != CACHE_VERSION or
			self.cache.timestamp != int(manager.package_directory.stat().st_mtime)
		):
			self.cache = self.build_animations_cache()
			self.write_animations_cache()

	def build_animations_cache(self) -> Animation_Cache:
		start_time = time.time()
		# scan animations in process pool
		tasks = [
			(package_id, package_path, self.manager.version)
			for package_id, package_path in self.manager.package_paths.items()
		]

		all_animations = []
		all_skeletons = set()
		all_rigs = set()
		all_entities = []

		total = len(tasks)

		with ThreadPoolExecutor() as executor:
			future_to_task = {
				executor.submit(_process_single_package, task): task
				for task in tasks
			}

			for progress, future in enumerate(as_completed(future_to_task), 1):
				package_id, package_path, version = future_to_task[future]

				res = future.result()
				if res is not None:
					all_animations.extend(res.animations)
					all_entities.extend(res.entities)
					all_skeletons.update(res.skeletons)
					all_rigs.update(res.rigs)

					logger.info(f"Scanned {package_path.filename} ({progress} / {total})")
					logger.info(f"Animations: {len(res.animations)}, Skeletons: {len(res.skeletons)}, Rigs: {len(res.rigs)}, Entities: {len(res.entities)}")

		logger.info(f"Total: Animations: {len(all_animations)}, Skeletons: {len(all_skeletons)}, Rigs: {len(all_rigs)}, Entities: {len(all_entities)}")

		game_version = self.manager.version
		entities_with_skeleton_rig = dict()

		for i in range(len(all_entities)):
			entity_tag = Tag_Handle(all_entities[i])
			package = self.manager.get_or_load_pkg(entity_tag.package_id)
			endianness = package.endianness

			try:
				reader = Binary_Reader(self.manager.read_tag(entity_tag))

				pattern = read_s_pattern(reader, game_version, endianness)

				skeleton: Tag_Handle | None = None
				rig: Tag_Handle | None =  None

				for j in range(len(pattern.component_tag_handles)):
					component_tag = pattern.component_tag_handles[j]

					if component_tag.value in all_skeletons and skeleton is None:
						skeleton = component_tag

					if component_tag.value in all_rigs and rig is None:
						rig = component_tag

				if skeleton is not None and rig is not None:
					entities_with_skeleton_rig[all_entities[i]] = Entity_Scan(skeleton, rig)

			except package_err.Package_Decrypt_Error as e:
				logger.debug(f"Failed to read redacted entity {entity_tag}")
				continue

		logger.info(f"Total entities with skeleton and rig: {len(entities_with_skeleton_rig)}")

		trie = Animation_Prefix_Tree()

		for animation in all_animations:
			trie.add(animation)

		current_timestamp = int(self.manager.package_directory.stat().st_mtime)

		elapsed = time.time() - start_time
		logger.info(f"Built lookup cache for {len(all_animations)} animations in {elapsed:.3f}s")

		return Animation_Cache(
			CACHE_VERSION,
			current_timestamp,
			trie,
			entities_with_skeleton_rig
		)

	def write_animations_cache(self) -> None:
		try:
			with open(self.cache_path / CACHE_FILE_NAME_TEMPLATE.format(self.manager.cache_key()), "wb") as f:
				pickle.dump(self.cache, f, protocol=pickle.HIGHEST_PROTOCOL)
		except Exception as e:
			logger.error(f"Failed to write cache: {e}")

	def read_animations_cache(self) -> Animation_Cache | None:
		try:
			with open(self.cache_path / CACHE_FILE_NAME_TEMPLATE.format(self.manager.cache_key()), "rb") as f:
				logger.info("Loading animations cache...")
				cache = pickle.load(f)
				logger.info("Animations cache loaded")
				return cache
		except FileNotFoundError:
			logger.error(f"Failed to locate cache file")
			return None
		except Exception as e:
			logger.error(f"Failed to read cache: {e}")
			return None
