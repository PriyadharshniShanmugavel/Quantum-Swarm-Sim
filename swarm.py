import numpy as np


# BOIDS PARAMETERS

SEPARATION_RADIUS = 0.15   # Too close → push away
ALIGNMENT_RADIUS  = 0.4    # Match neighbors velocity
COHESION_RADIUS   = 0.5    # Move toward group center
DEBRIS_AVOID_RADIUS = 0.2  # Run from debris!

SEPARATION_WEIGHT = 0.08
ALIGNMENT_WEIGHT  = 0.04
COHESION_WEIGHT   = 0.01
DEBRIS_WEIGHT     = 0.15   # Strongest force!

MAX_SPEED         = 0.02
ORBIT_RADIUS      = 0.7    # Keep satellites in orbit

def initialize_swarm(n=5):
    """
    Initialize satellites evenly distributed
    around orbital ring (not random scatter)
    """
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    positions = np.column_stack([
        ORBIT_RADIUS * np.cos(angles),
        ORBIT_RADIUS * np.sin(angles)
    ])
    # Velocities perpendicular to orbit (circular motion)
    velocities = np.column_stack([
        -np.sin(angles),
        np.cos(angles)
    ]) * 0.01

    return positions, velocities


def separation(positions, i):
    """Push away from too-close neighbors"""
    force = np.zeros(2)
    for j, pos in enumerate(positions):
        if i == j:
            continue
        diff = positions[i] - pos
        dist = np.linalg.norm(diff)
        if 0 < dist < SEPARATION_RADIUS:
            force += diff / (dist ** 2)  # stronger when closer
    return force


def alignment(positions, velocities, i):
    """Match velocity of nearby neighbors"""
    avg_vel = np.zeros(2)
    count = 0
    for j, pos in enumerate(positions):
        if i == j:
            continue
        dist = np.linalg.norm(positions[i] - pos)
        if dist < ALIGNMENT_RADIUS:
            avg_vel += velocities[j]
            count += 1
    if count > 0:
        avg_vel /= count
        return avg_vel - velocities[i]
    return avg_vel


def cohesion(positions, i):
    """Steer toward center of nearby neighbors"""
    center = np.zeros(2)
    count = 0
    for j, pos in enumerate(positions):
        if i == j:
            continue
        dist = np.linalg.norm(positions[i] - pos)
        if dist < COHESION_RADIUS:
            center += pos
            count += 1
    if count > 0:
        center /= count
        return center - positions[i]
    return center


def avoid_debris(positions, debris, i):
    """CRITICAL: Steer hard away from debris"""
    force = np.zeros(2)
    for d in debris:
        diff = positions[i] - d
        dist = np.linalg.norm(diff)
        if 0 < dist < DEBRIS_AVOID_RADIUS:
            force += diff / (dist ** 2)
    return force


def orbital_correction(position):
    """
    Gentle force to keep satellite near
    orbital ring (not drift into Earth or space)
    """
    dist_from_center = np.linalg.norm(position)
    correction = ORBIT_RADIUS - dist_from_center
    direction = position / (dist_from_center + 1e-6)
    return direction * correction * 0.005


def limit_speed(velocity, max_speed=MAX_SPEED):
    speed = np.linalg.norm(velocity)
    if speed > max_speed:
        return velocity / speed * max_speed
    return velocity


def update_swarm(positions, velocities, debris=None):
    """
    Full Boids update:
    Separation + Alignment + Cohesion + Debris Avoidance
    """
    new_velocities = velocities.copy()

    for i in range(len(positions)):
        sep = separation(positions, i)
        ali = alignment(positions, velocities, i)
        coh = cohesion(positions, i)
        orb = orbital_correction(positions[i])

        # Debris avoidance (strongest force)
        deb = np.zeros(2)
        if debris is not None:
            deb = avoid_debris(positions, debris, i)

        # Combine all forces
        new_velocities[i] += (
            sep * SEPARATION_WEIGHT +
            ali * ALIGNMENT_WEIGHT +
            coh * COHESION_WEIGHT +
            deb * DEBRIS_WEIGHT +
            orb
        )

        # Speed limit
        new_velocities[i] = limit_speed(new_velocities[i])

    new_positions = positions + new_velocities

    return new_positions, new_velocities


def get_collision_warnings(positions, debris):
    """
    Returns list of (satellite_idx, debris_idx, distance)
    for any dangerous close approaches
    """
    warnings = []
    for i, sat in enumerate(positions):
        for j, deb in enumerate(debris):
            dist = np.linalg.norm(sat - deb)
            if dist < DEBRIS_AVOID_RADIUS:
                warnings.append({
                    "satellite": i + 1,
                    "debris": j + 1,
                    "distance_km": round(dist * 1000, 2),
                    "threat": "🚨 CRITICAL" if dist < 0.1 else "⚠️ WARNING"
                })
    return warnings
