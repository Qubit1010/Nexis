"""
swarm_flock.py  -  Reynolds Boids flocking, 5 e-puck swarm
===========================================================

Each robot runs this same controller. Because every robot is a Webots
Supervisor it can read the world-frame position and heading of every
other robot directly from the scene tree -- no radio emitter/receiver
needed.

Reynolds' three Boids rules are applied every timestep:

  Separation  - push away from neighbours closer than SEP_RANGE.
                Weight W_SEP. Prevents collisions and crowding.

  Cohesion    - steer toward the average position of visible neighbours.
                Weight W_COH. Keeps the flock together.

  Alignment   - match the average heading of visible neighbours.
                Weight W_ALI. Makes the flock move as one unit.

The three vectors are combined (weighted sum, then normalised) into a
target heading. Proximity sensors (ps0-ps7, built into the e-puck) add
wall and obstacle avoidance on top so the group stays inside the arena.

Tuning knobs are at the top of the file.
"""

import math
from controller import Supervisor

# ---- Tunables ---------------------------------------------------------------
MAX_SPEED    = 5.0    # rad/s  (e-puck physical max ~6.28)
CRUISE       = 3.5    # base forward speed when heading error is small
TURN_GAIN    = 4.0    # how sharply to steer toward the target heading
N_ROBOTS     = 5      # must match the number of DEF ROBOT_x nodes in the world

VISION_RANGE = 1.5    # (m) see neighbours within this radius
SEP_RANGE    = 0.25   # (m) push away from neighbours closer than this

W_SEP        = 3.0    # separation weight  (raise to spread out more)
W_COH        = 0.8    # cohesion weight    (raise to clump tighter)
W_ALI        = 1.2    # alignment weight   (raise to sync headings faster)
W_WALL       = 5.0    # wall avoidance weight

PS_WALL_THR  = 60.0   # proximity reading above which wall avoidance activates
PS_MAX       = 4096.0 # max proximity sensor reading (full-scale)

# e-puck proximity sensor angles in the ROBOT frame, CCW from forward (0 = forward)
PS_ANGLES = [
    -math.radians(22.5),   # ps0  front-right
    -math.radians(67.5),   # ps1  right
    -math.radians(90.0),   # ps2  side-right
    -math.radians(135.0),  # ps3  rear-right
     math.radians(135.0),  # ps4  rear-left
     math.radians(90.0),   # ps5  side-left
     math.radians(67.5),   # ps6  left
     math.radians(22.5),   # ps7  front-left
]

# -----------------------------------------------------------------------------


def wrap(a):
    """Wrap angle to [-pi, pi]."""
    return (a + math.pi) % (2 * math.pi) - math.pi


def norm2(vx, vy):
    """Return unit vector (vx, vy); (0, 0) if the vector is nearly zero."""
    length = math.hypot(vx, vy)
    if length > 1e-4:
        return vx / length, vy / length
    return 0.0, 0.0


def node_pos(node):
    """World-frame (x, y) of a scene-tree node."""
    p = node.getPosition()
    return p[0], p[1]


def node_yaw(node):
    """
    World-frame yaw (heading) of a scene-tree node.
    getOrientation() returns a row-major 3x3 rotation matrix as 9 floats.
    For a z-up robot on flat ground: yaw = atan2(R[1][0], R[0][0])
                                         = atan2(m[3],     m[0]).
    """
    m = node.getOrientation()
    return math.atan2(m[3], m[0])


# ---- Device setup -----------------------------------------------------------
robot    = Supervisor()
timestep = int(robot.getBasicTimeStep())
own_node = robot.getSelf()

# Proximity sensors (ps0-ps7 are always present on the e-puck)
ps = [robot.getDevice("ps{}".format(i)) for i in range(8)]
for s in ps:
    s.enable(timestep)

# Differential-drive motors
left_motor  = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Collect references to all OTHER robots' scene-tree nodes.
# (Supervisor.getFromDef is used here instead of radio/emitter/receiver.)
robot_nodes = []
for i in range(N_ROBOTS):
    n = robot.getFromDef("ROBOT_{}".format(i))
    if n is not None and n != own_node:
        robot_nodes.append(n)

tick = 0

# ---- Main loop --------------------------------------------------------------
while robot.step(timestep) != -1:

    # Own state
    ox, oy  = node_pos(own_node)
    own_hdg = node_yaw(own_node)

    # --- Gather visible neighbours -------------------------------------------
    neighbours = []
    for node in robot_nodes:
        nx, ny = node_pos(node)
        dist   = math.hypot(nx - ox, ny - oy)
        if 1e-4 < dist < VISION_RANGE:
            neighbours.append((nx, ny, node_yaw(node), dist))

    # --- Boids rules (all vectors computed in world frame) -------------------
    sep_x = sep_y = 0.0   # separation: push away from close neighbours
    coh_x = coh_y = 0.0   # cohesion:   sum of neighbour positions (averaged later)
    ali_x = ali_y = 0.0   # alignment:  sum of unit heading vectors

    for nx, ny, nhdg, dist in neighbours:
        if dist < SEP_RANGE:
            sep_x += (ox - nx) / (dist + 1e-6)
            sep_y += (oy - ny) / (dist + 1e-6)
        coh_x += nx
        coh_y += ny
        ali_x += math.cos(nhdg)
        ali_y += math.sin(nhdg)

    n = len(neighbours)

    # Default: hold current heading if no neighbours are visible
    tx = math.cos(own_hdg)
    ty = math.sin(own_hdg)

    if n > 0:
        # Cohesion: direction toward average neighbour position
        cx, cy = norm2(coh_x / n - ox, coh_y / n - oy)
        # Alignment: average neighbour heading as a unit vector
        ax, ay = norm2(ali_x, ali_y)
        # Separation: already a sum of push-away vectors
        sx, sy = norm2(sep_x, sep_y)

        # Weighted sum -> target direction
        tx, ty = norm2(
            W_COH * cx + W_ALI * ax + W_SEP * sx,
            W_COH * cy + W_ALI * ay + W_SEP * sy,
        )

    # --- Wall / obstacle avoidance -------------------------------------------
    # Each proximity sensor points in a known direction in the robot frame.
    # Convert to world frame and push the target direction away from the wall.
    ps_vals = [s.getValue() for s in ps]
    for i, val in enumerate(ps_vals):
        if val > PS_WALL_THR:
            sensor_world_angle = own_hdg + PS_ANGLES[i]
            strength = (val - PS_WALL_THR) / (PS_MAX - PS_WALL_THR)
            tx -= W_WALL * strength * math.cos(sensor_world_angle)
            ty -= W_WALL * strength * math.sin(sensor_world_angle)

    # Normalise the combined vector and compute heading error
    tx, ty      = norm2(tx, ty)
    target_hdg  = math.atan2(ty, tx)
    heading_err = wrap(target_hdg - own_hdg)

    # Slow down when turning sharply
    forward = CRUISE * max(0.1, math.cos(heading_err))

    left_speed  = max(-MAX_SPEED, min(MAX_SPEED, forward - TURN_GAIN * heading_err))
    right_speed = max(-MAX_SPEED, min(MAX_SPEED, forward + TURN_GAIN * heading_err))
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

    tick += 1
    if tick % 50 == 0:
        print("[{}] visible neighbours: {} | heading: {:.0f} deg".format(
            robot.getName(), n, math.degrees(own_hdg)))
