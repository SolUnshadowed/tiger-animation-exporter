class Animation_Decode_Error(Exception):
    pass

class Quat_Norm_Error(Animation_Decode_Error):
    """Quat norm is bigger than 1"""
    def __init__(self, norm_val: float):
        self.norm_val = norm_val
        super().__init__(f"Quaternion norm is invalid: {norm_val} (expected ~1.0)")

class Codec_Data_Parse_Error(Animation_Decode_Error):
    """Codec specific errors"""