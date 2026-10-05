from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QEvent


class Loading_Overlay(QFrame):
	def __init__(self, parent: QWidget):
		super().__init__(parent)
		self.setObjectName("loading_overlay")
		self.setStyleSheet("""
			#loading_overlay {
				background-color: rgba(0, 0, 0, 120);
			}
			#loading_overlay QLabel {
				background: transparent;
				color: white;
				font-size: 16px;
			}
			#loading_overlay QProgressBar {
				min-width: 250px;
			}
		""")

		layout = QVBoxLayout(self)
		layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.label = QLabel("Loading...")
		self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

		self.progress = QProgressBar()
		self.progress.setRange(0, 0)
		self.progress.setTextVisible(False)

		layout.addWidget(self.label)
		layout.addWidget(self.progress)

		parent.installEventFilter(self)
		self.setGeometry(parent.rect())
		self.hide()

	def eventFilter(self, obj, event):
		if obj is self.parent() and event.type() == QEvent.Type.Resize:
			self.setGeometry(obj.rect())
		return super().eventFilter(obj, event)

	def show_overlay(self, text="Loading..."):
		self.label.setText(text)
		self.setGeometry(self.parentWidget().rect())
		self.raise_()
		self.show()

	def hide_overlay(self):
		self.hide()
