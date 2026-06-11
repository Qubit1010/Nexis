# Autonomous LiDAR Navigation (Webots Lab Project)

A **TurtleBot3 Burger** with a 360-degree **LiDAR** autonomously crosses a two-room
obstacle environment to a goal beacon, using a **gap-seeking (VFH-style)** controller.
No map, no teleop - the robot senses the world with its laser scanner and decides where to
go in real time.

This is a single self-contained Webots world built to look like real autonomous robotics:
a sweeping laser, two rooms joined by a doorway, an obstacle field, and reactive navigation
toward a goal.

## What it demonstrates

- **360-degree LiDAR sensing** - a full laser scan (the real TurtleBot3 LDS-01) every step.
- **Gap-seeking navigation** - each step it knows the goal bearing and steers toward the
  *clear* laser direction whose bearing is closest to the goal. This goes cleanly *around*
  obstacles instead of orbiting them (the failure mode of a naive potential field).
- **Clearance-aware avoidance** - a direction only counts as drivable if there is room for
  the robot to fit, checked over an angular window rather than a single ray, so it keeps a
  safety margin and never "attaches" to a pillar.
- **Boxed-in recovery** - if nothing ahead is clear, it rotates toward the most open
  direction the laser sees until a gap opens up.
- **Odometry** - a Pen draws the path on the floor; distance travelled and time-to-goal are
  printed on arrival. A GPS confirms the goal and an IMU provides heading.

## Environment

A 3 m arena split into two rooms by a **dividing wall with a doorway** (around x = 0.35),
plus a stub wall near the start, and eight pillars/boxes scattered across both rooms. The
robot starts in the lower-left room and must thread the pillars, pass through the doorway,
and cross the upper room to the magenta goal beacon.

## Project structure

```
robotics-maze-solver/
├── worlds/
│   └── lidar_nav.wbt            # 3m arena, obstacle field, goal beacon, TurtleBot3 + LiDAR
├── controllers/
│   └── lidar_nav/
│       └── lidar_nav.py          # gap-seeking (VFH-style) navigation
└── README.md
```

## How to run

1. Open **Webots** (R2023b or newer recommended).
2. `File > Open World...` and select `worlds/lidar_nav.wbt`.
   - The first open downloads the TurtleBot3 / arena PROTO assets, so stay online for it.
3. Press **Play**. The robot starts in the far corner and drives to the magenta beacon,
   going around the grey/brown obstacles and through the doorway. The console prints periodic
   goal-distance and heading-offset readings, then a final distance/time report; the blue Pen
   trail shows the route taken.

The controller is plain Python on Webots' built-in interpreter - nothing to compile.

## How it works

Each timestep:

1. The **goal bearing** in the robot's frame is computed from the GPS position and IMU
   heading.
2. Every LiDAR direction is scored. A direction is **drivable** only if the minimum range
   within an angular window around it (`GAP_HALF`) exceeds `SAFE_DIST` - i.e. there is room
   for the robot to fit, with margin.
3. Among the drivable directions within `SEARCH_HALF` of forward, it picks the one whose
   bearing is **closest to the goal** (plus a small `HYSTERESIS` bias toward the previous
   heading, to stop left/right dithering at a pillar).
4. It steers toward that direction and drives forward, slowing if the way straight ahead is
   within `SLOW_DIST`. If nothing is drivable, it rotates toward the most open direction.
5. When the GPS says it is within `GOAL_RADIUS` of the beacon, it stops and reports.

This is a textbook reactive method (a vector-field-histogram variant): no global map, and it
visibly steers around each obstacle toward the goal. Unlike a naive potential field it does
not orbit obstacles, because it always commits to a clear gap rather than balancing push and
pull forces.

## Tuning

Knobs live at the top of `controllers/lidar_nav/lidar_nav.py`:

- `SAFE_DIST` - how much clearance a direction needs to count as drivable. Larger = wider
  berth around obstacles (and earlier avoidance), but very tight gaps get rejected.
- `GAP_HALF` - half-width of the fit-check window. Larger = safer (won't enter a gap too
  narrow for the robot), smaller = squeezes through tighter gaps.
- `HYSTERESIS` - bias toward the previous heading; raise it if it dithers, lower it if it is
  slow to react.
- `CRUISE`, `MAX_SPEED`, `TURN_GAIN` - speed and how sharply it steers.
- `SLOW_DIST`, `GOAL_RADIUS` - when to creep, and arrival tolerance.
- `GOAL` - target position; must match the `goal` solid in the world file (`1.2 1.2`).

### LiDAR orientation
Webots orders the laser range image left-to-right (index 0 = leftmost ray), so the
controller ships with `LIDAR_FLIP = True` and forward at the middle of the 360-degree scan.
This matches the real LDS-01 on the TurtleBot3. If you ever swap robots and it dodges the
wrong way, flip `LIDAR_FLIP`; if front and back are swapped, set `LIDAR_OFFSET = math.pi`.

## Editing the scene

- **Walls / rooms**: the `wall_*` solids (the divider segments and stub). Keep the doorway
  gap wide enough for the robot to fit (~0.5 m+) and avoid deep U-shaped traps.
- **Obstacles**: the `obs_*` solids (cylinders and boxes, height 0.3 so the laser plane hits
  them). Add or move them freely - just keep a path open.
- **Goal**: drag the magenta beacon (`DEF GOAL`) anywhere - even while the sim runs - and
  the robot retargets to its new position automatically (the supervisor reads it live). No
  code change needed; the `GOAL` constant is only a fallback if the `DEF GOAL` is missing.
- **Robot start**: the `TurtleBot3Burger` `translation` / `rotation`.

## Acceptance check

The robot crosses the arena from the start corner to the magenta beacon, visibly avoiding
the obstacles via its laser, and stops within `GOAL_RADIUS` with a distance/time report
printed to the console - no manual intervention.

## Note on the build
The device wiring was corrected against the actual Webots protos: the TurtleBot3's real
**LDS-01** lidar is kept in the extension slot (an earlier version accidentally replaced it,
which left the robot frozen), the ray ordering is set to Webots' left-to-right convention,
and the GPS/IMU/Pen are added alongside. The navigation was then changed from a potential
field (which orbited the first pillar) to this gap-seeking method. The remaining tuning
surface is `SAFE_DIST` / `GAP_HALF` if it ever clips an obstacle or refuses a real gap.
