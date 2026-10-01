from pathlib import Path

from PySide6.QtWidgets import (
	QWidget, QHBoxLayout, QTabWidget
)
from PySide6.QtCore import Signal, QThread, Slot

from gui.tabs.packages.packages_page import Packages_Page
from gui.tabs.entity.entity_page import Entity_Page
from gui.worker import Package_Worker
from gui.overlay import Loading_Overlay


class Main_Window(QWidget):
	tabs: QTabWidget
	packages_page: Packages_Page
	entity_page: Entity_Page
	overlay: Loading_Overlay

	cache_directory: Path
	worker: Package_Worker
	service_thread: QThread

	settings_emitter = Signal(object)
	request_package_list_emitter = Signal()
	exported_animation_emitter = Signal(list)

	def __init__(self, worker, cache_directory: Path):
		super().__init__()

		self.cache_directory = cache_directory
		self.setWindowTitle("Packages")

		self.setup_ui()
		self.init_service(worker)

	def setup_ui(self):
		self.overlay = Loading_Overlay(self)

		layout = QHBoxLayout(self)

		self.tabs = QTabWidget()

		self.packages_page = Packages_Page()
		self.tabs.addTab(self.packages_page , "Packages")

		self.entity_page = Entity_Page()
		self.tabs.addTab(self.entity_page, "Entity")

		layout.addWidget(self.tabs)


	def init_service(self, worker: Package_Worker):
		self.overlay.start_waiting("Starting")

		# create thread and move worker to it
		self.service_thread = QThread()
		self.worker = worker
		self.worker.moveToThread(self.service_thread)

		worker.loading_waiting.connect(self.overlay.start_waiting)  # passive mode
		worker.loading_progress.connect(self.overlay.start_polling)  # active polling mode
		worker.loading_hide.connect(self.overlay.hide_overlay) # hide

		self.worker.worker_started.connect(self.on_worker_update) # to turn off initial loadscreen

		self.request_package_list_emitter.connect(self.worker.get_packages_list)
		self.worker.package_list_ready_emitter.connect(self.packages_page.package_list.set_packages)
		self.worker.package_list_ready_emitter.connect(self.hide_initial_overlay)

		self.packages_page.package_list.package_selected.connect(self.worker.get_non_redacted_entities_for_package)
		self.worker.non_redacted_entities_for_package_ready_emitter.connect(self.packages_page.entities_list.set_tags)

		# list -> select entity
		self.packages_page.entities_list.tag_selected.connect(self.worker.select_entity)
		# worker -> get entity -> return skeleton and tags
		self.worker.entity_data_emitter.connect(self.entity_page.entity_title.set_data)
		self.worker.animations_list_emitter.connect(self.entity_page.animations_list.set_tags)
		self.worker.render_data_emitter.connect(self.entity_page.render.set_render_data)
		self.worker.render_data_emitter.connect(self.switch_tab_to_entity) # when entity is selected switch to its view

		self.entity_page.animations_list.tag_selected.connect(self.worker.get_gui_ready_animation)
		self.worker.gui_animation_data_emitter.connect(self.entity_page.set_animation)

		self.entity_page.render.animation_data.connect(self.update_animation_data)

		self.entity_page.export_button.clicked.connect(self.export_animation)
		self.exported_animation_emitter.connect(self.worker.export_animations)

		self.service_thread.start()

		self.settings_emitter.connect(self.worker.set_data)

	@Slot()
	def export_animation(self):
		selected_animations = self.entity_page.animations_list.selected_animations()

		self.exported_animation_emitter.emit(
			[
				animation.handle
				for animation in selected_animations
			]
		)

	@Slot(str)
	def update_animation_data(self, string: str):
		self.entity_page.stats_area.setPlainText(string)

	def switch_tab_to_entity(self):
		self.tabs.setCurrentIndex(1)

	@Slot(bool)
	def on_worker_update(self, status: bool):
		if status:
			self.request_package_list_emitter.emit()

	def hide_initial_overlay(self):
		self.overlay.hide_overlay()

	def closeEvent(self, event):
		self.entity_page.render.shutdown()
		self.service_thread.quit()
		self.service_thread.wait()
		event.accept()
