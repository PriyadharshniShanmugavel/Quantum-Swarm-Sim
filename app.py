import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from swarm import initialize_swarm, update_swarm, get_collision_warnings
from debris import generate_debris, update_debris, get_debris_positions
from secure_comm import generate_key, simulate_qkd

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="NakshatraNet",
    page_icon="🛸",
    layout="wide"
)

# ─────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────
st.title("🛸 NakshatraNet — Quantum Swarm Debris Shield")
st.caption("Autonomous Debris Mapping via Inter-Satellite QKD Laser Network | National Space Hackathon 2026")

# ─────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────
st.sidebar.header("⚙️ Mission Control")
num_satellites = st.sidebar.slider("Number of Satellites", 3, 10, 5)
threat_level   = st.sidebar.selectbox("Threat Level", ["Low", "Medium", "High"])
auto_run       = st.sidebar.checkbox("🔴 Live Mode (Auto Update)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🇮🇳 ISRO Mission Relevance")
st.sidebar.info(
    "🚀 Gaganyaan — Secure crew comms\n\n"
    "🛰️ SpaDeX — Debris mapping\n\n"
    "🌍 DFSM 2030 — Debris-free orbits"
)

# ─────────────────────────────────────────
# INITIALIZE SESSION STATE
# ─────────────────────────────────────────
if "positions" not in st.session_state:
    pos, vel = initialize_swarm(num_satellites)
    st.session_state.positions     = pos
    st.session_state.velocities    = vel
    st.session_state.debris        = generate_debris()
    st.session_state.step          = 0
    st.session_state.qber_history  = []
    st.session_state.alert_history = []

# Reset button
if st.sidebar.button("🔄 Reset Mission"):
    pos, vel = initialize_swarm(num_satellites)
    st.session_state.positions     = pos
    st.session_state.velocities    = vel
    st.session_state.debris        = generate_debris()
    st.session_state.step          = 0
    st.session_state.qber_history  = []
    st.session_state.alert_history = []

# ─────────────────────────────────────────
# COLUMNS LAYOUT
# ─────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌍 Live Orbital Map")

    # ── Simulation Update ──
    if st.button("⏭️ Next Step") or auto_run:

        # 1. Move debris
        st.session_state.debris = update_debris(
            st.session_state.debris
        )

        # 2. Get debris positions for swarm
        debris_pos = get_debris_positions(st.session_state.debris)

        # 3. Update swarm WITH debris awareness
        pos, vel = update_swarm(
            st.session_state.positions,
            st.session_state.velocities,
            debris_pos
        )
        st.session_state.positions  = pos
        st.session_state.velocities = vel
        st.session_state.step      += 1

        # 4. QKD update
        key    = generate_key()
        result = simulate_qkd(key, threat=threat_level)
        st.session_state.qber_history.append(result["QBER"])

        # 5. Alert log
        warnings = get_collision_warnings(
            st.session_state.positions, debris_pos
        )
        if warnings:
            st.session_state.alert_history.append(
                f"Step {st.session_state.step}: "
                f"{len(warnings)} collision warning(s)!"
            )

    # ── PLOT ──
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0a0a2e')
    ax.set_facecolor('#0a0a2e')

    # Earth
    earth = plt.Circle((0, 0), 0.15, color='#1a6b3c', zorder=5)
    ax.add_patch(earth)
    ax.text(0, 0, '🌍', ha='center', va='center', fontsize=20, zorder=6)

    # Orbital ring
    orbit_ring = plt.Circle(
        (0, 0), 0.7,
        fill=False,
        color='gray',
        linestyle='--',
        alpha=0.3
    )
    ax.add_patch(orbit_ring)

    # Laser links between satellites
    for i in range(len(st.session_state.positions)):
        for j in range(i + 1, len(st.session_state.positions)):
            ax.plot(
                [st.session_state.positions[i, 0],
                 st.session_state.positions[j, 0]],
                [st.session_state.positions[i, 1],
                 st.session_state.positions[j, 1]],
                'cyan', alpha=0.15, linewidth=0.8
            )

    # Satellites
    ax.scatter(
        st.session_state.positions[:, 0],
        st.session_state.positions[:, 1],
        color='cyan', s=120,
        label='🛰️ Satellites',
        zorder=10
    )

    # Label each satellite
    for i, pos in enumerate(st.session_state.positions):
        ax.text(
            pos[0] + 0.03, pos[1] + 0.03,
            f"S{i+1}",
            color='cyan', fontsize=7, zorder=11
        )

    # Debris with threat colors
    for d in st.session_state.debris:
        ax.scatter(
            d["position"][0],
            d["position"][1],
            color=d["color"],
            marker='x',
            s=80,
            zorder=9
        )

    # Legend manually
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor='cyan',    label='🛰️ Satellite',    markersize=8),
        Line2D([0], [0], marker='x', color='red',
               label='🔴 Critical Debris',  markersize=8, linewidth=2),
        Line2D([0], [0], marker='x', color='orange',
               label='🟠 High Debris',       markersize=8, linewidth=2),
        Line2D([0], [0], marker='x', color='yellow',
               label='🟡 Medium Debris',     markersize=8, linewidth=2),
        Line2D([0], [0], marker='x', color='white',
               label='⚪ Low Debris',        markersize=8, linewidth=2),
    ]
    ax.legend(
        handles=legend_elements,
        facecolor='#0a0a2e',
        labelcolor='white',
        loc='upper right',
        fontsize=8
    )

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_title(
        f"Step {st.session_state.step} — "
        f"{len(st.session_state.debris)} Debris Tracked",
        color='white', fontsize=13
    )
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333366')

    st.pyplot(fig)

# ─────────────────────────────────────────
# RIGHT COLUMN
# ─────────────────────────────────────────
with col2:

    # ── QKD Status ──
    st.subheader("🔐 Quantum Link Status")
    key    = generate_key()
    result = simulate_qkd(key, threat=threat_level)

    if result["QBER"] < 0.05:
        st.success(f"✅ SECURE — QBER: {result['QBER']:.3f}")
    elif result["QBER"] < 0.11:
        st.warning(f"⚠️ DEGRADED — QBER: {result['QBER']:.3f}")
    else:
        st.error(f"🚨 ATTACK DETECTED — QBER: {result['QBER']:.3f}")

    st.code(f"🔑 Key: {result['key_preview']}", language="text")
    st.caption(f"Protocol: {result['protocol']}")
    st.caption(f"Key Rate: {result['key_rate_bps']} bps")

    st.markdown("---")

    # ── Mission Metrics ──
    st.subheader("📊 Mission Stats")

    debris_pos = get_debris_positions(st.session_state.debris)
    warnings   = get_collision_warnings(
        st.session_state.positions, debris_pos
    )

    col_a, col_b = st.columns(2)
    col_a.metric("🛰️ Satellites",  len(st.session_state.positions))
    col_b.metric("☄️ Debris",      len(st.session_state.debris))
    col_a.metric("📍 Step",        st.session_state.step)
    col_b.metric("⚠️ Warnings",    len(warnings))

    # Overall health
    if len(warnings) == 0:
        st.success("🟢 Mission: NOMINAL")
    else:
        st.error(f"🔴 Mission: ALERT — {len(warnings)} threat(s)!")

    st.markdown("---")

    # ── QBER History Chart ──
    if len(st.session_state.qber_history) > 1:
        st.subheader("📈 QBER History")
        st.line_chart(st.session_state.qber_history)
        st.caption("Spikes = Eavesdropper attack detected")

    st.markdown("---")

    # ── Alert Log ──
    st.subheader("🚨 Alert Log")
    if st.session_state.alert_history:
        for alert in st.session_state.alert_history[-5:]:
            st.warning(alert)
    else:
        st.success("✅ No alerts yet")

    st.markdown("---")

    # ── Debris Table ──
    st.subheader("☄️ Critical Debris")
    critical = [
        d for d in st.session_state.debris
        if d["threat"] in ["CRITICAL", "HIGH"]
    ]
    for d in critical[:5]:
        st.markdown(
            f"**{d['name']}** — {d['threat']} "
            f"({d['size']}m)"
        )
