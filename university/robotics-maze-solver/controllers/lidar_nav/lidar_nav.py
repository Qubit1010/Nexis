"""
lidar_nav.py  -  Autonomous LiDAR navigation (gap-seeking / VFH-style)
=====================================================================

A TurtleBot3 Burger crosses a two-room obstacle environment to a goal beacon.

Earlier this used an artificial potential field, but those ORBIT a pillar that
sits between the robot and the goal (the sideways push dominates and the robot
circles forever). This version uses a GAP-SEEKING method instead, which goes
around obstacles cleanly:

  Each step it knows the goal bearing (from GPS + IMU). It scans every laser
  direction, keeps only those with enough clearance for the robot to fit
  (checked over an angular window, not a single ray), and steers toward the
  CLEAR direction whose bearing is closest to the goal. A small hysteresis term
  keeps it from dithering left/right at a pillar. If nothing ahead is clear it
  rotates toward the most open direction.

A Pen draws the path; distance and time print on arrival.

LiDAR convention: Webots orders the range image left-to-right, so LIDAR_FLIP is
True (index 0 = leftmost ray); forward is the middle of the 360-degree scan.
"""

import math
from controller import Supervisor

# ---------------- Tunables ----------------
MAX_SPEED = 6.0
CRUISE = 4.0
TURN_GAIN = 3.0
SAFE_DIST = 0.45         # a direction counts as clear only if nothing is nearer
GAP_HALF = math.radians(18)   # half-width of the clearance window (robot must fit)
SEARCH_HALF = math.radians(120)  # how far off forward we consider candidate headings
SLOW_DIST = 0.55         # slow down if the path straight ahead is closer than this
HYSTERESIS = 0.3         # bias toward the previously chosen heading (anti-dither)
GOAL = (1.2, 1.2)        # fallback only; the live goal position is read each step
GOAL_RADIUS = 0.35

# LiDAR angle convention
LIDAR_FLIP = True
LIDAR_OFFSET = 0.0


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def get_device_any(robot, names):
    for n in names:
        d = robot.getDevice(n)
        if d is not None:
            return d
    return None


# ---------------- Setup ----------------
robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# The goal beacon node, so we can read its LIVE position (drag it in the scene
# tree and the robot retargets). Falls back to the fixed GOAL if not found.
goal_node = robot.getFromDef("GOAL")
if goal_node is None:
    print("WARNING: DEF GOAL not found - using fixed GOAL", GOAL)


def goal_xy():
    if goal_node is not None:
        p = goal_node.getPosition()
        return p[0], p[1]
    return GOAL

left_motor = get_device_any(robot, ["left wheel motor", "left wheel", "wheel_left_joint"])
right_motor = get_device_any(robot, ["right wheel motor", "right wheel", "wheel_right_joint"])
if left_motor is None or right_motor is None:
    raise RuntimeError("Could not find wheel motors - check device names in the proto.")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

lidar = get_device_any(robot, ["LDS-01", "lidar"])
if lidar is None:
    raise RuntimeError("Could not find the LiDAR - check device name in the proto.")
lidar.enable(timestep)

gps = robot.getDevice("gps")
gps.enable(timestep)
imu = get_device_any(robot, ["imu", "inertial unit"])
if imu is None:
    raise RuntimeError("Could not find the IMU - check device name in the proto.")
imu.enable(timestep)

fov = lidar.getFov()
N = lidar.getHorizontalResolution()
max_range = lidar.getMaxRange()


def ray_angle(i):
    """Angle of laser ray i in the robot frame (+ = left / CCW, 0 = forward)."""
    j = (N - 1 - i) if LIDAR_FLIP else i
    return wrap(-fov / 2.0 + (j + 0.5) * (fov / N) + LIDAR_OFFSET)


ray_ang = [ray_angle(i) for i in range(N)]
window = max(1, int(round(GAP_HALF / (fov / N))))   # rays per side of the window
forward_index = min(range(N), key=lambda i: abs(ray_ang[i]))


def rng(ranges, i):
    d = ranges[i % N]
    if math.isinf(d) or d <= 0.0:
        return max_range
    return d


def clearance(ranges, i):
    """Minimum range in an angular window around ray i (does the robot fit here?)."""
    m = max_range
    for k in range(i - window, i + window + 1):
        v = rng(ranges, k)
        if v < m:
            m = v
    return m


start_time = robot.getTime()
prev_pos = None
distance_travelled = 0.0
prev_phi = 0.0
tick = 0

# ---------------- Main loop ----------------
while robot.step(timestep) != -1:
    x, y, _ = gps.getValues()
    if prev_pos is not None:
        distance_travelled += math.hypot(x - prev_pos[0], y - prev_pos[1])
    prev_pos = (x, y)

    gx, gy = goal_xy()
    goal_dist = math.hypot(x - gx, y - gy)
    if goal_dist < GOAL_RADIUS:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
        print("Goal reached - navigation complete.")
        print("  distance travelled: {:.2f} m".format(distance_travelled))
        print("  time to goal:       {:.1f} s".format(robot.getTime() - start_time))
        break

    ranges = lidar.getRangeImage()
    yaw = imu.getRollPitchYaw()[2]
    goal_bearing = wrap(math.atan2(gy - y, gx - x) - yaw)

    # Pick the clear heading whose bearing is closest to the goal (+ hysteresis).
    best_phi = None
    best_cost = float("inf")
    best_open_phi = 0.0
    best_open_rng = -1.0
    for i in range(N):
        a = ray_ang[i]
        if abs(a) > SEARCH_HALF:
            continue
        clr = clearance(ranges, i)
        if clr > best_open_rng:          # track most open (fallback if all blocked)
            best_open_rng = clr
            best_open_phi = a
        if clr < SAFE_DIST:
            continue
        cost = abs(wrap(a - goal_bearing)) + HYSTERESIS * abs(wrap(a - prev_phi))
        if cost < best_cost:
            best_cost = cost
            best_phi = a

    if best_phi is None:                 # boxed in: rotate toward the most open gap
        phi = best_open_phi
        forward = 0.6
    else:
        phi = best_phi
        forward = CRUISE * max(0.1, math.cos(phi))
        if clearance(ranges, forward_index) < SLOW_DIST:
            forward = min(forward, 1.2)
    prev_phi = phi

    left_speed = max(-MAX_SPEED, min(MAX_SPEED, forward - TURN_GAIN * phi))
    right_speed = max(-MAX_SPEED, min(MAX_SPEED, forward + TURN_GAIN * phi))
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

    tick += 1
    if tick % 25 == 0:
        print("goal dist: {:.2f} m | heading offset: {:.0f} deg".format(
            goal_dist, math.degrees(phi)))
