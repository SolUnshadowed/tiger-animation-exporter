from pyglm import glm
from src.decode_animation.decode_animation import Bone_Tracks
from src.tag_readers.skeleton.read_skeleton import Transform

# Tiger
# 	Z-up
# 	X-forward
# 	Y-right
# Three.js
# 	Y-up
#	Z-forward
#	X-right
# Tiger to Three.js, GL
# [x, y, z] -> [y, z, x]
#  x  y  z      x  y  z
#  x_new = y_old
#  y_new = z_old
#  z_new = x_old


# transform matrix (x, y, z -> y, z, x)
BUNGIE_TO_GL = glm.mat4(
    glm.vec4(0, 0, 1, 0),  # X -> Z (third position)
    glm.vec4(1, 0, 0, 0),  # Y -> X (first)
    glm.vec4(0, 1, 0, 0),  # Z -> Y (second)
    glm.vec4(0, 0, 0, 1)   # W stays
)

# inv mat (x, y, z -> z, x, y)
GL_TO_BUNGIE = glm.transpose(BUNGIE_TO_GL)


def glm_mat4_bungie_to_gl(m: glm.mat4) -> glm.mat4:
    return BUNGIE_TO_GL * m * GL_TO_BUNGIE


def glm_mat4_gl_to_bungie(m: glm.mat4) -> glm.mat4:
    return GL_TO_BUNGIE * m * BUNGIE_TO_GL


def transform_to_gl(transform: Transform) -> Transform:
    return Transform(
        (transform.ts[1], transform.ts[2], transform.ts[0], transform.ts[3]),
        (transform.r[1], transform.r[2], transform.r[0], transform.r[3]),
    )


def tracks_bungie_to_gl(
	tracks: list[Bone_Tracks],
) -> list[Bone_Tracks]:
    return [
        Bone_Tracks(
            bone_name_hash=track.bone_name_hash,
            scales=track.scales[:, [1, 2, 0]],
            translations=track.translations[:, [1, 2, 0]],
            rotations=track.rotations[:, [1, 2, 0, 3]], # quat.w is last
        )
        for track in tracks
    ]


def tracks_gl_to_bungie(
    tracks: list[Bone_Tracks],
) -> list[Bone_Tracks]:
    return [
        Bone_Tracks(
            bone_name_hash=track.bone_name_hash,
            scales=track.scales[:, [2, 0, 1]],
            translations=track.translations[:, [2, 0, 1]],
            rotations=track.rotations[:, [2, 0, 1, 3]],  # quat.w is still last
        )
        for track in tracks
    ]
