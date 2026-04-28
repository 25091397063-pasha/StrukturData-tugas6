"""
╔══════════════════════════════════════════════════════════════╗
║   STUDI KASUS 1 — Antrian Printer Bersama                   ║
║   Struktur Data & Algoritma — Queue (FIFO)                   ║
╚══════════════════════════════════════════════════════════════╝

Skenario:
  Banyak user mengirim dokumen ke 1 printer bersama.
  Printer hanya bisa mencetak 1 dokumen pada satu waktu.
  Dokumen yang datang duluan dicetak duluan (FIFO murni).

Operasi Queue:
  enqueue() → user mengirim dokumen baru ke antrian
  dequeue() → printer mengambil & mencetak dokumen berikutnya

Visualisasi:
  Panel kiri  : tampilan antrian + printer yang sedang mencetak
  Panel kanan : log operasi secara real-time
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import os

# ─── Implementasi Queue (Circular Array) ───────────────────────

class Queue:
    def __init__(self, maxSize):
        self._count   = 0
        self._front   = 0
        self._rear    = maxSize - 1
        self._data    = [None] * maxSize
        self._maxSize = maxSize

    def isEmpty(self):  return self._count == 0
    def isFull(self):   return self._count == self._maxSize
    def __len__(self):  return self._count

    def enqueue(self, item):
        assert not self.isFull(), "Queue penuh!"
        self._rear = (self._rear + 1) % self._maxSize
        self._data[self._rear] = item
        self._count += 1

    def dequeue(self):
        assert not self.isEmpty(), "Queue kosong!"
        item = self._data[self._front]
        self._front = (self._front + 1) % self._maxSize
        self._count -= 1
        return item

    def peek(self):
        assert not self.isEmpty(), "Queue kosong!"
        return self._data[self._front]

    def to_list(self):
        result = []
        for i in range(self._count):
            result.append(self._data[(self._front + i) % self._maxSize])
        return result


# ─── Data & Warna ───────────────────────────────────────────────

DOCS_TO_SEND = [
    "laporan.pdf",
    "tugas.docx",
    "foto.jpg",
    "slides.pptx",
    "invoice.xlsx",
]

DOC_COLORS = {
    "laporan.pdf"  : "#4C72B0",
    "tugas.docx"   : "#DD8452",
    "foto.jpg"     : "#55A868",
    "slides.pptx"  : "#8172B3",
    "invoice.xlsx" : "#64B5CD",
}

PALETTE = {
    "bg"    : "#F7F9FC",
    "dark"  : "#2B2B2B",
    "gray"  : "#AAAAAA",
    "orange": "#DD8452",
    "red"   : "#C44E52",
    "green" : "#55A868",
    "yellow": "#F5C518",
}


# ─── Simulasi (bangun semua frame lebih dulu) ───────────────────

def build_frames():
    frames = []
    queue  = Queue(maxSize=10)
    log    = ["[Mulai] Printer antrian siap."]
    queue_snapshot = []

    # Fase 1 — enqueue semua dokumen
    for i, doc in enumerate(DOCS_TO_SEND):
        queue.enqueue(doc)
        queue_snapshot = queue.to_list()
        log = log + [f"enqueue  -->  {doc}"]
        frames.append({
            "queue"   : list(queue_snapshot),
            "printing": None,
            "log"     : list(log),
            "phase"   : f"User {i+1} mengirim dokumen",
        })

    # Fase 2 — printer dequeue & cetak satu per satu
    while not queue.isEmpty():
        doc = queue.dequeue()
        queue_snapshot = queue.to_list()
        log = log + [f"dequeue  -->  MENCETAK: {doc}"]
        frames.append({
            "queue"   : list(queue_snapshot),
            "printing": doc,
            "log"     : list(log),
            "phase"   : "Printer sedang mencetak...",
        })
        log = log + ["Cetak selesai !"]
        frames.append({
            "queue"   : list(queue_snapshot),
            "printing": None,
            "log"     : list(log),
            "phase"   : "Cetak selesai, ambil dokumen berikutnya",
        })

    log = log + ["[Selesai] Semua dokumen telah dicetak!"]
    frames.append({
        "queue"   : [],
        "printing": None,
        "log"     : list(log),
        "phase"   : "Antrian kosong -- selesai!",
    })
    return frames


# ─── Gambar setiap frame ────────────────────────────────────────

def draw_frame(idx, frames, axes):
    ax_q, ax_log = axes
    fr      = frames[idx]
    q_state = fr["queue"]
    printing= fr["printing"]
    log     = fr["log"]
    phase   = fr["phase"]

    W, H = 1.35, 0.65      # ukuran kotak dokumen

    # ── Panel antrian ──────────────────────────────────────────
    ax_q.cla(); ax_q.axis("off")
    ax_q.set_facecolor(PALETTE["bg"])
    ax_q.set_xlim(-0.5, 10); ax_q.set_ylim(0, 7.5)

    ax_q.text(4.5, 7.15, "ANTRIAN PRINTER BERSAMA",
              ha="center", fontsize=12, fontweight="bold", color=PALETTE["dark"])
    ax_q.text(4.5, 6.65, phase, ha="center", fontsize=9,
              color=PALETTE["orange"], style="italic")

    # Label front / rear
    ax_q.text(0.0, 5.7,  "DEPAN (front)", fontsize=8,
              color="#4C72B0", fontweight="bold")
    ax_q.text(5.5, 5.7, "BELAKANG (rear)", fontsize=8,
              color=PALETTE["orange"], fontweight="bold", ha="right")

    # Kotak-kotak dokumen dalam antrian
    y_q = 4.8
    for j, doc in enumerate(q_state):
        c    = DOC_COLORS.get(doc, "#888888")
        rect = mpatches.FancyBboxPatch(
            (j * (W + 0.12), y_q - H / 2),
            W, H, boxstyle="round,pad=0.06",
            linewidth=1.5, edgecolor="white",
            facecolor=c, alpha=0.92, zorder=3)
        ax_q.add_patch(rect)
        ax_q.text(j * (W + 0.12) + W / 2, y_q,
                  doc, ha="center", va="center",
                  fontsize=7.5, fontweight="bold", color="white", zorder=4)

    if not q_state:
        ax_q.text(2.5, y_q, "[ Antrian Kosong ]",
                  ha="center", va="center", fontsize=10,
                  color=PALETTE["gray"], style="italic")

    # Panah ke printer
    if q_state:
        ax_q.annotate("", xy=(7.2, 3.3),
                      xytext=(len(q_state) * (W + 0.12), 3.3),
                      arrowprops=dict(arrowstyle="->",
                                      color=PALETTE["red"], lw=2.2))

    # Gambar printer
    printer_rect = mpatches.FancyBboxPatch(
        (7.2, 2.2), 2.4, 2.0,
        boxstyle="round,pad=0.1", linewidth=2,
        edgecolor=PALETTE["dark"], facecolor="#E8E8E8", zorder=2)
    ax_q.add_patch(printer_rect)
    ax_q.text(8.4, 4.5, "[ PRINTER ]",
              ha="center", fontsize=10, fontweight="bold", color=PALETTE["dark"])

    if printing:
        c = DOC_COLORS.get(printing, "#888")
        ax_q.text(8.4, 3.55, printing,
                  ha="center", fontsize=8.5, color=c, fontweight="bold")
        ax_q.text(8.4, 2.9, "MENCETAK...",
                  ha="center", fontsize=8, color=PALETTE["green"])
    else:
        ax_q.text(8.4, 3.2, "[ siap ]",
                  ha="center", fontsize=9, color=PALETTE["gray"])

    # Statistik
    n_done = sum(1 for ln in log if "MENCETAK" in ln)
    ax_q.text(0.0, 1.6, f"Dalam antrian  : {len(q_state)} dokumen",
              fontsize=9, color=PALETTE["dark"])
    ax_q.text(0.0, 1.1, f"Sudah dicetak  : {n_done} dokumen",
              fontsize=9, color=PALETTE["dark"])
    ax_q.text(0.0, 0.55,
              "Prinsip: FIFO — yang masuk pertama, keluar pertama",
              fontsize=8, color=PALETTE["gray"], style="italic")

    # ── Panel log ──────────────────────────────────────────────
    ax_log.cla(); ax_log.axis("off")
    ax_log.set_facecolor(PALETTE["bg"])
    ax_log.set_xlim(0, 1); ax_log.set_ylim(0, 1)

    ax_log.text(0.5, 0.97, "LOG OPERASI",
                ha="center", fontsize=11, fontweight="bold",
                color=PALETTE["dark"], va="top")
    ax_log.axhline(y=0.92, color=PALETTE["gray"], lw=0.8, alpha=0.5)

    shown = log[-13:]
    for k, line in enumerate(reversed(shown)):
        alpha = max(1.0 - k * 0.06, 0.3)
        if "MENCETAK" in line:
            color = PALETTE["green"]
        elif "enqueue" in line:
            color = "#4C72B0"
        elif "Selesai" in line or "selesai" in line:
            color = PALETTE["orange"]
        else:
            color = PALETTE["dark"]
        ax_log.text(0.05, 0.88 - k * 0.068, line,
                    fontsize=8.2, color=color, alpha=alpha, va="top")


# ─── Main ───────────────────────────────────────────────────────

def main():
    out_dir = "/mnt/user-data/outputs"
    os.makedirs(out_dir, exist_ok=True)

    frames = build_frames()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5),
                             facecolor=PALETTE["bg"])
    fig.subplots_adjust(left=0.03, right=0.98, top=0.88,
                        bottom=0.08, wspace=0.30)
    fig.suptitle(
        "Studi Kasus 1 — Antrian Printer Bersama  |  Queue FIFO",
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

    path = f"{out_dir}/case1_printer_queue.gif"
    ani.save(path, writer="pillow", fps=1.1)
    plt.close(fig)
    print(f"Animasi disimpan: {path}")


if __name__ == "__main__":
    main()
