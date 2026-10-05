from PySide6.QtWidgets import (
	QWidget, QVBoxLayout,  QLabel
)
from PySide6.QtCore import Slot, Qt
from gui.worker_types import Entity_Data

class Entity_Title(QWidget):
	tag_label: QLabel
	package_label: QLabel

	def __init__(self, parent=None):
		super().__init__(parent)

		layout = QVBoxLayout(self)

		self.tag_label = QLabel("Tag: ")
		self.tag_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
		self.package_label = QLabel("Package: ")
		self.package_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

		layout.addWidget(self.tag_label)
		layout.addWidget(self.package_label)

	@Slot(object)
	def set_data(self, data: Entity_Data):
		self.tag_label.setText(f"Tag: {data.entity_handle_int:X}")
		self.package_label.setText(f"Package: {data.package_name}")
