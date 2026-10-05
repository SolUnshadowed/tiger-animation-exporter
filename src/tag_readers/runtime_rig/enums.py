from enum import IntEnum


class Constraint_Type(IntEnum):
	PARENT = 0
	POINT_AND_ORIENT = 1


class IK_Function_Type(IntEnum):
	NONE = -1
	IK_3 = 0
	RFK = 1


class Space_Type(IntEnum):
	RELATIVE = 0
	PARENT = 1
	OBJECT = 2
	UNK_3 = 3
	BIND = 4
	AVERAGE = 5
	AIM = 6
