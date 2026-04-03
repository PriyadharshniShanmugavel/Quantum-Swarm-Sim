from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from swarm import initialize_swarm, update_swarm, get_collision_warnings
from debris import (generate_debris, update_debris,
                    get_debris_positions, get_debris_catalog,
                    get_critical_debris)
from secure_comm import generate_key, simulate_qkd, laser_link_status

app = FastAPI(
    title="NakshatraNet API",
    description="Quantum Swarm Debris Shield — ISRO Hackathon 2026",
    version="1.0.0"
)

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────
# SHARED STATE (persists between requests)
# ─────────────────────────────────────────
state = {
    "positions": None,
    "velocities": None,
    "debris": None,
    "step": 0
}

def ensure_initialized(n=5):
    if state["positions"] is None:
        state["positions"], state["velocities"] = initialize_swarm(n)
        state["debris"] = generate_debris()
        state["step"] = 0


# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────

@app.get("/")
def home():
    return {
        "mission": "NakshatraNet 🛸",
        "status":  "API Online",
        "version": "1.0.0",
        "endpoints": [
            "/swarm",
            "/swarm/update",
            "/debris/catalog",
            "/debris/critical",
            "/secure",
            "/collision_warnings",
            "/mission_status"
        ]
    }


@app.get("/swarm")
def get_swarm(n: int = Query(default=5, ge=3, le=10)):
    """Initialize and return swarm positions"""
    ensure_initialized(n)
    return {
        "satellites":  len(state["positions"]),
        "positions":   state["positions"].tolist(),
        "velocities":  state["velocities"].tolist(),
        "step":        state["step"]
    }


@app.get("/swarm/update")
def update_swarm_step():
    """Advance simulation by one step"""
    ensure_initialized()
    debris_pos = get_debris_positions(state["debris"])

    state["positions"], state["velocities"] = update_swarm(
        state["positions"],
        state["velocities"],
        debris_pos
    )
    state["debris"] = update_debris(state["debris"])
    state["step"] += 1

    warnings = get_collision_warnings(state["positions"], debris_pos)

    return {
        "step":             state["step"],
        "positions":        state["positions"].tolist(),
        "collision_warnings": warnings,
        "debris_avoided":   len(warnings) == 0
    }


@app.get("/debris/catalog")
def debris_catalog():
    """Full debris catalog with threat levels"""
    ensure_initialized()
    return {
        "total_objects": len(state["debris"]),
        "catalog":       get_debris_catalog(state["debris"])
    }


@app.get("/debris/critical")
def critical_debris():
    """Only CRITICAL and HIGH threat debris"""
    ensure_initialized()
    critical = get_critical_debris(state["debris"])
    return {
        "critical_count": len(critical),
        "objects": [
            {
                "name":   d["name"],
                "threat": d["threat"],
                "size_m": d["size"],
                "position": {
                    "x": round(float(d["position"][0]), 4),
                    "y": round(float(d["position"][1]), 4)
                }
            }
            for d in critical
        ]
    }


@app.get("/secure")
def secure_comms(threat: str = Query(default="Low",
                                     enum=["Low", "Medium", "High"])):
    """
    Simulate QKD between two satellites.
    threat=High → Eve attack → QBER spikes
    """
    key    = generate_key()
    result = simulate_qkd(key, threat=threat)
    return {
        "key_preview":    result["key_preview"],
        "QBER":           result["QBER"],
        "status":         result["status"],
        "secure":         result["secure"],
        "protocol":       result["protocol"],
        "key_rate_bps":   result["key_rate_bps"],
        "sifted_bits":    result["sifted_bits"],
        "threat_simulated": threat
    }


@app.get("/collision_warnings")
def collision_warnings():
    """Check all satellite-debris close approaches"""
    ensure_initialized()
    debris_pos = get_debris_positions(state["debris"])
    warnings   = get_collision_warnings(state["positions"], debris_pos)
    return {
        "total_warnings": len(warnings),
        "safe":           len(warnings) == 0,
        "warnings":       warnings
    }


@app.get("/laser_link")
def check_laser_link(sat1: int = Query(default=0, ge=0),
                     sat2: int = Query(default=1, ge=0)):
    """Check QKD laser link quality between two satellites"""
    ensure_initialized()
    n = len(state["positions"])
    if sat1 >= n or sat2 >= n:
        return {"error": f"Satellite index out of range (max {n-1})"}

    dist = float(np.linalg.norm(
        state["positions"][sat1] - state["positions"][sat2]
    ))
    link = laser_link_status(dist)
    return {
        "satellite_1":      sat1,
        "satellite_2":      sat2,
        "distance_units":   round(dist, 4),
        "link_status":      link["link"],
        "signal_strength":  link["signal_strength"],
        "qkd_feasible":     link["feasible"]
    }


@app.get("/mission_status")
def mission_status():
    """Overall mission health summary"""
    ensure_initialized()
    debris_pos = get_debris_positions(state["debris"])
    warnings   = get_collision_warnings(state["positions"], debris_pos)
    critical   = get_critical_debris(state["debris"])
    key        = generate_key()
    qkd        = simulate_qkd(key)

    return {
        "mission":          "NakshatraNet 🛸",
        "step":             state["step"],
        "satellites":       len(state["positions"]),
        "debris_tracked":   len(state["debris"]),
        "critical_threats": len(critical),
        "collision_warnings": len(warnings),
        "quantum_status":   qkd["status"],
        "overall_health":   "🟢 NOMINAL" if len(warnings) == 0 else "🔴 ALERT"
    }
