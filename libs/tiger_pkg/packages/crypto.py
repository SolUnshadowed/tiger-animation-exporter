from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from libs.tiger_pkg.packages.block_flags import Block_Flags
from libs.tiger_pkg.game_version import Game_Version
from libs.tiger_pkg.packages import exceptions as err

AES_KEY_0 = bytes(
	(0xD6, 0x2A, 0xB2, 0xC1, 0x0C, 0xC0, 0x1B, 0xC5, 0x35, 0xDB, 0x7B, 0x86, 0x55, 0xC7,
	0xDC, 0x3B)
)

AES_KEY_1 = bytes(
	(0x3A, 0x4A, 0x5D, 0x36, 0x73, 0xA6, 0x60, 0x58, 0x7E, 0x63, 0xE6, 0x76, 0xE4, 0x08,
	0x92, 0xB5)
)

AES_NONCE_BASE = bytes(
	(0x84, 0xDF, 0x11, 0xC0, 0xAC, 0xAB, 0xFA, 0x20, 0x33, 0x11, 0x26, 0x99)
)

CIPHER_0 = AESGCM(AES_KEY_0)
CIPHER_1 = AESGCM(AES_KEY_1)


class Package_GCM:
	nonce: bytearray
	package_id: int
	version: Game_Version
	group: int

	def __init__(self, version: Game_Version, package_id: int, group: int):
		self.nonce = bytearray(AES_NONCE_BASE)
		self.version = version
		self.package_id = package_id
		self.group = group

		self.nonce[0] ^= (package_id >> 8) & 0xFF

		#if self.version in (Game_Version.D2_BETA, Game_Version.D2_SK):  # not implemented, TODO
		#		self.nonce[1] = 0xF9
		#else:
		self.nonce[1] = 0xEA

		self.nonce[11] ^= package_id & 0xFF

	def decrypt_block(self, flags: Block_Flags, tag: bytes, data: bytes) -> bytes:
		if flags & Block_Flags.REDACTED:
			raise err.Package_Decrypt_Error("Block is redacted")

		cipher = CIPHER_1 if flags & Block_Flags.ALT_CIPHER else CIPHER_0

		try:
			return cipher.decrypt(bytes(self.nonce), data + tag, b"")
		except Exception as e:
			raise err.Package_Decrypt_Error("Failed to decrypt PKG data block") from e
