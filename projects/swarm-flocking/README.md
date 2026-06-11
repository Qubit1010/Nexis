# Swarm Flocking — Reynolds Boids (Webots Lab Project)

Five **e-puck robots** run the same controller and exhibit collective **flocking
behavior** in a shared arena. No robot has a goal. No robot knows the global plan.
The group behavior emerges purely from each robot applying three local rules to
whatever neighbors it can see.

This is a completely different paradigm from single-robot reactive navigation:
instead of one sensor-driven agent pursuing a goal, you have a multi-agent system
where order emerges from simple peer interactions.

## What it demonstrates

- **Reynolds Boids algorithm** — the three-rule model behind flocking in every
  major animated film since 1987 (Batman Returns, The Lion King, Mulan).
- **Supervisor scene-tree access** — each robot reads the positions and headings
  of its neighbors directly from the Webots scene tree. No radio, no map.
- **Emergent behavior** — no robot is told to form a flock. The flock forms
  because each robot independently follows the same local rules.
- **Multi-agent systems** — N identical controllers running in parallel on N
  separate robots, each acting on partial information.
- **Proximity-sensor wall avoidance** — the e-puck's built-in IR sensors keep
  the flock inside the arena without explicit boundary logic.

## The Three Boids Rules

| Rule | What it does | Effect |
|------|-------------|--------|
| **Separation** | Steer away from neighbors closer than `SEP_RANGE` | Prevents collisions |
| **Cohesion** | Steer toward the average position of visible neighbors | Keeps the flock together |
| **Alignment** | Match the average heading of visible neighbors | Makes the group move as one |

Each rule produces a direction vector in world frame. The three are combined as
a weighted sum, normalized, then added to the wall-avoidance vector from the IR
sensors. The result is converted to a heading error and applied as a differential
wheel command.

## Environment

A 4 m x 4 m open arena with two static cylindrical obstacles. The robots start
clustered in the center so they immediately form a flock. Once flocking, they
roam the arena collectively, splitting around obstacles and reforming.

## Project structure

```
swarm-flocking/
├── worlds/
│   └── swarm_flock.wbt              # 4m arena, 2 obstacles, 5 e-puck robots
├── controllers/
│   └── swarm_flock/
│       └── swarm_flock.py           # Reynolds Boids controller (identical for all robots)
└── README.md
```

## How to run

1. Open **Webots** (R2023b or newer).
2. `File > Open World...` and select `worlds/swarm_flock.wbt`.
   - First open downloads the e-puck PROTO assets, so stay online.
3. Press **Play**. All five robots start moving. Within a few seconds they
   align headings, form a loose cluster, and move through the arena together.
   The console prints each robot's visible-neighbor count and heading every
   ~1.6 seconds.

## How it works (per timestep, per robot)

1. Read own position and heading from the **Webots scene tree** (`getSelf()`,
   `getPosition()`, `getOrientation()`).
2. For each of the other 4 robots, read their position and heading the same way
   (`getFromDef("ROBOT_i")`). Collect those within `VISION_RANGE` as neighbors.
3. Compute three unit vectors:
   - **Separation**: average push-away direction from neighbors within `SEP_RANGE`.
   - **Cohesion**: direction toward the centroid of all visible neighbors.
   - **Alignment**: average heading of all visible neighbors (as a unit vector).
4. Weighted sum -> normalize -> target direction.
5. Read 8 IR proximity sensors. For any sensor above `PS_WALL_THR`, subtract a
   scaled vector in that sensor's world-frame direction (pushes away from walls).
6. Normalize combined vector, compute heading error vs. current yaw.
7. Differential wheel speeds: slow when turning sharply, cruise when aligned.

## Tuning

All weights live at the top of `swarm_flock.py`:

| Knob | Default | Effect |
|------|---------|--------|
| `W_SEP` | 3.0 | Raise to spread robots further apart |
| `W_COH` | 0.8 | Raise to clump them tighter |
| `W_ALI` | 1.2 | Raise to synchronize headings faster |
| `W_WALL` | 5.0 | Raise if robots are clipping walls |
| `VISION_RANGE` | 1.5 m | How far a robot can "see" its neighbors |
| `SEP_RANGE` | 0.25 m | Minimum comfortable inter-robot distance |
| `CRUISE` | 3.5 | Base forward speed |
| `TURN_GAIN` | 4.0 | Steering aggression |

### Experiments to try
- Set `W_COH = 0`, `W_ALI = 0` — robots only avoid each other (pure separation = random scatter).
- Set `W_SEP = 0` — robots pile up on top of each other.
- Set `W_ALI = 5.0` — robots snap to the same heading almost instantly but cohesion weakens.
- Reduce `VISION_RANGE` to 0.5 — flock fragments because robots can only see immediate neighbors.
- Add a 6th robot by duplicating a `DEF ROBOT_5 E-puck` in the world and setting `N_ROBOTS = 6`.

## Why this is different from the LiDAR navigation project

| | LiDAR Navigation | Swarm Flocking |
|--|-----------------|---------------|
| Robots | 1 | 5 |
| Has a goal | Yes (beacon) | No |
| Sensing | Laser rangefinder | IR proximity + scene tree |
| Algorithm | Gap-seeking VFH | Reynolds Boids |
| Behavior type | Goal-directed reactive | Emergent collective |
| What to watch | Robot threading doorway | Flock forming and roaming |

## Acceptance check

Within 10 seconds of pressing Play, all five robots are moving together as a loose
cluster with roughly aligned headings. When the group approaches a wall or obstacle,
it bends around it and reforms. No robot gets permanently stuck. The console shows
each robot reporting 3-4 visible neighbors steadily.
