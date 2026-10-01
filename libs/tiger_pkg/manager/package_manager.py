import json
import sys
import time
import pickle
import logging

from pathlib import Path
from dataclasses import dataclass, field, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed

from libs.progress import Progress
from libs.tiger_pkg.manager import exceptions as err
from libs.tiger_pkg.enums import Package_Platform
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.packages.package_path import Package_Path
from libs.tiger_pkg.packages.package_common import Unified_Entry_Header, Tag_Handle, Package, Package_Named_Tag_Entry
from libs.tiger_pkg.packages.d1_devalpha.package import Package_D1_DEVALPHA
from libs.tiger_pkg.packages.d1_roi.package import Package_D1_ROI
from libs.tiger_pkg.packages.d2_eof.package import Package_D2_EOF


logger = logging.getLogger(__name__)


PACKAGE_CACHE_FILE_NAME = "package_cache.json"
LOOKUP_CACHE_FILE_NAME_TEMPLATE = "lookup_cache_{}.bin"
LOOKUP_CACHE_MAGIC = b"TLC0" # to keep it different from tiger-pkg as it is in different format
CACHE_VERSION = 1
PROGRESS = Progress()


game_version_to_package: dict[Game_Version, type[Package]] = {
	Game_Version.D1_DEV_ALPHA: Package_D1_DEVALPHA,
	Game_Version.D1_ROI: Package_D1_ROI,
	Game_Version.D2_EOF: Package_D2_EOF,
	Game_Version.MARATHON: Package_D2_EOF
}


def form_cache_key(version: Game_Version, platform: Package_Platform):
	return f"{version.value}_{platform.fmt}"


@dataclass
class Path_Cache_Entry:
	timestamp: int
	version: Game_Version
	platform: Package_Platform
	base_path: str
	paths: dict[int, str]


@dataclass
class Hash_Table_Entry_Short:
	handle_32: Tag_Handle
	reference: Tag_Handle


@dataclass
class Tag_Lookup_Index:
	tag32_entries_by_pkg: dict[int, list[Unified_Entry_Header]]
	tag32_to_tag64: dict[int, int]
	tag64_entries: dict[int, Hash_Table_Entry_Short]
	named_tags: list[Package_Named_Tag_Entry]


@dataclass
class Path_Cache:
	cache_version: int = CACHE_VERSION
	versions: dict[str, Path_Cache_Entry] = field(default_factory=dict)  # version + platform key: entry


def _process_single_package(
	args: tuple[int, Package_Path, Game_Version]
) -> tuple[
	tuple[int, list[Unified_Entry_Header]],
	list[tuple[int, Hash_Table_Entry_Short]],
	list[Package_Named_Tag_Entry]
] | None:
	pkg_id, p_path, version = args
	package = game_version_to_package[version](p_path.to_str())
	entries = (package.package_id, list(package.get_entries()))
	#redaction_level = (pkg.pkg_id(), pkg.redaction_level()) # TODO

	hashes = [
		(
			hash_64.handle_64,
			Hash_Table_Entry_Short(
				handle_32=hash_64.handle_32,
				reference=hash_64.reference
			)
		)
		for hash_64 in package.get_hash64_table()
	]

	named_tags = package.get_named_tags()

	return entries, hashes, named_tags


class Package_Manager:
	package_directory: Path
	cache_directory: Path
	version: Game_Version
	platform: Package_Platform
	package_paths: dict[int, Package_Path]
	lookup: Tag_Lookup_Index
	packages: dict[int, Package]


	def __init__(
		self,
		version: Game_Version,
		platform: Package_Platform | None,
		package_directory: Path,
		cache_directory: Path
	) -> None:
		self.version = version
		self.package_directory = package_directory
		self.cache_directory = cache_directory
		self.packages = dict()

		packages: dict[int, str] | None = None

		PROGRESS.update(0, 0, "Loading path cache")
		logger.info("Loading path cache...")

		cache = self.read_package_cache()

		if cache is None:
			cache = Path_Cache(cache_version=CACHE_VERSION)

		valid_entry = self.find_valid_cache_entry(cache, platform)

		cache_up_to_date = False
		if valid_entry:
			PROGRESS.update(0, 0, "Path cache loaded")
			logger.info("Path cache loaded")
			packages = valid_entry.paths
			cache_up_to_date = True
		else:
			PROGRESS.update(0, 0, "Path cache is invalid or missing, creating new one")
			logger.info("Path cache is invalid or missing, creating new one")
			packages = self.scan_and_build_package_cache()

		self.package_paths = {
			package_id_int: Package_Path.parse_with_defaults(path)
			for package_id_int, path in packages.items()
		}

		if not self.package_paths:
			raise err.Package_Error("No packages found")

		first_path = next(iter(self.package_paths.values()))

		try:
			if valid_entry:
				platform = valid_entry.platform
			else:
				package = game_version_to_package[self.version](first_path.to_str())
				platform = package.platform
		except Exception as e:
			logger.error(e)
			raise err.Unexpected_Package_Platform("Unknown package platform")

		self.platform = platform

		if not valid_entry:
			try:
				timestamp = int(self.package_directory.stat().st_mtime)
			except OSError:
				timestamp = 0

			# add entry
			cache.versions[self.cache_key()] = Path_Cache_Entry(
				timestamp=timestamp,
				version=self.version,
				platform=self.platform,
				base_path=str(self.package_directory),
				paths={pkg_id: pkg_path for pkg_id, pkg_path in packages.items()}
			)

			PROGRESS.update(0, 0, "Path cache created")
			logger.info("Path cache created")

		if not cache_up_to_date:
			self.write_package_cache(cache)
			self.build_lookup_cache()
			self.write_lookup_cache()
		else:
			lookup_cache = self.read_lookup_cache()

			if lookup_cache:
				self.lookup = lookup_cache
			else:
				self.build_lookup_cache()
				self.write_lookup_cache()

		logger.info(f"Manager configured, Game: {self.version}, Platform: {self.platform.fmt}")

	def scan_and_build_package_cache(self) -> dict[int, str]:
		packages_all = []
		try:
			for entry in self.package_directory.iterdir():
				if entry.is_file() and entry.suffix.lower() == ".pkg":
					packages_all.append(entry.resolve())  # absolute path
		except OSError as e:
			raise err.Base_Directory_Error(f"Error reading directory: {e}")

		# key: (id_hex, language), value: (patch_number, package_id_int, full_path)
		latest_patch_for_file: dict[tuple[str, str | None], tuple[int, int, Path]] = {}

		for file_path in packages_all:
			name_without_ext = file_path.stem

			# with maxsplit=2
			# "w64_textures_01a2_en_0" -> ["w64_textures_01a2", "en", "0"]
			# "ps3_arch_fallen_0059_0.pkg" -> ["ps3_arch_fallen", "0059", "0"]
			# so -1 is patch, -2 is language or package_id, -3 is {platform}_{name}_{id} or {platform}_{name}
			parts = name_without_ext.rsplit('_', 2)
			if len(parts) < 3:
				logger.warning(f"Invalid packages name: {name_without_ext}, ignoring")
				continue

			base_or_id, lang_or_id, patch_str = parts[0], parts[1], parts[2]

			try:  # if patch is not a number we have a problem
				patch_number = int(patch_str)
			except ValueError:
				logger.warning(f"Invalid packages name: {name_without_ext}, ignoring")
				continue

			if len(lang_or_id) == 2:  # if len == 2 it is language | but jpn is 3 letters long....
				# id + language
				package_id = base_or_id.split('_')[-1]  # from "w64_textures_01a2" take "01a2"
				group_key = (package_id, lang_or_id)
			else:
				# languageless file
				package_id = lang_or_id
				group_key = (package_id, None)

			try:  # from hex str to int
				package_id_int = int(package_id, 16)
			except ValueError:
				logger.warning(f"Invalid packages name: {name_without_ext}, ignoring")
				continue

			if group_key not in latest_patch_for_file:
				latest_patch_for_file[group_key] = (patch_number, package_id_int, file_path)
			elif patch_number > latest_patch_for_file[group_key][0]:  # if patch is bigger
				latest_patch_for_file[group_key] = (patch_number, package_id_int, file_path)

		packages: dict[int, str] = {
			package_id_int: str(path)
			for _, package_id_int, path in latest_patch_for_file.values()
		}

		return packages

	def read_package_cache(self) -> Path_Cache | None:
		try:
			with open(self.cache_directory / PACKAGE_CACHE_FILE_NAME, "r", encoding="utf-8") as f:
				raw_data = json.load(f)

			if raw_data.get("cache_version") != CACHE_VERSION:
				return None

			cache = Path_Cache(cache_version=raw_data["cache_version"])
			for key, entry_dict in raw_data.get("versions", {}).items():
				paths: dict[int, str] = {
					int(package_id): path for package_id, path in entry_dict["paths"].items()
				}

				cache.versions[key] = Path_Cache_Entry(
					timestamp=entry_dict["timestamp"],
					version=Game_Version(entry_dict["version"]),
					platform=Package_Platform(entry_dict["platform"]),
					base_path=entry_dict["base_path"],
					paths=paths
				)
			return cache

		except OSError: # or could not read
			return None

	def write_package_cache(self, cache: Path_Cache) -> None:
		with open(self.cache_directory / PACKAGE_CACHE_FILE_NAME, "w", encoding="utf-8") as f:
			json.dump(asdict(cache), f, indent=2, ensure_ascii=False)

	def find_valid_cache_entry(self, cache: Path_Cache, platform: Package_Platform | None) -> Path_Cache_Entry | None:
		entry = self.get_paths(cache, self.version, platform, self.package_directory)
		if not entry:
			return None

		try:
			current_timestamp = int(self.package_directory.stat().st_mtime)
		except OSError:
			current_timestamp = 0

		if entry.timestamp < current_timestamp or Path(entry.base_path) != self.package_directory:
			return None

		return entry

	def get_paths(
		self, cache: Path_Cache, version: Game_Version, platform: Package_Platform | None, base_path: Path
	) -> Path_Cache_Entry | None:
		if platform is not None:
			return cache.versions.get(
				form_cache_key(version, platform)
			)

		matches = [cache_entry for cache_entry in cache.versions.values() if cache_entry.version == version]

		if len(matches) > 1:  # if base path is the same
			matches = [m for m in matches if Path(m.base_path) == base_path]

		if len(matches) > 1:  # if there are multiple matches but no platform
			raise ValueError(f"There is more than one cache entry for version '{version}', but no platform was given")

		return matches[0] if matches else None

	def build_lookup_cache(self) -> None:
		start_time = time.time()

		tasks = [
			(package_id, package_path, self.version)
			for package_id, package_path in self.package_paths.items()
		]

		tables = []
		total = len(tasks)

		with ProcessPoolExecutor() as executor:
			future_to_task = {
				executor.submit(_process_single_package, task): task
				for task in tasks
			}

			for progress, future in enumerate(as_completed(future_to_task), 1):
				package_id, package_path, version = future_to_task[future]

				res = future.result()

				PROGRESS.update(progress, total, f"Scanned package {package_path.filename} ({progress} / {total})")
				logger.info(f"Scanned {package_path.filename} ({progress} / {total})")

				if res is not None:
					tables.append(res)

		if not tables:
			logger.warning("No packages to build lookup cache.")
			return

		entries, hashes_flat, named_tags_flat = zip(*tables) # , redaction_levels_flat

		tag32_to_tag64 = {}
		tag64_entries = {}

		for package_hashes in hashes_flat:
			for h64, entry in package_hashes:
				tag32_to_tag64[entry.handle_32.value] = h64
				tag64_entries[h64] = entry

		self.lookup = Tag_Lookup_Index(
			tag32_entries_by_pkg=dict(entries),
			tag32_to_tag64=tag32_to_tag64,
			tag64_entries=tag64_entries,
			named_tags=[tag for sublist in named_tags_flat for tag in sublist],
			#redaction_levels=dict(redaction_levels_flat)
		)

		elapsed = time.time() - start_time
		logger.info(f"Built lookup cache for {len(self.lookup.tag32_entries_by_pkg)} packages in {elapsed:.3f}s")

	def read_lookup_cache(self) -> Tag_Lookup_Index | None:
		try:
			with open(self.cache_directory / LOOKUP_CACHE_FILE_NAME_TEMPLATE.format(self.cache_key()), "rb") as f:
				magic = f.read(4)

				if magic != LOOKUP_CACHE_MAGIC:
					logger.info("Invalid lookup cache magic")
					return None

				PROGRESS.update(0, 0, "Loading index cache")
				logger.info("Loading index cache")

				cache = pickle.load(f)

				PROGRESS.update(0, 0, "Index cache loaded")
				logger.info("Index cache loaded")
				return cache

		except FileNotFoundError:
			return None

		except Exception as e:
			logger.error(f"Failed to read cache: {e}")
			return None

	def write_lookup_cache(self) -> None:
		try:
			with open(self.cache_directory / LOOKUP_CACHE_FILE_NAME_TEMPLATE.format(self.cache_key()), "wb") as f:
				PROGRESS.update(0, 0, "Writing lookup cache")
				logger.info("Writing lookup cache")

				f.write(LOOKUP_CACHE_MAGIC)
				pickle.dump(self.lookup, f, protocol=pickle.HIGHEST_PROTOCOL)

				PROGRESS.update(0, 0, "Lookup cache written")
				logger.info("Lookup cache written")

		except Exception as e:
			logger.error(f"Failed to write cache: {e}")

	def get_or_load_pkg(self, package_id: int) -> Package:
		package = self.packages.get(package_id)

		if package is None:
			package_path = self.package_paths.get(package_id)

			if not package_path:
				raise err.Package_Error(f"Couldn't get a path for packages id {package_id:04x}")
			try:
				package = game_version_to_package[self.version](package_path.to_str())
			except Exception as e:
				raise err.Package_Error(f"Failed to open packages '{package_path.filename}'") from e

			self.packages[package_id] = package

		return package

	def read_tag(self, tag: Tag_Handle | int) -> bytes:
		handle = tag if isinstance(tag, Tag_Handle) else Tag_Handle(tag)

		package = self.get_or_load_pkg(handle.package_id)
		return package.read_entry(handle.entry_index)

	def get_entry(self, tag: Tag_Handle | int) -> Unified_Entry_Header :
		handle = tag if isinstance(tag, Tag_Handle) else Tag_Handle(tag)

		return self.lookup.tag32_entries_by_pkg[handle.package_id][handle.entry_index]

	def get_entry_package_index(self, package_id: int, entry_index: int) -> Unified_Entry_Header:
		handle = Tag_Handle.new(package_id, entry_index)

		return self.get_entry(handle)

	def get_all_by_reference(self, ref: int) -> list[tuple[Tag_Handle, Unified_Entry_Header]]:
		return [
			(Tag_Handle.new(package_id, index), entry)
			for package_id, entries in self.lookup.tag32_entries_by_pkg.items()
			for index, entry in enumerate(entries)
			if entry.reference == ref
		]

	def get_named_tag(self, name: str) -> Tag_Handle | None:
		for tag in self.lookup.named_tags:
			if tag.name == name:
				return tag.handle

		return None

	def cache_key(self) -> str:
		return form_cache_key(self.version, self.platform)
