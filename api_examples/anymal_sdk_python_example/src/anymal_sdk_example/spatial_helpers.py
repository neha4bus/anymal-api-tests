import math
from typing import Tuple

import anymal_api_proto as api


def create_pose(
    frame_id: str,
    x: float,
    y: float,
    z: float,
    qx: float,
    qy: float,
    qz: float,
    qw: float,
) -> api.Pose:
    pose = api.Pose()
    pose.frame_id = frame_id
    pose.value.position.x = x
    pose.value.position.y = y
    pose.value.position.z = z
    pose.value.orientation.qx = qx
    pose.value.orientation.qy = qy
    pose.value.orientation.qz = qz
    pose.value.orientation.qw = qw
    return pose


def quaternion_to_euler(qx: float, qy: float, qz: float, qw: float) -> Tuple[float, float, float]:
    """
    Helper function that converts a quaternion value into euler angles (roll, pitch, yaw) in radians
    See https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    """
    t0 = +2.0 * (qw * qx + qy * qz)
    t1 = +1.0 - 2.0 * (qx**2 + qy**2)
    roll = math.atan2(t0, t1)

    t2 = +2.0 * (qw * qy - qz * qx)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = max(t2, -1.0)
    pitch = math.asin(t2)

    t3 = +2.0 * (qw * qz + qx * qy)
    t4 = +1.0 - 2.0 * (qy**2 + qz**2)
    yaw = math.atan2(t3, t4)

    return roll, pitch, yaw


def deg_to_rad(deg) -> float:
    return deg * math.pi / 180.0
