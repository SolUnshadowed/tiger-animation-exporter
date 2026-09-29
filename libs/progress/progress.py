from threading import Lock


class Progress:
	_lock: Lock
	_current: int
	_total: int
	_message: str

	def __init__(self):
		self._lock = Lock()
		self._current = 0
		self._total = 0
		self._message = ""

	def update(self, current: int, total: int, message: str = ""):
		with self._lock:
			self._current = current
			self._total = total
			self._message = message

	def get(self) -> tuple[int, int, str]:
		with self._lock:
			return (
				self._current,
				self._total,
				self._message,
			)