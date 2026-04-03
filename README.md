# Quantum Swarm Sim (NakshatraNet)
Quantum-Swarm: Autonomous Debris Mapping with Secure Inter-Satellite Communication
# 🛸 NakshatraNet — Quantum Swarm Debris Shield

> *"Every hackathon team protects the spacecraft. We protect the orbital environment it flies in."*

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**National Space Hackathon 2026 | IIT Delhi | Team:  Quantum Swarm Sim (NakshatraNet)**

---

## Problem Statement

India's orbital environment faces a **dual crisis**:
- **129+ debris objects** from ISRO missions (PSLV stages, dead satellites, fragments)
- **Classical encryption** becomes obsolete by 2028 — threatening Gaganyaan communications
- Current ground radars track debris **centrally** — single point of failure
- No real-time **satellite-to-satellite** secure coordination exists

---

## Solution: Quantum Swarm Sim (NakshatraNet)

An autonomous **10-satellite swarm** that:

- Self-organizes using **Boids flocking intelligence**
- Detects and maps debris using distributed scanning
- Communicates via **BB84 Quantum Key Distribution** laser links
- Detects eavesdroppers when **QBER > 11%**
- Falls back to **Kyber-768 Post-Quantum Cryptography** on attack
- Exposes real-time data via **REST API**

---

## Project Structure
    quantum-swarm-sim
├── app.py
├── swarm.py
├── debris.py
├── secure_comm.py
├── api.py
├── requirements.txt
├── README.md
---

## Core Algorithms

### 1. Boids Swarm Intelligence
Three forces keep satellites organized:
- **Separation** — avoid crowding neighbors
- **Alignment** — match neighbor velocities  
- **Cohesion** — steer toward group center
- **Debris Avoidance** — strongest force, overrides all

### 2. BB84 Quantum Key Distribution
      Alice (SatA) → Random bits + bases → Laser → Bob (SatB)
      Bob measures with random bases → Sifting → Shared key
      QBER calculated → If > 11% → Eve detected → Session aborted
      Fallback → Kyber-768 Post-Quantum Cryptography

### 3.  Debris Catalog
Real ISRO-inspired debris objects:
| Object | Type | Threat |
|---|---|---|
| PSLV-C37 Stage | Rocket Body | 🔴 CRITICAL |
| Cartosat Debris | Dead Satellite | 🟠 HIGH |
| RISAT Fragment | Fragment | 🟡 MEDIUM |
| SpaDeX Residue | Microparticle | ⚪ LOW |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Mission status |
| `/swarm` | GET | Initialize swarm |
| `/swarm/update` | GET | Step simulation |
| `/debris/catalog` | GET | Full debris list |
| `/debris/critical` | GET | High threat only |
| `/secure?threat=High` | GET | QKD + Eve attack sim |
| `/laser_link?sat1=0&sat2=1` | GET | Link quality check |
| `/collision_warnings` | GET | Close approaches |
| `/mission_status` | GET | Full health summary |

---
## Setup & Run

### 1. Clone Repository
```bash
git clone https://github.com/username/Quantum-Swarm-Sim.git
cd Quantum-Swarm-Sim
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Dashboard
```bash
streamlit run app.py
```

### 4. Run API (separate terminal)
```bash
uvicorn api:app --reload
```

### 5. View API Docs
http://localhost:8000/docs
---

## Live Demo Walkthrough

1. Open dashboard → 5 satellites orbit Earth
2. Click **Next Step** → satellites avoid debris in real-time
3. Watch **laser links** form between satellites (cyan lines)
4. Set threat to **High** → QBER spikes → *"Eavesdropper Detected!"*
5. System auto-switches to **Kyber-768 fallback**
6. Check `/mission_status` API → full health report

---

## 🇮🇳 ISRO Relevance

| ISRO Mission | How Quantum Swarm Sim Helps |
|---|---|
| **Gaganyaan** | Quantum-secure crew communications |
| **SpaDeX** | Debris mapping around docking zone |
| **DFSM 2030** | Autonomous debris-free orbital corridors |
| **PSLV Legacy** | Tracks and maps own rocket body debris |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Dashboard | Streamlit |
| API | FastAPI + Uvicorn |
| Simulation | NumPy + Matplotlib |
| Swarm AI | Boids Algorithm |
| Quantum Sim | BB84 + Kyber-768 |
| Language | Python 3.10+ |

---

## License
MIT License — Open for ISRO collaboration
