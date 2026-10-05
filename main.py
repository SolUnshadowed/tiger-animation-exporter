import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication

import libs.tiger_pkg.oodle as oodle
import libs.tiger_pkg.manager.exceptions as manager_exceptions

from src.cli_parser import parse_cli_args

from gui.main_window import Main_Window
from gui.worker import Package_Worker
from gui.worker import Worker_Data, Export_Settings


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)


if __name__ == "__main__":

	try:
		arguments = parse_cli_args()
	except (FileNotFoundError, NotADirectoryError) as e:
		logger.error(e)
		sys.exit(1)

	project_directory = Path(__file__).resolve().parent

	# TODO: change init mechanism
	try:
		oodle.init([arguments.packages.parent / "bin" / "x64", project_directory])
	except oodle.Oodle_Error as e:
		logger.error(e)
		sys.exit(2)

	worker = Package_Worker(
		Export_Settings(
			arguments.name_convention,
			arguments.animation_space,
			arguments.export_target,
			arguments.json_indent
		)
	)

	app = QApplication(sys.argv)

	window = Main_Window(worker, project_directory)

	try:
		window.settings_emitter.emit(
			Worker_Data(
				cache_path=project_directory,
				packages_path=arguments.packages,
				game_version=arguments.version,
				platform=None
			)
		)
	except manager_exceptions.Package_Manager_Error as e:
		logger.info("Manager threw exception")
		logger.error(e)
		sys.exit(1)

	app.aboutToQuit.connect(window.shutdown)

	window.show()

	sys.exit(app.exec())
