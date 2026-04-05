"""
Generates TerraAlert Risk Trend Figure showing exponential decay scoring
for four disaster types across a 7-day rolling window.
Saved as: Diagrams/risk_trend_figure.jpg
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# ── Simulated report data ─────────────────────────────────────────────────
# Each entry: (disaster_type, days_ago, severity_weight)
EVENTS = [
    ("Flood",       0.1, 1.5),
    ("Flood",       0.4, 1.5),
    ("Flood",       1.2, 1.5),
    ("Flood",       3.0, 1.5),
    ("Flood",       5.5, 1.5),
    ("Earthquake",  0.3, 2.0),
    ("Earthquake",  2.1, 2.0),
    ("Earthquake",  4.8, 2.0),
    ("Cyclone",     1.0, 1.8),
    ("Cyclone",     3.5, 1.8),
    ("Cyclone",     6.5, 1.8),
    ("Heatwave",    0.8, 1.2),
    ("Heatwave",    2.5, 1.2),
    ("Heatwave",    5.0, 1.2),
]

HALF_LIFE = 3.0       # days
POINTS_PER_REPORT = 10

COLORS = {
    "Flood":      "#2196F3",
    "Earthquake": "#F44336",
    "Cyclone":    "#9C27B0",
    "Heatwave":   "#FF9800",
}
TYPES = list(COLORS.keys())

# ── Time axis: evaluate risk score at each hour for 7 days ────────────────
base = datetime(2026, 4, 5, 12, 0)   # "now"
hours = np.arange(0, 7*24 + 1, 1)    # one point per hour
times = [base - timedelta(hours=float(h)) for h in reversed(hours)]
t_arr = np.array([(base - t).total_seconds() / 86400 for t in times])  # days from now (positive = future display = past data)

def risk_at_point(d_type, t_eval_days):
    """Risk contributed by a disaster type at a given evaluation time."""
    score = 0.0
    for dtype, days_ago, weight in EVENTS:
        if dtype == d_type:
            age = t_eval_days + days_ago     # age at that point in the past
            if 0 <= age <= 7:
                score += POINTS_PER_REPORT * weight * np.exp(-age / HALF_LIFE)
    return min(score, 100)

# Build curves (evaluate over a rolling window relative to 'now')
rolling_days = np.linspace(0, 7, len(times))
curves = {d: np.array([risk_at_point(d, r) for r in rolling_days]) for d in TYPES}

# Overall combined (capped)
overall = np.clip(sum(curves.values()), 0, 100)

# ── Plot ──────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=False,
                                gridspec_kw={"height_ratios": [3, 1.4]})
fig.patch.set_facecolor("#0D1B2A")

for ax in (ax1, ax2):
    ax.set_facecolor("#0D1B2A")
    for spine in ax.spines.values():
        spine.set_edgecolor("#2C4A6E")
    ax.tick_params(colors="#A0B8D0", labelsize=9)
    ax.yaxis.label.set_color("#A0B8D0")
    ax.xaxis.label.set_color("#A0B8D0")

x_days = np.linspace(-7, 0, len(times))   # -7 days ago → 0 = now

# ── Ax1: Per-Type Risk Lines ──────────────────────────────────────────────
for d_type in TYPES:
    ax1.plot(x_days, curves[d_type], label=d_type,
             color=COLORS[d_type], linewidth=2.0, alpha=0.9)
    ax1.fill_between(x_days, curves[d_type], alpha=0.08, color=COLORS[d_type])

ax1.axvline(0, color="#FFFFFF", linewidth=1.2, linestyle="--", alpha=0.4, label="Now")
ax1.set_ylabel("Risk Score (0–100)", fontsize=10, color="#A0B8D0")
ax1.set_title("TerraAlert – Localised Disaster Risk Trend (7-Day Rolling Window)",
              fontsize=13, color="#E8F4FD", fontweight="bold", pad=12)
ax1.legend(loc="upper left", framealpha=0.25, labelcolor="white",
           facecolor="#0D1B2A", edgecolor="#2C4A6E", fontsize=9)
ax1.set_ylim(0, 105)
ax1.set_xlim(-7, 0.3)
ax1.grid(axis="y", color="#2C4A6E", alpha=0.5, linewidth=0.6)

# Risk thresholds
ax1.axhline(35, color="#FFEB3B", linewidth=1.0, linestyle=":", alpha=0.7)
ax1.text(0.1, 36, "Medium Threshold (35%)", color="#FFEB3B", fontsize=7.5, va="bottom", alpha=0.8)
ax1.axhline(70, color="#FF5722", linewidth=1.0, linestyle=":", alpha=0.7)
ax1.text(0.1, 71, "High Threshold (70%)", color="#FF5722", fontsize=7.5, va="bottom", alpha=0.8)

# ── Ax2: Overall Combined Risk ────────────────────────────────────────────
ax2.fill_between(x_days, overall, alpha=0.35, color="#00BCD4")
ax2.plot(x_days, overall, color="#00BCD4", linewidth=2.2, label="Overall Risk")
ax2.axvline(0, color="#FFFFFF", linewidth=1.2, linestyle="--", alpha=0.4)
ax2.set_ylabel("Overall %", fontsize=9, color="#A0B8D0")
ax2.set_xlabel("Days Before Present", fontsize=10, color="#A0B8D0")
ax2.set_ylim(0, 105)
ax2.set_xlim(-7, 0.3)
ax2.grid(axis="y", color="#2C4A6E", alpha=0.5, linewidth=0.6)
ax2.legend(loc="upper left", framealpha=0.25, labelcolor="white",
           facecolor="#0D1B2A", edgecolor="#2C4A6E", fontsize=9)

# X-axis labels (shared)
ax2.set_xticks(range(-7, 1))
ax2.set_xticklabels([f"Day -{abs(d)}" if d != 0 else "Now" for d in range(-7, 1)],
                    fontsize=8, color="#A0B8D0")

plt.tight_layout(pad=2.0)
out = "Diagrams/risk_trend_figure.jpg"
plt.savefig(out, dpi=180, format="jpeg",
            bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {out}")
