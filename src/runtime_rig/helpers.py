from __future__ import annotations
from pyglm import glm
from libs.matrix_operations import (
	glm_get_quat, glm_get_translation,
	glm_compose_mat4,
	glm_axis_x, glm_axis_y, glm_axis_z, X
)

from libs.tag.data_types import Skeleton_Node_Def


def from_to(a: glm.vec3, b: glm.vec3, pole: glm.vec3):
    if glm.dot(a, b) < -0.9999:
        side = glm.normalize(glm.cross(a, pole))
        v = glm.normalize(glm.cross(a, side))
        return glm.quat(0, v.x, v.y, v.z)

    half = glm.normalize(a + b)
    v = glm.cross(a, half)
    return glm.quat(glm.dot(a, half), v.x, v.y, v.z)


# creates a quaternion with x along dir_x and z as close to ref_z
def look_rot_x_dir_z_ref(dir_x: glm.vec3, ref_z: glm.vec3) -> glm.quat:
    x = glm.normalize(dir_x)
    # z closest to ref_z, in plane perpendicular to x,
    # or z is a closest vector to ref_z, orthogonal to x
    z = glm.normalize(glm.cross(glm.cross(x, ref_z), x))

    q1 = from_to(X, x, z) # shortest rotation from (1, 0, 0) to x, (z as pole)
    # q1 * Z is where the Z axis ended up after q1.
    # Both q1 * Z and z are perpendicular to x, so this is a pure twist around x
    # x stays in place, only the roll changes. (x is the pole for the 180 degree case)
    q2 = from_to(glm_axis_z(q1), z, x) # shortest rotation from (0, 0, 1) rotated by q1 to z, with x as pole
    return q2 * q1


# creates a quaternion with x along dir_x and y as close to ref_y
def look_rot_x_dir_y_ref(direction: glm.vec3, ref_y: glm.vec3) -> glm.quat:
    x = glm.normalize(direction)
    y = glm.normalize(glm.cross(glm.cross(x, ref_y), x)) # y closest to ref_y

    q1 = from_to(X, x, y)
    q2 = from_to(glm_axis_y(q1), y, x)
    return q2 * q1


def bone_aim_offset(bone_rot: glm.quat, segment: glm.vec3) -> glm.quat:
    # glm_axis_x(bone_rot) is world orientation of bone's x axis
    # if segment orientation is the same as bone's x axis -> no rotation -> identity quat
    if glm.dot(glm.normalize(segment), glm_axis_x(bone_rot)) >= 1.0:
        return glm.quat()

    # look_rot_x_dir_z_ref(segment, bone_rot * Z) is a quat with x (segment) and z (bone_rot.z in world coords)
    # and return difference between bone_rot and constructed (what is constructed?.. a perfect bone with x along segment)
    return glm.inverse(bone_rot) * look_rot_x_dir_z_ref(segment, glm_axis_z(bone_rot))


def ik_3_solve_no_pole(
    target: glm.mat4, start: glm.mat4, middle: glm.mat4, end: glm.mat4
) -> 'tuple[glm.mat4, glm.mat4, glm.mat4] | None':
    start_tr = glm_get_translation(start)
    start_rot = glm_get_quat(start)
    middle_tr = glm_get_translation(middle)
    middle_rot = glm_get_quat(middle)
    end_tr = glm_get_translation(end)

    start_to_middle_vec = middle_tr - start_tr
    start_to_middle_len = glm.length(start_to_middle_vec)
    middle_to_end_vec = end_tr - middle_tr
    middle_to_end_len = glm.length(middle_to_end_vec)

    if start_to_middle_len <= 1e-4 or middle_to_end_len <= 1e-4:
        return

    # rotation diff from bone quat and bone aimed along segment
    start_rot_delta = bone_aim_offset(start_rot, start_to_middle_vec) # delta between bone and perfect bone (bone which x axis is aligned with segment)
    middle_rot_delta  = bone_aim_offset(middle_rot, middle_to_end_vec)
    start_z = glm_axis_z(start_rot * start_rot_delta) # z axis of perfect bone
    middle_z  = glm_axis_z(middle_rot * middle_rot_delta)

    start_to_target_vec = glm_get_translation(target) - start_tr # result chain
    max_chain_len = 0.98 * (start_to_middle_len + middle_to_end_len)  # max allowed length for start_to_target, 98% to prevent fully straight start_to_target
    min_chain_len = min(max_chain_len, 1.02 * abs(start_to_middle_len - middle_to_end_len))  # l
    start_to_target_vec_clamped = glm.clamp(glm.length(start_to_target_vec), min_chain_len, max_chain_len)
    start_to_target_aim = glm.normalize(start_to_target_vec)  # direction from start to target
    end_new_tr = start_tr + start_to_target_aim * start_to_target_vec_clamped  # wrist position, using clamped length and direction aim

    # cosine law, angle between start_to_middle and start_to_target
    cos_a = (
        (start_to_middle_len * start_to_middle_len + start_to_target_vec_clamped * start_to_target_vec_clamped - middle_to_end_len * middle_to_end_len) /
        (2 * start_to_middle_len * start_to_target_vec_clamped)
    )
    sin_a = glm.sqrt(max(1 - cos_a * cos_a, 1e-8))
    bend_plane_rot = look_rot_x_dir_y_ref(start_to_target_aim, glm.normalize(start_to_middle_vec))
    # look_rot_x_dir_y_ref is not mandatory, can be look_rot_x_dir_z_ref
    # just making a basis with x and y, hence in next line z is zero, because plane is flat, obviously
    middle_new_tr = start_tr + bend_plane_rot * glm.vec3(start_to_middle_len * cos_a, start_to_middle_len * sin_a, 0)

    s = glm_compose_mat4(
        start_tr, # keep translation
        # middle_new_tr - start_tr = shoulder -> elbow
        # look_rot_x_dir_z_ref(middle_new_tr - start_tr, start_z) - orientation of a perfect bone
        # * glm.inverse(start_rot_delta) is to make from perfect bone a real one
        look_rot_x_dir_z_ref(middle_new_tr - start_tr, start_z) * glm.inverse(start_rot_delta),
        glm.vec3(1)
    )
    m = glm_compose_mat4(
        middle_new_tr, # updated translation
        look_rot_x_dir_z_ref(end_new_tr - middle_new_tr, middle_z) * glm.inverse(middle_rot_delta),
        glm.vec3(1)
    )
    e = glm_compose_mat4(
        end_new_tr, # updated translation
        glm_get_quat(target), # keep rotation
        glm.vec3(1)
    )

    return (s, m, e)


def ik_3_solve_with_pole(
    target: glm.mat4, pole: glm.vec3, start: glm.mat4, middle: glm.mat4, end: glm.mat4
) -> 'tuple[glm.mat4, glm.mat4, glm.mat4] | None':
    start_to_middle_vec = glm_get_translation(middle) - glm_get_translation(start)
    start_to_middle_len = glm.length(start_to_middle_vec)
    middle_to_end_vec = glm_get_translation(end) - glm_get_translation(middle)
    middle_to_end_len = glm.length(middle_to_end_vec)

    if start_to_middle_len <= 1e-4 or middle_to_end_len <= 1e-4:
        return

    start_to_target_vec = glm_get_translation(target) - glm_get_translation(start)
    start_to_target_vec_clamped = glm.clamp(
        glm.length(start_to_target_vec),
        abs(start_to_middle_len - middle_to_end_len),
        start_to_middle_len + middle_to_end_len
    )
    # creating x, y basis to solve in bend plane
    x = glm.normalize(start_to_target_vec) if glm.length(start_to_target_vec) >= 1e-4 else glm_axis_x(glm_get_quat(start))
    y = glm.normalize(glm.cross(pole, x))

    # cosine law, angle between start_to_middle and start_to_target
    cos_a = (
        (start_to_middle_len * start_to_middle_len + start_to_target_vec_clamped * start_to_target_vec_clamped - middle_to_end_len * middle_to_end_len) /
        (2 * start_to_middle_len * start_to_target_vec_clamped)
    )
    sin_a = -glm.sqrt(max(1 - cos_a * cos_a, 0))  # always the negative side
    middle_new_tr = glm_get_translation(start) + x * (start_to_middle_len * cos_a) + y * (start_to_middle_len * sin_a)
    end_new_tr = glm_get_translation(start) + x * start_to_target_vec_clamped # from start for start_to_target_vec_clamped in direction x

    s = glm_compose_mat4(
        glm_get_translation(start),
        from_to( # from to is delta between old and new middle_tr
            glm.normalize(start_to_middle_vec),
            glm.normalize(middle_new_tr - glm_get_translation(start)),
            pole
        ) * glm_get_quat(start), # add delta
        glm.vec3(1.0)
    )
    m = glm_compose_mat4(
        middle_new_tr,
        from_to(
            glm.normalize(middle_to_end_vec),
            glm.normalize(end_new_tr - middle_new_tr),
            pole
        ) * glm_get_quat(middle),
        glm.vec3(1.0)
    )
    e = glm_compose_mat4(
        end_new_tr,
        glm_get_quat(target),
        glm.vec3(1.0)
    )

    return (s, m, e)

def descendants(bone_index: int, node_defs: list[Skeleton_Node_Def], stop_at: set[int]) -> list[int]:
    start_node_def = node_defs[bone_index]

    stack = [start_node_def.first_child_node_index]

    result = []

    while stack:
        index = stack.pop()
        if index < 0:
            continue

        node = node_defs[index]

        # put siblings in case this node is in stop_at
        stack.append(node.next_sibling_node_index)

        if index in stop_at:
            continue

        # if it is not in stop_at -> add to result, put first child in stack
        result.append(index)
        stack.append(node.first_child_node_index)

    return result


def propagate(start: int, middle: int, end: int, pre_ik: glm.array, post_ik: glm.array, node_defs: list[Skeleton_Node_Def]):
    chain = {start, middle, end}

    for bone_index in chain:
        delta = post_ik[bone_index] * glm.inverse(pre_ik[bone_index])

        for child in descendants(bone_index, node_defs, stop_at=chain):
            post_ik[child] = delta * pre_ik[child]
