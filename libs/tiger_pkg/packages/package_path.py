from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class Package_Path:
	platform: str
	name: str
	id: str
	patch: int
	path: Path
	filename: str
	language: Optional[str] = None

	@staticmethod
	def parse(base_path: str) -> Optional["Package_Path"]:
		path = Path(base_path)
		path_filename = path.name
		if not path_filename:
			return None

		parts = path_filename.split('_')
		if len(parts) < 4:
			return None

		platform = parts[0]

		name = "_".join(parts[1:-2])
		pkg_id = parts[-2]
		language = None

		if len(pkg_id) == 2:
			language = pkg_id
			name = "_".join(parts[1:-3])
			pkg_id = parts[-3]

		patch_part = parts[-1].split('.')[0]
		try:
			patch = int(patch_part)
		except ValueError:
			return None


		return Package_Path(
			platform=platform,
			name=name,
			language=language,
			id=pkg_id,
			patch=patch,
			path=path,
			filename=path_filename
		)

	@classmethod
	def parse_with_defaults(cls, base_path: str) -> "Package_Path":
		parsed = cls.parse(base_path)
		if parsed is not None:
			return parsed

		path = Path(base_path)
		path_filename = path.name
		return cls(
			platform="unknown",
			name="unknown",
			id="unknown",
			patch=0,
			path=path,
			filename=path_filename,
			language=None
		)

	def to_str(self) -> str:
		return str(self.path)
