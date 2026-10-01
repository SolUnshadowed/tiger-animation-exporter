from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QEvent, QTimer

from libs.progress import Progress


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

		self.progress_bar = QProgressBar()
		self.progress_bar.setTextVisible(False)

		layout.addWidget(self.label)
		layout.addWidget(self.progress_bar)

		self.timer = QTimer(self)
		self.timer.setInterval(50)
		self.timer.timeout.connect(self._poll)

		self.watched_progress: Progress | None = None

		parent.installEventFilter(self)
		self.setGeometry(parent.rect())
		self.hide()

	def eventFilter(self, obj, event):
		if obj is self.parent() and event.type() == QEvent.Type.Resize:
			self.setGeometry(obj.rect())

		return super().eventFilter(obj, event)

	def show_overlay(self, text="Loading"):
		self.label.setText(text)
		self.setGeometry(self.parentWidget().rect())
		self.raise_()
		self.show()

	def hide_overlay(self):
		self.timer.stop()
		self.hide()

	def start_waiting(self, text="Loading"):
		self.timer.stop()
		self.watched_progress = None

		self.label.setText(text)
		self.progress_bar.setRange(0, 0)

		self.show_overlay(text)

	def start_polling(self, progress: Progress):
		self.watched_progress = progress

		self.progress_bar.setRange(0, 0)
		self.progress_bar.setValue(0)

		self.show_overlay()
		self.timer.start()

	def _poll(self):
		if self.watched_progress is None:
			return

		current, total, message = self.watched_progress.get()

		self.label.setText(message)

		if total > 0:
			self.progress_bar.setRange(0, total)
			self.progress_bar.setValue(current)
		else:
			self.progress_bar.setRange(0, 0)

	def update_overlay(self, current: int, total: int, text: str = "Loading"):
		self.timer.stop()
		self.watched_progress = None

		self.label.setText(text)
		self.progress_bar.setRange(0, total)
		self.progress_bar.setValue(current)