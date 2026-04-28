"""
╔══════════════════════════════════════════════════════════════╗
║   STUDI KASUS 2 — Permainan Hot Potato                      ║
║   Struktur Data & Algoritma — Queue (Circular Simulation)    ║
╚══════════════════════════════════════════════════════════════╝

Skenario:
  Pemain duduk melingkar dan mengoper benda ("kentang panas").
  Setelah N kali operan, pemain yang memegang benda tersingkir.
  Ulangi sampai tersisa 1 pemenang.

Teknik Queue:
  dequeue() front  →  enqueue() back   =  simulasi operan melingkar
  dequeue() tanpa enqueue               =  pemain TERSINGKIR

Visualisasi:
  Panel kiri  : lingkaran pemain + posisi potato
  Panel kanan : state antrian + daftar yang sudah tersingkir
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from collections import deque
import math, os

# ─── Implementasi Queue ──────────────────────────────────────────

class Queue:
    def __init__(self):
        self._data = deque()

    def isEmpty(self):          return len(self._data) == 0
    def __len__(self):          return len(self._data)
    def enqueue(self, item):    self._data.append(item)
    def dequeue(self):
        assert not self.isEmpty(), "Queue kosong!"
        return self._data.popleft()
    def peek(self):
        assert not self.isEmpty(), "Queue kosong!"
        return self._data[0]
    def to_list(self):          return list(self._data)


# ─── Konfigurasi Permainan ───────────────────────────────────────

PLAYERS_INIT = ["Alice", "Bob", "Citra", "Dedi", "Eka", "Fajar"]
NUM_PASS     = 4          # jumlah operan per ronde sebelum tersingkir

PALETTE = {
    "bg"    : "#F7F9FC",
    "dark"  : "#2B2B2B",
    "gray"  : "#AAAAAA",
    "orange": "#DD8452",
    "red"   : "#C44E52",
    "green" : "#55A868",
    "yellow": "#F5C518",
}

PLAYER_COLORS = {
    "Alice" : "#4C72B0",
    "Bob"   : "#DD8452",
    "Citra" : "#55A868",
    "Dedi"  : "#C44E52",
    "Eka"   : "#8172B3",
    "Fajar" : "#64B5CD",
}


# ─── Simulasi ────────────────────────────────────────────────────

def simulate_hot_potato(names, num_pass):
    """Simulasikan permainan Hot Potato dan kembalikan semua frame."""
    q   = Queue()
    for name in names:
        q.enqueue(name)

    frames     = []
    round_num  = 0

    while len(q) > 1:
        round_num += 1

        for step in range(num_pass):
            holder = q.peek()
            frames.append({
                "queue"  : q.to_list(),
                "holder" : holder,
                "phase"  : f"Ronde {round_num} | Operan ke-{step+1}/{num_pass}",
                "out"    : None,
            })
            # operan: dequeue depan, enqueue belakang
            q.enqueue(q.dequeue())

        # Setelah N operan, yang pegang tersingkir
        eliminated = q.dequeue()
        frames.append({
            "queue"  : q.to_list(),
            "holder" : eliminated,
            "phase"  : f"Ronde {round_num} | {eliminated} TERSINGKIR!",
            "out"    : eliminated,
        })

    winner = q.peek()
    frames.append({
        "queue"  : q.to_list(),
        "holder" : winner,
        "phase"  : f"PEMENANG: {winner}!",
        "out"    : None,
    })
    return frames


# ─── Helper: posisi melingkar ────────────────────────────────────

def player_positions(names):
    n   = len(names)
    pos = {}
    for i, name in enumerate(names):
        angle       = 2 * math.pi * i / n - math.pi / 2
        pos[name]   = (math.cos(angle) * 2.6, math.sin(angle) * 2.6)
    return pos


# ─── Gambar setiap frame ─────────────────────────────────────────

def draw_frame(idx, frames, axes):
    ax_circle, ax_queue = axes
    fr      = frames[idx]
    q_state = fr["queue"]
    holder  = fr["holder"]
    phase   = fr["phase"]
    out     = fr["out"]

    eliminated = [p for p in PLAYERS_INIT
                  if p not in q_state and p != (out or "")]

    # ── Panel lingkaran ────────────────────────────────────────
    ax_circle.cla()
    ax_circle.set_facecolor(PALETTE["bg"])
    ax_circle.set_xlim(-4.2, 4.2); ax_circle.set_ylim(-4.2, 4.2)
    ax_circle.set_aspect("equal"); ax_circle.axis("off")

    ax_circle.text(0, 3.85, "LINGKARAN PEMAIN",
                   ha="center", fontsize=11, fontweight="bold",
                   color=PALETTE["dark"])
    ax_circle.text(0, 3.3, phase, ha="center", fontsize=9,
                   color=PALETTE["orange"], style="italic")

    # Garis panduan lingkaran
    theta = __import__("numpy").linspace(0, 2 * math.pi, 300)
    import numpy as np
    ax_circle.plot(2.6 * np.cos(theta), 2.6 * np.sin(theta),
                   color=PALETTE["gray"], lw=0.8, ls="--", zorder=1, alpha=0.5)

    positions = player_positions(q_state)

    for name, (px, py) in positions.items():
        is_holder = (name == holder and out is None)
        is_winner = ("PEMENANG" in phase and name == holder)

        # Glow untuk pemegang potato
        if is_holder:
            glow = plt.Circle((px, py), 0.78,
                              color=PALETTE["yellow"], alpha=0.45, zorder=2)
            ax_circle.add_patch(glow)
        if is_winner:
            glow = plt.Circle((px, py), 0.85,
                              color=PALETTE["yellow"], alpha=0.60, zorder=2)
            ax_circle.add_patch(glow)

        circle = plt.Circle((px, py), 0.58,
                             color=PLAYER_COLORS.get(name, PALETTE["gray"]),
                             zorder=3, alpha=0.93)
        ax_circle.add_patch(circle)
        ax_circle.text(px, py, name[:5], ha="center", va="center",
                       fontsize=8.5, fontweight="bold", color="white", zorder=4)

        # Label potato / winner
        if is_holder and not is_winner:
            ax_circle.text(px, py - 0.95, "[POTATO]",
                           ha="center", fontsize=7, color=PALETTE["yellow"],
                           fontweight="bold")
        if is_winner:
            ax_circle.text(px, py - 1.0, "[WINNER!]",
                           ha="center", fontsize=7.5, color=PALETTE["yellow"],
                           fontweight="bold")

    # Pesan tersingkir
    if out:
        ax_circle.text(0, -3.65, f"{out} TERSINGKIR!",
                       ha="center", fontsize=11, fontweight="bold",
                       color=PALETTE["red"])

    # ── Panel queue ────────────────────────────────────────────
    ax_queue.cla()
    ax_queue.set_facecolor(PALETTE["bg"])
    ax_queue.set_xlim(0, 8); ax_queue.set_ylim(0, 7.5)
    ax_queue.axis("off")

    ax_queue.text(4, 7.2, "STATE ANTRIAN (Queue)",
                  ha="center", fontsize=11, fontweight="bold",
                  color=PALETTE["dark"])
    ax_queue.text(4, 6.75,
                  f"Sisa pemain: {len(q_state)}  |  Operan per ronde: {NUM_PASS}",
                  ha="center", fontsize=9, color=PALETTE["gray"])

    ax_queue.text(0.4, 6.2, "DEPAN", fontsize=8,
                  color="#4C72B0", fontweight="bold")
    ax_queue.text(7.6, 6.2, "BELAKANG", fontsize=8,
                  color=PALETTE["orange"], fontweight="bold", ha="right")

    BW = min(1.2, 6.8 / max(len(q_state), 1))
    for j, name in enumerate(q_state):
        c    = PLAYER_COLORS.get(name, PALETTE["gray"])
        rect = mpatches.FancyBboxPatch(
            (0.4 + j * (BW + 0.12), 5.35),
            BW, 0.72, boxstyle="round,pad=0.05",
            linewidth=1.5, edgecolor="white",
            facecolor=c, alpha=0.92, zorder=3)
        ax_queue.add_patch(rect)
        ax_queue.text(0.4 + j * (BW + 0.12) + BW / 2, 5.71,
                      name[:5], ha="center", va="center",
                      fontsize=8.5, fontweight="bold", color="white", zorder=4)

    # Daftar tersingkir
    ax_queue.text(0.4, 4.5, "Sudah Tersingkir:",
                  fontsize=9.5, fontweight="bold", color=PALETTE["red"])
    for k, name in enumerate(eliminated):
        ax_queue.text(0.4, 3.95 - k * 0.52,
                      f"  x  {name}",
                      fontsize=9, color=PALETTE["red"])

    # Penjelasan teknik
    ax_queue.text(0.4, 1.7, "Teknik Queue:", fontsize=9,
                  fontweight="bold", color=PALETTE["dark"])
    ax_queue.text(0.4, 1.25,
                  "dequeue() --> enqueue()  =  simulasi operan melingkar",
                  fontsize=8.2, color=PALETTE["dark"])
    ax_queue.text(0.4, 0.80,
                  "dequeue() tanpa enqueue  =  pemain TERSINGKIR",
                  fontsize=8.2, color=PALETTE["red"])


# ─── Main ────────────────────────────────────────────────────────

def main():
    out_dir = "/mnt/user-data/outputs"
    os.makedirs(out_dir, exist_ok=True)

    frames = simulate_hot_potato(PLAYERS_INIT, NUM_PASS)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                             facecolor=PALETTE["bg"])
    fig.subplots_adjust(left=0.02, right=0.97, top=0.88,
                        bottom=0.06, wspace=0.18)
    fig.suptitle(
        "Studi Kasus 2 — Permainan Hot Potato  |  Circular Queue Simulation",
        fontsize=13, fontweight="bold", color=PALETTE["dark"])

    for ax in axes:
        ax.set_facecolor(PALETTE["bg"])
        ax.axis("off")

    ani = animation.FuncAnimation(
        fig,
        lambda idx: draw_frame(idx, frames, axes),
        frames=len(frames),
        interval=800,
        repeat=False,
    )

    path = f"{out_dir}/case2_hot_potato.gif"
    ani.save(path, writer="pillow", fps=1.25)
    plt.close(fig)
    print(f"Animasi disimpan: {path}")


if __name__ == "__main__":
    main()
