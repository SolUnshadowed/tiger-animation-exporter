from threading import Lock


class Progress:
	lock: Lock
	current: int
	total: int
	message: str

	def __init__(self):
		self.lock = Lock()
		self.current = 0
		self.total = 0
		self.message = ""

	def update(self, current: int, total: int, message: str = ""):
		with self.lock:
			self.current = current
			self.total = total
			self.message = message

	def get(self) -> tuple[int, int, str]:
		with self.lock:
			return (
				self.current,
				self.total,
				self.message,
			)