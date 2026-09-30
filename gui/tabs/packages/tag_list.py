from dataclasses import dataclass
from enum import IntEnum
from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QApplication,  QHBoxLayout, QLabel,
	QListView, QComboBox, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt, QModelIndex

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
		self.list_view.setSpacing(4)
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

		self.searchbar.textChanged.connect(self.apply_filter_and_sort)
		self.sort_combo.currentIndexChanged.connect(self.apply_filter_and_sort)
		self.list_view.itemClicked.connect(self.on_item_clicked)

		self.raw_tags = []

	def set_tags(self, tags: list[Tag_Model]):
		self.raw_tags = tags
		self.list_view.clearSelection()
		self.list_view.setCurrentIndex(QModelIndex())
		self.apply_filter_and_sort()

	def apply_filter_and_sort(self):
		filter_text = self.searchbar.text().strip().lower()
		sort_data = self.sort_combo.currentData()
		sort_field = sort_data.field
		sort_type = sort_data.type

		if not filter_text.strip():
			filtered = list(self.raw_tags)
		else:
			query = filter_text.lower()
			filtered = [p for p in self.raw_tags if query in str(hex(p.handle)).lower()]

		filtered.sort(
			key=lambda item: item.number if sort_field is SORT_FIELD.NUMBER else item.size,
			reverse=(sort_type is SORT_TYPE.DESC)
		)

		self.update_display_list(filtered)

	def update_display_list(self, packages: list[Tag_Model]):
		self.list_view.clear()

		for tag in packages:
			item = QListWidgetItem(tag.to_line(self.format))
			item.setData(Qt.UserRole, tag.handle)
			self.list_view.addItem(item)

	def on_item_clicked(self, item: QListWidgetItem):
		tag_handle = item.data(Qt.UserRole)

		self.tag_selected.emit(tag_handle)


class Animation_List_Widget(QWidget):
	tag_selected = Signal(object)
	selection_changed = Signal()
	searchbar: QLineEdit
	sort_label: QLabel
	list_view: QListWidget
	sort_combo: QComboBox

	raw_animations: list[Tag_Model]

	def __init__(self, parent=None):
		super().__init__(parent)

		self.raw_animations = []
		self.searchbar = QLineEdit()
		self.searchbar.setPlaceholderText("Filter by animation")
		self.searchbar.setStyleSheet(search_style)
		self.sort_label = QLabel("Sort by:")

		self.sort_combo = QComboBox()

		self.sort_combo.addItem("id (asc)", userData=Sort_Params(SORT_FIELD.NUMBER, SORT_TYPE.ASC))
		self.sort_combo.addItem("id (desc)", userData=Sort_Params(SORT_FIELD.NUMBER, SORT_TYPE.DESC))
		self.sort_combo.addItem("size (asc)", userData=Sort_Params(SORT_FIELD.SIZE,SORT_TYPE.ASC))
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

		self.list_view = QListWidget()
		self.list_view.setStyleSheet(list_style)
		self.list_view.setSpacing(4)

		self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

		layout = QVBoxLayout(self)

		search_layout = QHBoxLayout()

		search_layout.addWidget(self.searchbar)
		search_layout.addWidget(self.sort_label)
		search_layout.addWidget(self.sort_combo)

		layout.addLayout(search_layout)
		layout.addWidget(self.list_view)

		self.searchbar.textChanged.connect(self.apply_filter_and_sort)

		self.sort_combo.currentIndexChanged.connect(self.apply_filter_and_sort)

		self.list_view.itemSelectionChanged.connect(self.on_selection_changed)

		self.list_view.itemChanged.connect(self.on_item_changed)

	def set_tags(self, animations: list[Tag_Model]):
		self.list_view.blockSignals(True)

		try:
			self.raw_animations = []

			self.list_view.clear()
			self.raw_animations = animations

			self.apply_filter_and_sort()

		finally:
			self.list_view.blockSignals(False)

		self.selection_changed.emit()

	def current_animation(self) -> Tag_Model | None:
		item = self.list_view.currentItem()

		if item is None:
			return None

		return item.data(Qt.ItemDataRole.UserRole)

	def selected_animations(self) -> list[Tag_Model]:
		result = []

		for index in range(self.list_view.count()):
			item = self.list_view.item(index)

			if item.checkState() == Qt.CheckState.Checked:
				animation = item.data(Qt.ItemDataRole.UserRole)

				result.append(animation)

		return result

	def uncheck_all(self):
		self.list_view.blockSignals(True)

		try:
			for index in range(self.list_view.count()):
				item = self.list_view.item(index)
				item.setCheckState(Qt.CheckState.Unchecked)
		finally:
			self.list_view.blockSignals(False)

		self.selection_changed.emit()

	def check_all(self):
		self.list_view.blockSignals(True)

		try:
			for index in range(self.list_view.count()):
				item = self.list_view.item(index)
				item.setCheckState(Qt.CheckState.Checked)
		finally:
			self.list_view.blockSignals(False)

		self.selection_changed.emit()

	def apply_filter_and_sort(self):
		filter_text = self.searchbar.text().strip().lower()

		sort_data: Sort_Params = self.sort_combo.currentData()

		if not filter_text:
			filtered = list(self.raw_animations)

		else:
			filtered = [
				animation
				for animation in self.raw_animations
				if self.matches_filter(animation, filter_text, )
			]

		filtered.sort(
			key=lambda animation: self.sort_key(animation, sort_data.field),
			reverse=(sort_data.type is SORT_TYPE.DESC)
		)

		self.update_display_list(filtered)

	def matches_filter(self, animation: Tag_Model, query: str) -> bool:
		return query in str(animation.handle).lower()

	def sort_key(self, animation: Tag_Model, field: SORT_FIELD):
		if field is SORT_FIELD.NUMBER:
			return animation.handle

		if field is SORT_FIELD.SIZE:
			return animation.size

		return 0

	def update_display_list(self, animations: list[Tag_Model]):
		# save which ones are checked
		checked = {
			self.animation_key(animation)
			for animation in self.selected_animations()
		}

		current = self.current_animation()
		current_key = (
			self.animation_key(current)
			if current is not None
			else None
		)

		self.list_view.blockSignals(True)

		try:
			self.list_view.clear()

			new_current_item = None

			for animation in animations:
				item = QListWidgetItem(animation.to_line("handle_and_size"))

				item.setData(Qt.ItemDataRole.UserRole, animation)
				item.setFlags(item.flags()| Qt.ItemFlag.ItemIsUserCheckable) # make selectable
				key = self.animation_key(animation)

				if key in checked:
					item.setCheckState(Qt.CheckState.Checked)
				else:
					item.setCheckState(Qt.CheckState.Unchecked)

				self.list_view.addItem(item)

				# restore current selected animation
				if current_key is not None and key == current_key:
					new_current_item = item

			if new_current_item is not None:
				self.list_view.setCurrentItem(new_current_item)

		finally:
			self.list_view.blockSignals(False)

	def animation_key(self, animation: Tag_Model):
		return animation.handle

	def on_selection_changed(self):
		current = self.list_view.currentItem()

		if current is None:
			return

		animation = current.data(Qt.ItemDataRole.UserRole)

		self.tag_selected.emit(animation.handle)


	def on_item_changed(self, item: QListWidgetItem):
		self.selection_changed.emit()
