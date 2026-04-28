"""
╔══════════════════════════════════════════════════════════════╗
║   STUDI KASUS 4 — BFS (Breadth-First Search)                ║
║   Struktur Data & Algoritma — Queue sebagai Engine BFS       ║
╚══════════════════════════════════════════════════════════════╝

Skenario:
  Penelusuran graf tak berbobot dari node awal.
  Queue memastikan penelusuran dilakukan LEVEL DEMI LEVEL.
  BFS menjamin jalur terpendek pada graf tanpa bobot.

Algoritma:
  1. Enqueue node awal, tandai sebagai dikunjungi.
  2. Selama queue tidak kosong:
       a. Dequeue node terdepan → proses.
       b. Enqueue semua tetangganya yang belum dikunjungi.
  3. Sifat FIFO menjamin node level dekat diproses sebelum yang jauh.

Visualisasi:
  Panel kiri  : graf dengan pewarnaan level + node aktif
  Panel kanan : state queue + urutan kunjungan BFS
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from collections import deque
import numpy as np
import os

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


# ─── Algoritma BFS ────────────────────────────────────────────────

def bfs(graph, start):
    """
    BFS standar — kembalikan daftar node dalam urutan kunjungan.
    Queue FIFO memastikan level-by-level traversal.
    """
    visited = set()
    queue   = Queue()
    order   = []

    queue.enqueue(start)
    visited.add(start)

    while not queue.isEmpty():
        node = queue.dequeue()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.enqueue(neighbor)

    return order


# ─── Data Graf ───────────────────────────────────────────────────

GRAPH = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F", "G"],
    "D": ["B"],
    "E": ["B", "H"],
    "F": ["C"],
    "G": ["C", "I"],
    "H": ["E"],
    "I": ["G"],
}

START_NODE = "A"

# Posisi tetap agar tampilan rapi (tree-like layout)
NODE_POS = {
    "A": (4.0, 7.2),
    "B": (2.2, 5.4),  "C": (5.8, 5.4),
    "D": (1.0, 3.6),  "E": (3.2, 3.6),  "F": (4.8, 3.6),  "G": (6.8, 3.6),
    "H": (3.2, 1.8),  "I": (6.8, 1.8),
}

# Level BFS setiap node dari A
NODE_LEVEL = {
    "A": 0,
    "B": 1, "C": 1,
    "D": 2, "E": 2, "F": 2, "G": 2,
    "H": 3, "I": 3,
}

LEVEL_COLOR = {
    0: "#4C72B0",
    1: "#64B5CD",
    2: "#55A868",
    3: "#8172B3",
}

PALETTE = {
    "bg"    : "#F7F9FC",
    "dark"  : "#2B2B2B",
    "gray"  : "#AAAAAA",
    "orange": "#DD8452",
    "yellow": "#F5C518",
    "red"   : "#C44E52",
}


# ─── Simulasi (rekam semua frame) ────────────────────────────────

def build_frames():
    queue   = Queue()
    visited = set()
    order   = []
    frames  = []

    queue.enqueue(START_NODE)
    visited.add(START_NODE)
    frames.append({
        "queue"  : queue.to_list(),
        "visited": set(visited),
        "order"  : list(order),
        "current": None,
        "phase"  : f"Start: enqueue('{START_NODE}')",
    })

    while not queue.isEmpty():
        node = queue.dequeue()
        order.append(node)
        frames.append({
            "queue"  : queue.to_list(),
            "visited": set(visited),
            "order"  : list(order),
            "current": node,
            "phase"  : f"dequeue() --> proses '{node}'  (Level {NODE_LEVEL[node]})",
        })

        for neighbor in GRAPH[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.enqueue(neighbor)
                frames.append({
                    "queue"  : queue.to_list(),
                    "visited": set(visited),
                    "order"  : list(order),
                    "current": node,
                    "phase"  : f"enqueue('{neighbor}') — tetangga '{node}'",
                })

    frames.append({
        "queue"  : [],
        "visited": set(visited),
        "order"  : list(order),
        "current": None,
        "phase"  : "BFS selesai! Semua node terjelajahi.",
    })
    return frames


# ─── Gambar setiap frame ─────────────────────────────────────────

def draw_frame(idx, frames, axes):
    ax_g, ax_info = axes
    fr      = frames[idx]
    q_state = fr["queue"]
    vis     = fr["visited"]
    order   = fr["order"]
    curr    = fr["current"]
    phase   = fr["phase"]

    # ── Panel Graf ─────────────────────────────────────────────
    ax_g.cla()
    ax_g.set_facecolor(PALETTE["bg"])
    ax_g.set_xlim(-0.3, 8.8); ax_g.set_ylim(0.5, 8.8)
    ax_g.axis("off")

    ax_g.text(4.25, 8.55, "GRAF & PENELUSURAN BFS",
              ha="center", fontsize=11, fontweight="bold", color=PALETTE["dark"])
    ax_g.text(4.25, 8.1, phase, ha="center", fontsize=8.5,
              color=PALETTE["orange"], style="italic")

    # Gambar sisi (edges)
    drawn_edges = set()
    for node, neighbors in GRAPH.items():
        for nb in neighbors:
            edge = tuple(sorted([node, nb]))
            if edge in drawn_edges:
                continue
            drawn_edges.add(edge)
            x1, y1 = NODE_POS[node]
            x2, y2 = NODE_POS[nb]
            both_visited = node in vis and nb in vis
            ax_g.plot([x1, x2], [y1, y2],
                      color=LEVEL_COLOR[NODE_LEVEL[node]] if both_visited
                            else PALETTE["gray"],
                      lw=2.5 if both_visited else 1.2,
                      alpha=0.85 if both_visited else 0.35, zorder=1)

    # Gambar node
    for node, (px, py) in NODE_POS.items():
        in_vis  = node in vis
        is_curr = node == curr
        in_q    = node in q_state

        if is_curr:
            glow = plt.Circle((px, py), 0.72,
                              color=PALETTE["yellow"], alpha=0.50, zorder=2)
            ax_g.add_patch(glow)

        color = LEVEL_COLOR[NODE_LEVEL[node]] if in_vis else PALETTE["gray"]
        circle = plt.Circle((px, py), 0.58,
                             color=color, zorder=3,
                             alpha=0.95 if in_vis else 0.38)
        ax_g.add_patch(circle)

        if in_q:
            ring = plt.Circle((px, py), 0.72,
                               fill=False, edgecolor=PALETTE["orange"],
                               lw=2.5, zorder=5)
            ax_g.add_patch(ring)

        ax_g.text(px, py, node, ha="center", va="center",
                  fontsize=10, fontweight="bold",
                  color="white" if in_vis else "#999", zorder=4)

    # Legend level
    for lvl in range(4):
        c = plt.Circle((0.5, 3.1 - lvl * 0.62), 0.22,
                       color=LEVEL_COLOR[lvl], zorder=3)
        ax_g.add_patch(c)
        ax_g.text(0.85, 3.1 - lvl * 0.62,
                  f"Level {lvl}", fontsize=7.5,
                  va="center", color=PALETTE["dark"])

    # Keterangan ring oranye
    ax_g.text(0.4, 0.85,
              "Ring oranye = dalam queue",
              fontsize=7.5, color=PALETTE["orange"])

    # ── Panel Info ─────────────────────────────────────────────
    ax_info.cla()
    ax_info.set_facecolor(PALETTE["bg"])
    ax_info.set_xlim(0, 1); ax_info.set_ylim(0, 1)
    ax_info.axis("off")

    ax_info.text(0.5, 0.97, "STATE QUEUE & HASIL BFS",
                 ha="center", fontsize=11, fontweight="bold",
                 color=PALETTE["dark"], va="top")
    ax_info.axhline(y=0.92, color=PALETTE["gray"], lw=0.8, alpha=0.5)

    # Queue visualisasi
    ax_info.text(0.05, 0.89, "Queue saat ini:",
                 fontsize=9, fontweight="bold", color=PALETTE["dark"])
    if q_state:
        bw = min(0.115, 0.88 / len(q_state))
        for j, n in enumerate(q_state):
            rect = mpatches.FancyBboxPatch(
                (0.05 + j * (bw + 0.012), 0.78), bw, 0.074,
                boxstyle="round,pad=0.015",
                linewidth=1.2, edgecolor="white",
                facecolor=LEVEL_COLOR[NODE_LEVEL[n]], alpha=0.92, zorder=3)
            ax_info.add_patch(rect)
            ax_info.text(0.05 + j * (bw + 0.012) + bw / 2, 0.817,
                         n, ha="center", va="center",
                         fontsize=8, fontweight="bold", color="white", zorder=4)
    else:
        ax_info.text(0.5, 0.815, "[ Queue Kosong ]",
                     ha="center", fontsize=8, color=PALETTE["gray"],
                     style="italic")

    ax_info.text(0.05, 0.74,
                 f"Elemen dalam queue: {len(q_state)}",
                 fontsize=8.2, color=PALETTE["gray"])

    # Urutan kunjungan
    ax_info.text(0.05, 0.67, "Urutan Kunjungan BFS:",
                 fontsize=9, fontweight="bold", color=PALETTE["dark"])
    ax_info.axhline(y=0.635, color=PALETTE["gray"], lw=0.5, alpha=0.4)

    for k, n in enumerate(order):
        y = 0.60 - k * 0.066
        c = LEVEL_COLOR[NODE_LEVEL[n]]
        rect = mpatches.FancyBboxPatch(
            (0.05, y - 0.025), 0.90, 0.052,
            boxstyle="round,pad=0.012",
            linewidth=1, edgecolor="white",
            facecolor=c, alpha=0.88, zorder=3)
        ax_info.add_patch(rect)
        ax_info.text(0.15, y + 0.001,
                     f"Step {k+1}: Node '{n}'   (Level {NODE_LEVEL[n]})",
                     va="center", fontsize=8.2,
                     color="white", fontweight="bold", zorder=4)

    ax_info.text(0.5, 0.04,
                 "FIFO Queue --> BFS Level demi Level",
                 ha="center", fontsize=7.5,
                 color=PALETTE["gray"], style="italic")


# ─── Main ────────────────────────────────────────────────────────

def main():
    out_dir = "/mnt/user-data/outputs"
    os.makedirs(out_dir, exist_ok=True)

    frames = build_frames()

    fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                             facecolor=PALETTE["bg"])
    fig.subplots_adjust(left=0.02, right=0.97, top=0.88,
                        bottom=0.05, wspace=0.18)
    fig.suptitle(
        "Studi Kasus 4 — BFS (Breadth-First Search)  |  Queue sebagai Engine",
        fontsize=13, fontweight="bold", color=PALETTE["dark"])

    for ax in axes:
        ax.set_facecolor(PALETTE["bg"])
        ax.axis("off")

    ani = animation.FuncAnimation(
        fig,
        lambda idx: draw_frame(idx, frames, axes),
        frames=len(frames),
        interval=850,
        repeat=False,
    )

    path = f"{out_dir}/case4_bfs.gif"
    ani.save(path, writer="pillow", fps=1.1)
    plt.close(fig)
    print(f"Animasi disimpan: {path}")


if __name__ == "__main__":
    # Demo text — jalankan BFS dan cetak urutan kunjungan
    print("Demo BFS (tanpa animasi):")
    result = bfs(GRAPH, START_NODE)
    print(f"  Start node     : {START_NODE}")
    print(f"  Urutan kunjungan: {' -> '.join(result)}")
    print()
    main()
