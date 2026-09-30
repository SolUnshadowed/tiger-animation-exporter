from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPlainTextEdit, QPushButton
)
from PySide6.QtCore import Qt, Slot

from gui.tabs.packages.tag_list import Tag_List_Widget, Animation_List_Widget
from gui.tabs.entity.entity_title import Entity_Title
from gui.canvas_frame.canvas_frame import Canvas_Frame

from gui.worker_types import Animation_Model
from gui.style.button import button_style

class Entity_Page(QWidget):
	entity_title: Entity_Title
	animations_list: Animation_List_Widget
	stats_area: QPlainTextEdit
	export_button: QPushButton
	render: Canvas_Frame

	animation_handle: int = -1

	def __init__(self, parent=None):
		super().__init__(parent)

		layout = QVBoxLayout(self)

		self.entity_title = Entity_Title()

		self.render = Canvas_Frame()

		self.animations_list = Animation_List_Widget()

		main_splitter = QSplitter(Qt.Orientation.Horizontal)

		left_splitter = QSplitter(Qt.Orientation.Vertical)
		left_splitter.addWidget(self.entity_title)
		left_splitter.addWidget(self.render)
		left_splitter.setStretchFactor(0, 0)
		left_splitter.setStretchFactor(1, 1)

		right_layout_container = QWidget()
		right_layout = QVBoxLayout()

		self.stats_area = QPlainTextEdit()
		self.stats_area.setReadOnly(True)
		self.stats_area.setStyleSheet(
			"""
			QPlainTextEdit {
				background-color: #ffffff;
				border: 1px solid #000000;
				outline: 0;
				padding: 5px;
				margin: 8px;
			}
			"""
		)

		self.export_button = QPushButton("Export")
		self.export_button.setStyleSheet(button_style)

		right_layout.addWidget(self.animations_list)

		uncheck_all_button = QPushButton("Uncheck all")
		uncheck_all_button.setStyleSheet(button_style)
		uncheck_all_button.clicked.connect(self.animations_list.uncheck_all)
		check_all_button = QPushButton("Check all")
		check_all_button.setStyleSheet(button_style)
		check_all_button.clicked.connect(self.animations_list.check_all)

		list_buttons_layout = QHBoxLayout()
		list_buttons_layout.addWidget(uncheck_all_button)
		list_buttons_layout.addWidget(check_all_button)

		right_layout.addLayout(list_buttons_layout)
		right_layout.addWidget(self.export_button)
		right_layout_container.setLayout(right_layout)

		main_splitter.addWidget(left_splitter)
		main_splitter.addWidget(self.stats_area)
		main_splitter.addWidget(right_layout_container)
		main_splitter.setStretchFactor(0, 2)
		main_splitter.setStretchFactor(1, 1)
		main_splitter.setStretchFactor(2, 1)

		layout.addWidget(main_splitter)

	@Slot(object)
	def set_animation(self, animation: Animation_Model):
		self.animation_handle = animation.handle

		self.render.set_animation(animation)
