import logging
import ctypes
from enum import IntEnum
from pathlib import Path
import platform


logger = logging.getLogger(__name__)

class Oodle_Error(Exception):
	pass

class Oodle_Already_Initialised_Error(Oodle_Error):
	pass

class Oodle_Not_Initialised_Error(Oodle_Error):
	pass

class Oodle_Decompression_Error(Oodle_Error):
	pass

class Oodle_Lz_Fuzz_Safe(IntEnum):
	No = 0
	Yes = 1


class Oodle_Lz_Check_CRC(IntEnum):
	No = 0
	Yes = 1


class Oodle_Lz_Verbosity(IntEnum):
	None_ = 0
	Minimal = 1
	Some = 2
	Lots = 3


class Oodle_Lz_Thread_Phase(IntEnum):
	ThreadPhase1 = 1
	ThreadPhase2 = 2
	ThreadPhaseAll = 3


class Oodle_Version(IntEnum):
	V3 = 3
	V9 = 9


class Oodle:
	def __init__(self, version: Oodle_Version, lib_paths: list[Path]):
		self.lib = self.load_library(version, lib_paths)

		self.decompress = self.lib.OodleLZ_Decompress

		self.decompress.argtypes = [
			ctypes.POINTER(ctypes.c_uint8),  # comp_buf
			ctypes.c_int64,                  # comp_buf_size

			ctypes.POINTER(ctypes.c_uint8),  # raw_buf
			ctypes.c_int64,                  # raw_len

			ctypes.c_uint32,  # fuzz_safe
			ctypes.c_uint32,  # check_crc
			ctypes.c_uint32,  # verbosity

			ctypes.c_void_p,  # dec_buf_base
			ctypes.c_void_p,  # dec_buf_size

			ctypes.c_void_p,  # fp_callback
			ctypes.c_void_p,  # callback_user_data

			ctypes.c_void_p,  # decoder_memory
			ctypes.c_void_p,  # decoder_memory_size

			ctypes.c_uint32,  # thread_phase
		]

		self.decompress.restype = ctypes.c_int64


	def load_library(self, version: Oodle_Version, lib_paths: list[Path]):
		os_type = platform.system()

		if os_type == "Windows":
			name = f"oo2core_{version.value}_win64.dll"
		elif os_type == "Linux":
			match version:
				case Oodle_Version.V3:
					name = "liblinoodle3.so"
				case Oodle_Version.V9:
					name = "liboodle-data-shared.so"
		else:
			raise RuntimeError(f"Unsupported platform {os_type}")

		errors = []

		for path in lib_paths:
			full_path = path / name

			try:
				lib = ctypes.CDLL(str(full_path))
				logger.info(f"Loaded Oodle{version.value}: {str(full_path)}")
				return lib
			except OSError as e:
				errors.append(f"\t{full_path}: {e}")

		details = "\n".join(errors) if errors else "  (no search paths provided)"
		raise FileNotFoundError(
			f"Cannot load Oodle library '{name}', tried:\n{details}"
		)

	def decompress_data(self, data: bytes, output_size: int = 0x40000) -> bytes:
		# create arrays
		src_array = ctypes.c_uint8 * len(data)
		src = src_array.from_buffer_copy(data)

		dst_array = ctypes.c_uint8 * output_size
		dst = dst_array()

		result = self.decompress(
			src,
			len(data),

			dst,
			output_size,

			Oodle_Lz_Fuzz_Safe.Yes,
			Oodle_Lz_Check_CRC.No,
			Oodle_Lz_Verbosity.Minimal,

			None,
			None,
			None,
			None,
			None,
			None,

			Oodle_Lz_Thread_Phase.ThreadPhaseAll,
		)

		if result < 0:
			raise Oodle_Decompression_Error(
				f"Oodle decompression failed: {result}"
			)

		return bytes(dst)


# global instances
OODLE_3: Oodle | None = None
OODLE_9: Oodle | None = None
LIBRARY_PATHS: list[Path] = []
INITIALIZED = False


def init(library_paths: list[Path | str] | str | Path):
	global LIBRARY_PATHS, INITIALIZED

	if INITIALIZED:
		raise Oodle_Already_Initialised_Error("Oodle module is already initialized")

	if isinstance(library_paths, (list, tuple)):
		raw_paths = library_paths
	else:
		raw_paths = [library_paths]

	if not raw_paths:
		raise ValueError("At least one library path must be provided")

	paths = []
	skipped = []

	for p in raw_paths:
		path = Path(p)
		if path.is_dir():
			paths.append(path)
		else:
			skipped.append(str(path))

	if not paths:
		reason = "\n".join(f"  {p}" for p in skipped) if skipped else "  (no paths provided)"
		raise NotADirectoryError(
			f"None of the provided paths are valid directories:\n{reason}"
		)

	if skipped:
		for p in skipped:
			logger.warning(f"Ignoring invalid Oodle search path: {p}")

	LIBRARY_PATHS = paths
	INITIALIZED = True


def get_oodle(version: Oodle_Version) -> Oodle:
	global OODLE_3, OODLE_9, INITIALIZED

	if not INITIALIZED:
		raise Oodle_Not_Initialised_Error("Module is not initialized")

	match version:
		case Oodle_Version.V3:
			if OODLE_3 is None:
				OODLE_3 = Oodle(Oodle_Version.V3, LIBRARY_PATHS)

			return OODLE_3

		case Oodle_Version.V9:
			if OODLE_9 is None:
				OODLE_9 = Oodle(Oodle_Version.V9, LIBRARY_PATHS)

			return OODLE_9


# todo check block sizes
def decompress_3(data: bytes, output_size: int=0x40000) -> bytes:
	return get_oodle(Oodle_Version.V3).decompress_data(
		data,
		output_size
	)


def decompress_9(data: bytes, output_size: int=0x40000) -> bytes:
	return get_oodle(Oodle_Version.V9).decompress_data(
		data,
		output_size
	)
