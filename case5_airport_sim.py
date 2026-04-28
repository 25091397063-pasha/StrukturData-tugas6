"""
╔══════════════════════════════════════════════════════════════╗
║   STUDI KASUS 5 — Simulasi Loket Tiket Bandara              ║
║   Struktur Data & Algoritma — Discrete Event Simulation      ║
╚══════════════════════════════════════════════════════════════╝

Skenario:
  Penumpang tiba secara acak di loket tiket bandara.
  Beberapa agen melayani penumpang secara paralel.
  Simulasi menghitung rata-rata waktu tunggu penumpang.

Tiga Aturan per Tick Waktu:
  R1: Penumpang tiba (acak, probabilitas = 1/betweenTime) --> enqueue
  R2: Agen bebas & queue tidak kosong --> dequeue & layani
  R3: Transaksi selesai --> agen kembali bebas

Parameter Kunci:
  NUM_AGENTS    : jumlah agen loket
  SERVICE_TIME  : menit per penumpang
  BETWEEN_TIME  : rata-rata selang kedatangan (menit)

Insight:
  Menambah 1 agen (2->3) bisa menurunkan avg. tunggu secara drastis.
  Contoh: 2 agen -> avg. tunggu 475 mnt | 3 agen -> avg. tunggu 1.14 mnt

Visualisasi:
  Panel kiri  : loket agen + antrian penumpang saat ini
  Panel kanan : grafik rata-rata waktu tunggu vs waktu simulasi
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from collections import deque
import random, os

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
    def to_list(self):          return list(self._data)


# ─── Model Agen Loket ────────────────────────────────────────────

class Agent:
    def __init__(self, agent_id):
        self.agent_id   = agent_id
        self.busy_until = -1
        self.passenger  = None           # nama penumpang yang sedang dilayani

    def is_free(self, current_time):
        return current_time >= self.busy_until

    def start_serving(self, passenger_name, current_time, service_duration):
        self.passenger  = passenger_name
        self.busy_until = current_time + service_duration

    def finish(self, current_time):
        if not self.is_free(current_time):
            return None
        name            = self.passenger
        self.passenger  = None
        return name

    def remaining_time(self, current_time):
        return max(0, self.busy_until - current_time)


# ─── Parameter Simulasi ──────────────────────────────────────────

RANDOM_SEED  = 7
NUM_MINUTES  = 30
NUM_AGENTS   = 3
SERVICE_TIME = 4
BETWEEN_TIME = 3

PASSENGER_NAMES = [
    "Ali",   "Siti",  "Budi",  "Rina",  "Tono",
    "Dewi",  "Heru",  "Maya",  "Agus",  "Lena",
    "Dian",  "Farid", "Nita",  "Rudi",  "Wati",
    "Joko",  "Sari",  "Eko",   "Putri", "Gani",
    "Andi",  "Reni",  "Bayu",  "Fitri", "Wahyu",
]

PALETTE = {
    "bg"    : "#F7F9FC",
    "dark"  : "#2B2B2B",
    "gray"  : "#AAAAAA",
    "orange": "#DD8452",
    "red"   : "#C44E52",
    "green" : "#55A868",
    "yellow": "#F5C518",
    "blue"  : "#4C72B0",
}

AGENT_COLORS = ["#4C72B0", "#8172B3", "#64B5CD"]


# ─── Simulasi ────────────────────────────────────────────────────

def run_simulation():
    random.seed(RANDOM_SEED)

    queue       = Queue()
    agents      = [Agent(i) for i in range(NUM_AGENTS)]
    frames      = []
    total_wait  = 0
    num_served  = 0
    name_idx    = [0]

    def next_passenger():
        name       = PASSENGER_NAMES[name_idx[0] % len(PASSENGER_NAMES)]
        name_idx[0] += 1
        return name

    for t in range(NUM_MINUTES + 1):

        # R1 — Penumpang tiba?
        if random.random() < 1 / BETWEEN_TIME:
            passenger = next_passenger()
            queue.enqueue((passenger, t))   # (nama, waktu_tiba)

        # R2 — Agen bebas & ada penumpang di queue?
        for ag in agents:
            if ag.is_free(t) and not queue.isEmpty():
                passenger_name, arrive_time = queue.dequeue()
                wait_time   = t - arrive_time
                total_wait += wait_time
                num_served += 1
                ag.start_serving(passenger_name, t, SERVICE_TIME)

        # R3 — Agen selesai?
        for ag in agents:
            ag.finish(t)

        avg_wait = round(total_wait / num_served, 2) if num_served else 0

        frames.append({
            "time"     : t,
            "q_state"  : queue.to_list(),
            "agents"   : [
                {
                    "name": ag.passenger,
                    "busy": not ag.is_free(t),
                    "rem" : ag.remaining_time(t),
                }
                for ag in agents
            ],
            "served"   : num_served,
            "avg_wait" : avg_wait,
            "total_wait": total_wait,
        })

    return frames


# ─── Gambar setiap frame ─────────────────────────────────────────

def draw_frame(idx, frames, ax_main, ax_chart, avg_wait_hist):
    fd         = frames[idx]
    t          = fd["time"]
    q_state    = fd["q_state"]
    agent_info = fd["agents"]
    served     = fd["served"]
    avg_wait   = fd["avg_wait"]

    avg_wait_hist.append(avg_wait)

    # ── Panel Utama ────────────────────────────────────────────
    ax_main.cla()
    ax_main.set_facecolor(PALETTE["bg"])
    ax_main.set_xlim(0, 8); ax_main.set_ylim(0, 8.5)
    ax_main.axis("off")

    ax_main.text(4, 8.25, "SIMULASI LOKET TIKET BANDARA",
                 ha="center", fontsize=11, fontweight="bold",
                 color=PALETTE["dark"])
    ax_main.text(4, 7.8,
                 f"Menit ke-{t}  |  Agen: {NUM_AGENTS}  "
                 f"|  Layanan: {SERVICE_TIME} mnt/orang  "
                 f"|  Tiba tiap: ~{BETWEEN_TIME} mnt",
                 ha="center", fontsize=8, color=PALETTE["orange"])

    # Loket agen
    ax_main.text(0.3, 7.35, "LOKET AGEN:",
                 fontsize=9.5, fontweight="bold", color=PALETTE["dark"])

    for j, ag in enumerate(agent_info):
        xj   = 0.4 + j * 2.35
        busy = ag["busy"]
        rem  = ag["rem"]
        name = ag["name"]
        c    = AGENT_COLORS[j]

        rect = mpatches.FancyBboxPatch(
            (xj, 5.85), 2.0, 1.25,
            boxstyle="round,pad=0.08",
            linewidth=2, edgecolor=c,
            facecolor=c if busy else "#E8E8E8",
            alpha=0.88 if busy else 0.45, zorder=3)
        ax_main.add_patch(rect)
        ax_main.text(xj + 1.0, 7.35,
                     f"Agen {j+1}", ha="center", fontsize=8.5,
                     fontweight="bold",
                     color="white" if busy else PALETTE["gray"])
        if busy and name:
            ax_main.text(xj + 1.0, 6.85, name,
                         ha="center", fontsize=8.5, color="white")
            ax_main.text(xj + 1.0, 6.35,
                         f"sisa {rem} mnt",
                         ha="center", fontsize=7.5, color="#FFECB3")
        else:
            ax_main.text(xj + 1.0, 6.5, "[ Bebas ]",
                         ha="center", fontsize=8.5, color=PALETTE["gray"])

    # Antrian penumpang
    ax_main.text(0.3, 5.4,
                 f"ANTRIAN  ({len(q_state)} penumpang):",
                 fontsize=9.5, fontweight="bold", color=PALETTE["dark"])

    MAX_SHOW = 10
    shown    = q_state[:MAX_SHOW]
    BW, BH   = 0.70, 0.52

    for k, (name, arrive) in enumerate(shown):
        xk = 0.3  + (k % 5) * (BW + 0.14)
        yk = 4.35 - (k // 5) * (BH + 0.16)
        rect = mpatches.FancyBboxPatch(
            (xk, yk), BW, BH,
            boxstyle="round,pad=0.05",
            linewidth=1.5, edgecolor="white",
            facecolor=PALETTE["orange"], alpha=0.90, zorder=3)
        ax_main.add_patch(rect)
        ax_main.text(xk + BW / 2, yk + BH / 2,
                     name[:4], ha="center", va="center",
                     fontsize=7.5, fontweight="bold", color="white", zorder=4)

    if len(q_state) > MAX_SHOW:
        ax_main.text(5.7, 3.95,
                     f"... +{len(q_state) - MAX_SHOW} lagi",
                     fontsize=8, color=PALETTE["gray"])
    if not q_state:
        ax_main.text(3.0, 4.1, "[ Antrian Kosong ]",
                     ha="center", fontsize=9, color=PALETTE["gray"],
                     style="italic")

    # Statistik
    ax_main.axhline(y=2.6, xmin=0.02, xmax=0.98,
                    color=PALETTE["gray"], lw=0.7, alpha=0.4)
    ax_main.text(0.3, 2.3,
                 f"Rata-rata tunggu   :  {avg_wait:.2f} menit",
                 fontsize=9.5, color=PALETTE["dark"])
    ax_main.text(0.3, 1.8,
                 f"Total terlayani    :  {served} penumpang",
                 fontsize=9.5, color=PALETTE["dark"])
    ax_main.text(0.3, 1.3,
                 f"Insight: Tambah 1 agen (2->3) bisa pangkas tunggu >99%!",
                 fontsize=8, color=PALETTE["gray"], style="italic")

    ax_main.text(0.3, 0.6,
                 f"Aturan:\n"
                 f"  R1  Penumpang tiba (prob=1/{BETWEEN_TIME}) --> enqueue\n"
                 f"  R2  Agen bebas & queue ada --> dequeue & layani\n"
                 f"  R3  Selesai layani --> agen bebas",
                 fontsize=7.5, color=PALETTE["dark"])

    # ── Panel Grafik ───────────────────────────────────────────
    ax_chart.cla()
    ax_chart.set_facecolor(PALETTE["bg"])
    ax_chart.set_xlabel("Menit ke-", fontsize=8)
    ax_chart.set_ylabel("Avg. Tunggu (menit)", fontsize=8)
    ax_chart.set_title("Grafik Rata-rata Waktu Tunggu",
                       fontsize=9, fontweight="bold")
    ax_chart.set_xlim(0, NUM_MINUTES)
    peak = max(max(avg_wait_hist, default=0.5) * 1.15, 1)
    ax_chart.set_ylim(0, peak)
    ax_chart.tick_params(labelsize=7)

    xs = list(range(len(avg_wait_hist)))
    ax_chart.fill_between(xs, avg_wait_hist, alpha=0.22,
                          color=PALETTE["blue"])
    ax_chart.plot(xs, avg_wait_hist,
                  color=PALETTE["blue"], lw=2)

    if avg_wait > 0:
        ax_chart.axhline(y=avg_wait, color=PALETTE["red"],
                         lw=1.2, ls="--", alpha=0.7)
        ax_chart.text(max(t * 0.95, 1), avg_wait * 1.06,
                      f"{avg_wait:.1f}", fontsize=7,
                      color=PALETTE["red"], ha="right")

    ax_chart.spines["top"].set_visible(False)
    ax_chart.spines["right"].set_visible(False)


# ─── Main ────────────────────────────────────────────────────────

def main():
    out_dir = "/mnt/user-data/outputs"
    os.makedirs(out_dir, exist_ok=True)

    frames = run_simulation()

    fig = plt.figure(figsize=(13, 6), facecolor=PALETTE["bg"])
    fig.suptitle(
        "Studi Kasus 5 — Simulasi Loket Tiket Bandara  |  Discrete Event Simulation",
        fontsize=13, fontweight="bold", color=PALETTE["dark"])

    ax_main  = fig.add_axes([0.02, 0.08, 0.54, 0.80])
    ax_chart = fig.add_axes([0.62, 0.10, 0.36, 0.76])

    avg_wait_hist = []

    ani = animation.FuncAnimation(
        fig,
        lambda idx: draw_frame(idx, frames, ax_main, ax_chart, avg_wait_hist),
        frames=len(frames),
        interval=400,
        repeat=False,
    )

    path = f"{out_dir}/case5_airport_sim.gif"
    ani.save(path, writer="pillow", fps=2.5)
    plt.close(fig)
    print(f"Animasi disimpan: {path}")


if __name__ == "__main__":
    main()
