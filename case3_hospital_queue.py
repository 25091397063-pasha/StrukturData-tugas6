"""
╔══════════════════════════════════════════════════════════════╗
║   STUDI KASUS 3 — Antrian Rumah Sakit (Priority Queue)      ║
║   Struktur Data & Algoritma — Bounded Priority Queue         ║
╚══════════════════════════════════════════════════════════════╝

Skenario:
  Pasien datang dengan tingkat urgensi berbeda.
  Pasien kondisi kritis harus dilayani lebih dahulu.
  Untuk prioritas yang sama, berlaku FIFO (yang datang duluan).

Level Prioritas:
  0 = Kritis   (tertinggi, dilayani pertama)
  1 = Darurat
  2 = Menengah
  3 = Ringan   (terendah, dilayani terakhir)

Implementasi:
  BoundedPriorityQueue — array of queues, satu per level prioritas.
  dequeue() selalu mengambil dari level prioritas terendah (0 dulu).

Visualisasi:
  Panel kiri  : bounded priority queue dengan 4 level
  Panel kanan : urutan pasien yang telah dilayani
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from collections import deque
import os

# ─── Implementasi Bounded Priority Queue ────────────────────────

class BoundedPriorityQueue:
    """
    Priority Queue dengan jumlah level prioritas terbatas.
    Level 0 = prioritas tertinggi.
    Untuk prioritas yang sama, berlaku FIFO.
    """
    def __init__(self, num_levels):
        self._queues = [deque() for _ in range(num_levels)]
        self._levels = num_levels
        self._count  = 0

    def isEmpty(self):
        return self._count == 0

    def __len__(self):
        return self._count

    def enqueue(self, item, priority):
        assert 0 <= priority < self._levels, "Prioritas di luar jangkauan!"
        self._queues[priority].append(item)
        self._count += 1

    def dequeue(self):
        assert not self.isEmpty(), "Priority Queue kosong!"
        for q in self._queues:
            if q:
                self._count -= 1
                return q.popleft()

    def peek(self):
        assert not self.isEmpty(), "Priority Queue kosong!"
        for q in self._queues:
            if q:
                return q[0]

    def snapshot(self):
        """Kembalikan snapshot isi tiap level sebagai list of list."""
        return [list(q) for q in self._queues]


# ─── Data Pasien ─────────────────────────────────────────────────

PATIENTS = [
    # (nama, prioritas, warna)
    ("Budi",  3, "#27AE60"),   # Ringan   — hijau
    ("Ani",   0, "#E74C3C"),   # Kritis   — merah
    ("Citra", 2, "#F39C12"),   # Menengah — oranye
    ("Dedi",  0, "#C0392B"),   # Kritis   — merah tua
    ("Eka",   1, "#E67E22"),   # Darurat  — oranye tua
]

LEVEL_LABEL = {
    0: "Kritis  (P0)",
    1: "Darurat (P1)",
    2: "Menengah(P2)",
    3: "Ringan  (P3)",
}

LEVEL_COLORS = {
    0: "#E74C3C",
    1: "#E67E22",
    2: "#F39C12",
    3: "#27AE60",
}

PALETTE = {
    "bg"    : "#F7F9FC",
    "dark"  : "#2B2B2B",
    "gray"  : "#AAAAAA",
    "orange": "#DD8452",
    "yellow": "#F5C518",
}


# ─── Simulasi ────────────────────────────────────────────────────

def build_frames():
    bpq    = BoundedPriorityQueue(num_levels=4)
    served = []
    frames = []

    # Fase 1 — pasien masuk
    for name, prio, color in PATIENTS:
        bpq.enqueue((name, prio, color), prio)
        frames.append({
            "snapshot": bpq.snapshot(),
            "served"  : list(served),
            "action"  : f"enqueue({name})  -->  {LEVEL_LABEL[prio]}",
            "serving" : None,
        })

    # Fase 2 — layani satu per satu
    while not bpq.isEmpty():
        patient = bpq.dequeue()
        name, prio, color = patient
        frames.append({
            "snapshot": bpq.snapshot(),
            "served"  : list(served),
            "action"  : f"dequeue()  -->  Melayani {name}  [{LEVEL_LABEL[prio]}]",
            "serving" : (name, prio, color),
        })
        served.append((name, prio, color))
        frames.append({
            "snapshot": bpq.snapshot(),
            "served"  : list(served),
            "action"  : f"{name} selesai dilayani.",
            "serving" : None,
        })

    return frames


# ─── Gambar setiap frame ─────────────────────────────────────────

def draw_frame(idx, frames, axes):
    ax_pq, ax_info = axes
    fr       = frames[idx]
    snapshot = fr["snapshot"]
    served   = fr["served"]
    action   = fr["action"]
    serving  = fr["serving"]

    # ── Panel Priority Queue ────────────────────────────────────
    ax_pq.cla()
    ax_pq.set_facecolor(PALETTE["bg"])
    ax_pq.set_xlim(-0.5, 9); ax_pq.set_ylim(0, 8.5)
    ax_pq.axis("off")

    ax_pq.text(4.25, 8.2, "BOUNDED PRIORITY QUEUE",
               ha="center", fontsize=12, fontweight="bold", color=PALETTE["dark"])
    ax_pq.text(4.25, 7.7, action, ha="center", fontsize=8.5,
               color=PALETTE["orange"], style="italic")

    # Gambar 4 level
    y_bases = [6.2, 4.8, 3.4, 2.0]
    BW      = 1.3

    for lvl, y_base in enumerate(y_bases):
        lc  = LEVEL_COLORS[lvl]
        lbl = LEVEL_LABEL[lvl]

        # Strip latar level
        strip = mpatches.FancyBboxPatch(
            (-0.3, y_base - 0.1), 9.0, 0.92,
            boxstyle="round,pad=0.04",
            linewidth=1, edgecolor=lc, facecolor=lc, alpha=0.08, zorder=1)
        ax_pq.add_patch(strip)

        ax_pq.text(-0.25, y_base + 0.32, lbl,
                   fontsize=8.5, fontweight="bold", color=lc, va="center")

        for j, (name, prio, color) in enumerate(snapshot[lvl]):
            rect = mpatches.FancyBboxPatch(
                (j * (BW + 0.14), y_base),
                BW, 0.72,
                boxstyle="round,pad=0.06",
                linewidth=1.5, edgecolor="white",
                facecolor=color, alpha=0.93, zorder=3)
            ax_pq.add_patch(rect)
            ax_pq.text(j * (BW + 0.14) + BW / 2, y_base + 0.36,
                       name, ha="center", va="center",
                       fontsize=9, fontweight="bold", color="white", zorder=4)

        if not snapshot[lvl]:
            ax_pq.text(0.5, y_base + 0.32, "[ kosong ]",
                       fontsize=8, color=PALETTE["gray"], style="italic")

    # Kotak sedang dilayani
    ax_pq.text(0.0, 1.0, "Sedang Dilayani:",
               fontsize=9, fontweight="bold", color=PALETTE["dark"])
    if serving:
        name, prio, color = serving
        rect = mpatches.FancyBboxPatch(
            (2.3, 0.15), 2.8, 0.82,
            boxstyle="round,pad=0.08",
            linewidth=2.5, edgecolor=PALETTE["yellow"],
            facecolor=color, alpha=0.93, zorder=3)
        ax_pq.add_patch(rect)
        ax_pq.text(3.7, 0.56,
                   f"  {name}  |  {LEVEL_LABEL[prio]}",
                   ha="center", va="center",
                   fontsize=9, fontweight="bold", color="white", zorder=4)

    # ── Panel Urutan Layanan ────────────────────────────────────
    ax_info.cla()
    ax_info.set_facecolor(PALETTE["bg"])
    ax_info.set_xlim(0, 1); ax_info.set_ylim(0, 1)
    ax_info.axis("off")

    ax_info.text(0.5, 0.97, "URUTAN LAYANAN",
                 ha="center", fontsize=11, fontweight="bold",
                 color=PALETTE["dark"], va="top")
    ax_info.axhline(y=0.92, color=PALETTE["gray"], lw=0.8, alpha=0.5)

    for k, (name, prio, color) in enumerate(served):
        y = 0.87 - k * 0.13
        rect = mpatches.FancyBboxPatch(
            (0.05, y - 0.05), 0.90, 0.10,
            boxstyle="round,pad=0.03",
            linewidth=1.2, edgecolor="white",
            facecolor=color, alpha=0.87, zorder=3)
        ax_info.add_patch(rect)
        ax_info.text(0.12, y,
                     f"{k+1}.  {name}  —  {LEVEL_LABEL[prio]}",
                     va="center", fontsize=8.5, fontweight="bold",
                     color="white", zorder=4)

    ax_info.text(0.5, 0.10,
                 f"Total pasien masuk  : {len(PATIENTS)}\n"
                 f"Sudah dilayani      : {len(served)}",
                 ha="center", fontsize=9, color=PALETTE["dark"], va="center")

    ax_info.text(0.5, 0.02,
                 "Prioritas sama --> FIFO berlaku",
                 ha="center", fontsize=7.5,
                 color=PALETTE["gray"], style="italic")


# ─── Main ────────────────────────────────────────────────────────

def main():
    out_dir = "/mnt/user-data/outputs"
    os.makedirs(out_dir, exist_ok=True)

    frames = build_frames()

    fig, axes = plt.subplots(1, 2, figsize=(13, 6),
                             facecolor=PALETTE["bg"])
    fig.subplots_adjust(left=0.03, right=0.97, top=0.88,
                        bottom=0.06, wspace=0.25)
    fig.suptitle(
        "Studi Kasus 3 — Antrian Rumah Sakit  |  Bounded Priority Queue",
        fontsize=13, fontweight="bold", color=PALETTE["dark"])

    for ax in axes:
        ax.set_facecolor(PALETTE["bg"])
        ax.axis("off")

    ani = animation.FuncAnimation(
        fig,
        lambda idx: draw_frame(idx, frames, axes),
        frames=len(frames),
        interval=900,
        repeat=False,
    )

    path = f"{out_dir}/case3_hospital_queue.gif"
    ani.save(path, writer="pillow", fps=1.1)
    plt.close(fig)
    print(f"Animasi disimpan: {path}")


if __name__ == "__main__":
    main()
