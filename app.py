import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from swarm import initialize_swarm, update_swarm
from debris import generate_debris
from secure_comm import generate_key, simulate_qkd

# Page Config
st.set_page_config(
    page_title="NakshatraNet",
    page_icon="🛸",
    layout="wide"
)

# Title
st.title("🛸 NakshatraNet — Quantum Swarm Debris Shield")
st.caption("Autonomous Debris Mapping via Inter-Satellite QKD Laser Network")

# Sidebar Controls
st.sidebar.header("⚙️ Mission Control")
num_satellites = st.sidebar.slider("Number of Satellites", 3, 10, 5)
threat_level = st.sidebar.selectbox("Threat Level", ["Low", "Medium", "High"])
auto_run = st.sidebar.checkbox("🔴 Live Mode (Auto Update)")

# Initialize
if "positions" not in st.session_state:
    pos, vel = initialize_swarm(num_satellites)
    st.session_state.positions = pos
    st.session_state.velocities = vel
    st.session_state.debris = generate_debris()
    st.session_state.step = 0
    st.session_state.qber_history = []

# Columns Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌍 Live Orbital Map")

    # Update simulation
    if st.button("⏭️ Next Step") or auto_run:
        pos, vel = update_swarm(
            st.session_state.positions,
            st.session_state.velocities
        )
        st.session_state.positions = pos
        st.session_state.velocities = vel
        st.session_state.step += 1

    # BETTER PLOT
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0a0a2e')  # Space background
    ax.set_facecolor('#0a0a2e')

    # Draw Earth
    earth = plt.Circle((0, 0), 0.15, color='#1a6b3c', zorder=5)
    ax.add_patch(earth)
    ax.text(0, 0, '🌍', ha='center', va='center', fontsize=20, zorder=6)

    # Draw orbital ring
    orbit_ring = plt.Circle(
        (0, 0), 0.7,
        fill=False,
        color='gray',
        linestyle='--',
        alpha=0.3
    )
    ax.add_patch(orbit_ring)

    # Satellites with trails
    ax.scatter(
        st.session_state.positions[:, 0],
        st.session_state.positions[:, 1],
        color='cyan', s=100,
        label='🛰️ Satellites',
        zorder=10
    )

    # Draw laser links between satellites
    for i in range(len(st.session_state.positions)):
        for j in range(i+1, len(st.session_state.positions)):
            ax.plot(
                [st.session_state.positions[i,0],
                 st.session_state.positions[j,0]],
                [st.session_state.positions[i,1],
                 st.session_state.positions[j,1]],
                'cyan', alpha=0.15, linewidth=0.8
            )

    # Debris
    ax.scatter(
        st.session_state.debris[:, 0],
        st.session_state.debris[:, 1],
        color='red', marker='x', s=80,
        label='☄️ Debris',
        zorder=9
    )

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.legend(facecolor='#0a0a2e', labelcolor='white')
    ax.set_title(
        f"Step {st.session_state.step} — "
        f"{len(st.session_state.debris)} Debris Tracked",
        color='white'
    )
    ax.tick_params(colors='white')
    st.pyplot(fig)

with col2:
    st.subheader("🔐 Quantum Link Status")

    key = generate_key()
    result = simulate_qkd(key)

    # Store QBER history
    st.session_state.qber_history.append(result["QBER"])

    # Status color
    if result["QBER"] < 0.05:
        st.success(f"✅ Link SECURE — QBER: {result['QBER']:.3f}")
    elif result["QBER"] < 0.11:
        st.warning(f"⚠️ Link DEGRADED — QBER: {result['QBER']:.3f}")
    else:
        st.error(f"🚨 ATTACK DETECTED — QBER: {result['QBER']:.3f}")

    st.code(f"🔑 Key: {key[:20]}...", language="text")

    # Metrics
    st.subheader("📊 Mission Stats")
    st.metric("Satellites Active", len(st.session_state.positions))
    st.metric("Debris Tracked", len(st.session_state.debris))
    st.metric("Mission Step", st.session_state.step)
    st.metric("Quantum Keys Generated", st.session_state.step + 1)

    # QBER Chart
    if len(st.session_state.qber_history) > 1:
        st.subheader("📈 QBER History")
        st.line_chart(st.session_state.qber_history)
