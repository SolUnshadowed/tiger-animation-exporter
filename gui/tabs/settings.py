from dataclasses import dataclass
from pathlib import Path
from PySide6.QtWidgets import QWidget, QFileDialog, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout
from PySide6.QtCore import Qt

from libs.tiger_pkg.game_version import Game_Version

from src.export.animation_export.enums import Bone_Name_Convention, Animation_Space


@dataclass
class Settings:
	game_version: Game_Version | None = None
	packages_path: Path | None = None
	export_path: Path | None = None
	bone_name_convention: Bone_Name_Convention = Bone_Name_Convention.BLENDER
	animation_space: Animation_Space = Animation_Space.LOCAL


class Settings_Tab(QWidget):
	path_preview: QLineEdit
	path_button: QPushButton


	def __init__(self, parent=None):
		super().__init__(parent)

		layout = QGridLayout(self)

		name_convention_label = QLabel("Bones name convention")
		name_convention_label.setToolTip("How a skeleton bones will be named")
		self.convention_combo = QComboBox()
		self.convention_combo.addItem("Blender", Bone_Name_Convention.BLENDER)
		self.convention_combo.setItemData(0, "Blender importer style", Qt.ItemDataRole.ToolTipRole)
		self.convention_combo.addItem("fnv1le", Bone_Name_Convention.FNV1LE)
		self.convention_combo.setItemData(
			1,
			"FNV-1 32-bit little-endian hash",
			Qt.ItemDataRole.ToolTipRole
		)
		self.convention_combo.addItem("fnv1le_no_zeroes", Bone_Name_Convention.FNV1LE_NO_ZEROES)
		self.convention_combo.setItemData(
			2,
			"FNV-1 32-bit little-endian hash with leading zeroes stripped.",
			Qt.ItemDataRole.ToolTipRole
		)
		self.convention_combo.addItem("fnv1be", Bone_Name_Convention.FNV1BE)
		self.convention_combo.setItemData(
			3,
			"FNV-1 32-bit big-endian hash.",
		    Qt.ItemDataRole.ToolTipRole
		)
		self.convention_combo.addItem("fnv1be_no_zeroes", Bone_Name_Convention.FNV1BE_NO_ZEROES)
		self.convention_combo.setItemData(
			4,
			"FNV-1 32-bit big-endian hash with leading zeroes stripped.",
		    Qt.ItemDataRole.ToolTipRole
		)
		self.convention_combo.currentIndexChanged.connect(self.select_convention)
		layout.addWidget(name_convention_label, 3, 0)
		layout.addWidget(self.convention_combo, 3, 2)

		space_label = QLabel("Animation space")
		self.space_combo = QComboBox()
		self.space_combo.addItem("Local", Animation_Space.LOCAL)
		self.space_combo.setItemData(
			0,
			"Bones' transforms are in parent local space.",
			Qt.ItemDataRole.ToolTipRole
		)
		self.space_combo.addItem("Object", Animation_Space.OBJECT)
		self.space_combo.setItemData(
			1,
			"bones' transforms are in character's object space.",
			Qt.ItemDataRole.ToolTipRole
		)
		self.space_combo.currentIndexChanged.connect(self.select_space)
		layout.addWidget(space_label, 4, 0)
		layout.addWidget(self.space_combo, 4, 2)

		layout.setAlignment(Qt.AlignmentFlag.AlignTop)

	def select_version(self):
		# get version data
		data = self.version_combo.currentData()
		# set version in settings object
		# remove packages path from settings object
		# remove packages path from ui
		self.path_preview.setText("")
		print(data)

	def select_packages_path(self):
		path = QFileDialog.getExistingDirectory(
			self,
			"Select packages folder"
		)

		if path != "":
			self.path_preview.setText(path)

	def select_export_path(self):
		path = QFileDialog.getExistingDirectory(
			self,
			"Select exports folder"
		)

		if path != "":
			self.export_preview.setText(path)

	def select_convention(self):
		convention = self.convention_combo.currentData()
		print(convention)

	def select_space(self):
		convention = self.space_combo.currentData()
		print(convention)


