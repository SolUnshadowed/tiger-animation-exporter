from dataclasses import dataclass
from enum import IntEnum
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QApplication,  QHBoxLayout, QLabel,
	QListView, QComboBox
)
from PySide6.QtCore import Signal, Qt

from gui.style.lists import list_style, search_style
from gui.worker_types import Tag_Model


class SORT_FIELD(IntEnum):
	NUMBER = 0
	SIZE = 1


class SORT_TYPE(IntEnum):
	ASC = 0
	DESC = 1


@dataclass(slots=True)
class Sort_Params:
	field: SORT_FIELD
	type: SORT_TYPE


class Tag_List_Widget(QWidget):
	tag_selected = Signal("quint32")
	format: str
	raw_tags: list[Tag_Model]
	searchbar: QLineEdit
	sort_label: QLabel
	list_view: QListWidget
	sort_combo: QComboBox

	def __init__(self, parent=None, fmt=""):
		super().__init__(parent)
		self.format = fmt

		self.searchbar = QLineEdit()
		self.searchbar.setPlaceholderText("Filter by handle")
		self.list_view = QListWidget()
		self.sort_label = QLabel("Sort by:")


		self.list_view.setStyleSheet(list_style)
		self.searchbar.setStyleSheet(search_style)
		self.sort_combo = QComboBox()
		self.sort_combo.addItem("id (asc)", userData=Sort_Params(SORT_FIELD.NUMBER, SORT_TYPE.ASC))
		self.sort_combo.addItem("id (desc)", userData=Sort_Params(SORT_FIELD.NUMBER, SORT_TYPE.DESC))
		self.sort_combo.addItem("size (asc)", userData=Sort_Params(SORT_FIELD.SIZE, SORT_TYPE.ASC))
		self.sort_combo.addItem("size (desc)", userData=Sort_Params(SORT_FIELD.SIZE, SORT_TYPE.DESC))
		self.sort_combo.setStyleSheet(
		"""
		QComboBox {
			border: 1px solid black;
			padding: 0 5px;
		}
		QComboBox::drop-down {
			border: none;
			background: transparent;
		}
		QComboBox::down-arrow {
			image: none;
		}
		"""
		)

		layout = QVBoxLayout(self)

		search_layout = QHBoxLayout()
		search_layout.addWidget(self.searchbar)
		search_layout.addWidget(self.sort_label)
		search_layout.addWidget(self.sort_combo)

		layout.addLayout(search_layout)

		layout.addWidget(self.list_view)

		self.searchbar.textChanged.connect(self._apply_filter_and_sort)
		self.sort_combo.currentIndexChanged.connect(self._apply_filter_and_sort)
		self.list_view.itemClicked.connect(self._on_item_clicked)

		self._raw_tags = []

	def set_tags(self, tags: list[Tag_Model]):
		self._raw_tags = tags
		self._apply_filter_and_sort()
		#self._update_display_list(self._raw_tags)

	def _apply_filter_and_sort(self):
		filter_text = self.searchbar.text().strip().lower()
		sort_data = self.sort_combo.currentData()
		sort_field = sort_data.field
		sort_type = sort_data.type

		if not filter_text.strip():
			filtered = list(self._raw_tags)
		else:
			query = filter_text.lower()
			filtered = [p for p in self._raw_tags if query in str(hex(p.handle)).lower()]

		filtered.sort(
			key=lambda item: item.number if sort_field is SORT_FIELD.NUMBER else item.size,
			reverse=(sort_type is SORT_TYPE.DESC)
		)

		self._update_display_list(filtered)

	def _update_display_list(self, packages: list[Tag_Model]):
		self.list_view.clear()

		for tag in packages:
			item = QListWidgetItem(tag.to_line(self.format))
			item.setData(Qt.UserRole, tag.handle)
			self.list_view.addItem(item)

	def _on_item_clicked(self, item: QListWidgetItem):
		tag_handle = item.data(Qt.UserRole)

		self.tag_selected.emit(tag_handle)