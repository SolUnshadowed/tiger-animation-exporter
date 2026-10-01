from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QSplitter
)
from PySide6.QtCore import Qt
from gui.tabs.packages.package_list import Package_List_Widget
from gui.tabs.packages.tag_list import Tag_List_Widget


class Packages_Page(QWidget):
	package_list: Package_List_Widget
	entities_list: Tag_List_Widget

	def __init__(self, parent=None):
		super().__init__(parent)

		layout = QVBoxLayout(self)

		self.package_list = Package_List_Widget()
		self.entities_list = Tag_List_Widget()

		splitter = QSplitter(Qt.Orientation.Horizontal)

		splitter.addWidget(self.package_list)
		splitter.addWidget(self.entities_list)
		layout.addWidget(splitter)
