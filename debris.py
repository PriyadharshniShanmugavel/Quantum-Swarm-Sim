import numpy as np

# ─────────────────────────────────────────
# DEBRIS CLASSIFICATION
# ─────────────────────────────────────────
DEBRIS_TYPES = {
    "rocket_body": {
        "size_m": 8.0,
        "color": "red",
        "threat": "CRITICAL",
        "orbital_speed": 0.008
    },
    "dead_satellite": {
        "size_m": 2.0,
        "color": "orange",
        "threat": "HIGH",
        "orbital_speed": 0.007
    },
    "fragment": {
        "size_m": 0.1,
        "color": "yellow",
        "threat": "MEDIUM",
        "orbital_speed": 0.009
    },
    "microparticle": {
        "size_m": 0.01,
        "color": "white",
        "threat": "LOW",
        "orbital_speed": 0.006
    }
}

# Real ISRO debris objects (simulated TLE-inspired)
KNOWN_ISRO_DEBRIS = [
    {"name": "PSLV-C37 Stage",   "angle": 0.52,  "radius": 0.68, "type": "rocket_body"},
    {"name": "RISAT Fragment",    "angle": 1.89,  "radius": 0.72, "type": "fragment"},
    {"name": "Cartosat Debris",   "angle": 3.14,  "radius": 0.71, "type": "dead_satellite"},
    {"name": "GSAT Fragment",     "angle": 4.71,  "radius": 0.69, "type": "fragment"},
    {"name": "SpaDeX Residue",    "angle": 5.50,  "radius": 0.73, "type": "microparticle"},
]


def generate_debris(n=15, include_known=True):
    """
    Generate debris field:
    - Real ISRO-named objects (for realism)
    - Random fragments (for density)
    Both orbiting at realistic speeds
    """
    debris_list = []

    # ── Known ISRO debris first ──
    if include_known:
        for obj in KNOWN_ISRO_DEBRIS:
            dtype = DEBRIS_TYPES[obj["type"]]
            x = obj["radius"] * np.cos(obj["angle"])
            y = obj["radius"] * np.sin(obj["angle"])

            # Orbital velocity (perpendicular to radius)
            vx = -np.sin(obj["angle"]) * dtype["orbital_speed"]
            vy =  np.cos(obj["angle"]) * dtype["orbital_speed"]

            debris_list.append({
                "name":     obj["name"],
                "position": np.array([x, y]),
                "velocity": np.array([vx, vy]),
                "type":     obj["type"],
                "size":     dtype["size_m"],
                "color":    dtype["color"],
                "threat":   dtype["threat"]
            })

    # ── Random fragments ──
    remaining = n - len(debris_list)
    types = list(DEBRIS_TYPES.keys())
    weights = [0.1, 0.2, 0.4, 0.3]  # more fragments/microparticles

    for _ in range(remaining):
        dtype_name = np.random.choice(types, p=weights)
        dtype = DEBRIS_TYPES[dtype_name]

        angle  = np.random.uniform(0, 2 * np.pi)
        radius = np.random.normal(0.7, 0.12)
        radius = np.clip(radius, 0.4, 1.0)

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        vx = -np.sin(angle) * dtype["orbital_speed"]
        vy =  np.cos(angle) * dtype["orbital_speed"]

        debris_list.append({
            "name":     f"Fragment-{np.random.randint(1000,9999)}",
            "position": np.array([x, y]),
            "velocity": np.array([vx, vy]),
            "type":     dtype_name,
            "size":     dtype["size_m"],
            "color":    dtype["color"],
            "threat":   dtype["threat"]
        })

    return debris_list


def update_debris(debris_list):
    """
    Move debris along orbital path each step
    """
    for obj in debris_list:
        obj["position"] += obj["velocity"]

        # Keep in orbital zone
        dist = np.linalg.norm(obj["position"])
        if dist > 1.1 or dist < 0.3:
            obj["velocity"] *= -1

    return debris_list


def get_debris_positions(debris_list):
    """Extract just positions array for swarm calculations"""
    return np.array([d["position"] for d in debris_list])


def get_critical_debris(debris_list):
    """Return only high-threat objects"""
    return [d for d in debris_list if d["threat"] in ["CRITICAL", "HIGH"]]


def get_debris_catalog(debris_list):
    """
    API-ready debris catalog
    Returns clean dict for /debris_catalog endpoint
    """
    return [
        {
            "name":     d["name"],
            "type":     d["type"],
            "threat":   d["threat"],
            "size_m":   d["size"],
            "position": {
                "x": round(float(d["position"][0]), 4),
                "y": round(float(d["position"][1]), 4)
            }
        }
        for d in debris_list
    ]
