import os
import argparse
from pathlib import Path
from dataclasses import dataclass

from libs.tiger_pkg.game_version import Game_Version
from src.export.animation_export.enums import Bone_Name_Convention, Animation_Space, Export_Target


@dataclass
class Arguments:
	version: Game_Version
	packages: Path
	json_indent: None | int
	name_convention: Bone_Name_Convention
	animation_space: Animation_Space
	export_target: Export_Target


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
	"-v", "--version",
	help="game version",
	type=str,
	choices=[c.value for c in Game_Version],
	required=True
)
parser.add_argument( "--packages", help="path to packages folder", required=True)
parser.add_argument(
	"-i", "--json-indent",
	help="number of spaces to use for JSON indentation",
	type=int,
	default=None,
)
parser.add_argument(
	"-t", "--target",
	help="export target",
	choices=[c.value for c in Export_Target],
	default=Export_Target.GLTF_RETARGET.value,
	type=str,
)
parser.add_argument(
	"--name-convention",
	help="bone name convention",
	choices=[c.value for c in Bone_Name_Convention],
	default=Bone_Name_Convention.FNV1BE.value,
	type=str,
)
parser.add_argument(
	"--animation-space",
	help="export animation space",
	type=str,
	choices=[c.value for c in Animation_Space],
	default=Animation_Space.LOCAL.value,
)


def parse_cli_args() -> Arguments:
	args = parser.parse_args()

	packages = Path(args.packages)

	if not packages.exists():
		raise FileNotFoundError(f"Directory does not exist: {packages}")

	if not packages.is_dir():
		raise NotADirectoryError(f"{packages} is not a directory")

	return Arguments(
		version=Game_Version(args.version),
		packages=packages,
		json_indent=args.json_indent,
		name_convention=Bone_Name_Convention(args.name_convention),
		animation_space=Animation_Space(args.animation_space),
		export_target=Export_Target(args.target),
	)


if __name__ == "__main__":
	print(parse_cli_args())