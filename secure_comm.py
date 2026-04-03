import random
import hashlib
import time

# ─────────────────────────────────────────
# BB84 QUANTUM KEY DISTRIBUTION SIMULATOR
# ─────────────────────────────────────────

BASES = ['+', 'x']          # Rectilinear vs Diagonal
BITS  = ['0', '1']

def generate_photons(n=64):
    """
    Alice generates random bits + random bases
    Like a real QKD transmitter satellite
    """
    bits  = [random.choice(BITS)  for _ in range(n)]
    bases = [random.choice(BASES) for _ in range(n)]
    return bits, bases


def measure_photons(bits, alice_bases, eve_present=False):
    """
    Bob measures incoming photons with random bases.
    If Eve intercepts → introduces errors (QBER rises)
    """
    bob_bases = [random.choice(BASES) for _ in range(len(bits))]
    bob_bits  = []

    for i in range(len(bits)):
        if eve_present and random.random() < 0.5:
            # Eve intercepts → random guess → 50% error
            bob_bits.append(random.choice(BITS))
        elif alice_bases[i] == bob_bases[i]:
            # Bases match → correct bit received
            bob_bits.append(bits[i])
        else:
            # Bases mismatch → random bit
            bob_bits.append(random.choice(BITS))

    return bob_bits, bob_bases


def sift_key(alice_bits, alice_bases, bob_bits, bob_bases):
    """
    Keep only bits where bases matched
    This is the real BB84 sifting step
    """
    sifted_alice = []
    sifted_bob   = []

    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])

    return sifted_alice, sifted_bob


def calculate_qber(alice_key, bob_key):
    """
    Quantum Bit Error Rate
    QBER > 11% = Eve detected = abort session
    """
    if not alice_key:
        return 0.0
    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    return round(errors / len(alice_key), 4)


def generate_key(length=64):
    """
    Generate secure quantum-inspired key
    Uses BB84 sifted bits → SHA256 hash
    """
    bits, alice_bases = generate_photons(length)
    bob_bits, bob_bases = measure_photons(bits, alice_bases)
    sifted_alice, _ = sift_key(bits, alice_bases, bob_bits, bob_bases)

    # Convert bits to string → hash for final key
    raw = ''.join(sifted_alice)
    if not raw:
        raw = str(time.time())

    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return key_hash


def simulate_qkd(key, threat="Low"):
    """
    Full BB84 simulation with threat scenarios:
    Low    → Normal operation  → QBER ~3%
    Medium → Noise/interference → QBER ~8%
    High   → Eve attacking      → QBER ~25%
    """
    # Eve presence based on threat
    eve_present = threat == "High"

    # Run BB84
    alice_bits, alice_bases = generate_photons(128)
    bob_bits, bob_bases = measure_photons(
        alice_bits,
        alice_bases,
        eve_present=eve_present
    )
    sifted_alice, sifted_bob = sift_key(
        alice_bits, alice_bases,
        bob_bits,   bob_bases
    )
    qber = calculate_qber(sifted_alice, sifted_bob)

    # Add noise for Medium threat
    if threat == "Medium":
        qber = max(qber, 0.06 + random.uniform(0, 0.04))

    # Determine status
    if qber > 0.11:
        status = "🚨 EAVESDROPPER DETECTED — Session Aborted"
        secure = False
    elif qber > 0.05:
        status = "⚠️ Channel Degraded — Switching to Kyber PQC"
        secure = True
    else:
        status = "✅ Quantum Channel Secure"
        secure = True

    return {
        "QBER":           round(qber, 4),
        "status":         status,
        "secure":         secure,
        "key_preview":    key[:16] + "...",
        "sifted_bits":    len(sifted_alice),
        "key_rate_bps":   len(sifted_alice) * 10,
        "protocol":       "BB84" if secure else "Kyber-768 (Fallback)",
        "threat_level":   threat
    }


def laser_link_status(sat_distance):
    """
    Check if laser link is possible between 2 satellites
    Based on distance (in our simulation units)
    """
    if sat_distance < 0.3:
        return {
            "link": "✅ Strong",
            "signal_strength": round(1.0 - sat_distance, 3),
            "feasible": True
        }
    elif sat_distance < 0.6:
        return {
            "link": "⚠️ Weak",
            "signal_strength": round(0.5 - sat_distance * 0.3, 3),
            "feasible": True
        }
    else:
        return {
            "link": "❌ Out of Range",
            "signal_strength": 0.0,
            "feasible": False
        }
