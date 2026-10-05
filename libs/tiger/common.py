from enum import IntEnum

class Primitive_Type(IntEnum):
	TRIANGLES = 3
	TRIANGLE_STRIP = 5

class Lod_Category(IntEnum):
	MAIN_GEOM_0 = 0 # main geometry lod0
	GRIP_STOCK_0 = 1  # grip/stock lod0
	STICKERS_0 = 2  # stickers lod0
	INTERNAL_GEOM_0 = 3  # internal geom lod0
	LOW_POLY_GEOM_1 = 4  # low poly geom lod1
	LOW_POLY_GEOM_2 = 7  # low poly geom lod2
	GRIP_STOCK_SCOPE_2 = 8  # grip/stock/scope lod2
	LOW_POLY_GEOM_3 = 9  # low poly geom lod3
	DETAIL_0 = 10 # detail lod0
