from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QApplication,  QHBoxLayout, QLabel,
	QListView
)
from PySide6.QtCore import Signal, Qt

from gui.style.lists import list_style, search_style
from gui.worker_types import Package_Model


class Package_List_Widget(QWidget):
	package_selected = Signal(int)
	_raw_packages: list[Package_Model]

	def __init__(self, parent=None):
		super().__init__(parent)

		self.searchbar = QLineEdit()
		self.searchbar.setPlaceholderText("Filter packages")
		self.list_view = QListWidget()

		self.list_view.setStyleSheet(list_style)
		self.list_view.setSpacing(4)
		self.searchbar.setStyleSheet(search_style)

		layout = QVBoxLayout(self)

		search_layout = QHBoxLayout()
		search_layout.addWidget(self.searchbar)

		layout.addLayout(search_layout)

		layout.addWidget(self.list_view)

		self.searchbar.textChanged.connect(self._filter_list)
		self.list_view.itemClicked.connect(self._on_item_clicked)

		self._raw_packages = []

	def set_packages(self, packages: list[Package_Model]):
		self._raw_packages = packages
		self._update_display_list(self._raw_packages)

	def _filter_list(self, filter_text: str):
		if not filter_text.strip():
			filtered = self._raw_packages
		else:
			query = filter_text.lower()
			filtered = [p for p in self._raw_packages if query in p.name.lower()]

		self._update_display_list(filtered)

	def _update_display_list(self, packages: list[Package_Model]):
		self.list_view.clear()

		for package in packages:
			item = QListWidgetItem(package.to_line())
			item.setData(Qt.UserRole, package.id)
			self.list_view.addItem(item)

	def _on_item_clicked(self, item: QListWidgetItem):
		pkg_id = item.data(Qt.UserRole)

		self.package_selected.emit(pkg_id)
