class Animation_Read_Error(Exception):
    """Base decode_animation error"""

class Unknown_Codec_Error(Animation_Read_Error):
    """if different from 0, 1, 2, 3"""