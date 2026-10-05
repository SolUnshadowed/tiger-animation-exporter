from enum import IntFlag


class Block_Flags(IntFlag):
	COMPRESSED = 0x1
	ENCRYPTED = 0x2
	ALT_CIPHER = 0x4
	REDACTED = 0x8
