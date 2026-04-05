"""
Generates TerraAlert Risk Decay Formula Figure.
Two panels:
  Top   – annotated formula card showing the equation + parameter table
  Bottom – decay curve comparison for three half-life settings + severity bands
Saved as: Diagrams/risk_decay_formula_figure.jpg
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

BG        = "#0D1B2A"
PANEL_BG  = "#112233"
GRID_COL  = "#1E3A5F"
TEXT_MAIN = "#E8F4FD"
TEXT_DIM  = "#7BA7C8"

HALF_LIVES = [1.5, 3.0, 6.0]
HL_COLORS  = ["#FF5722", "#2196F3", "#4CAF50"]
HL_LABELS  = ["Half-life = 1.5 days (aggressive)", "Half-life = 3.0 days (default)", "Half-life = 6.0 days (lenient)"]

SEVERITY   = {"Low (×1.2)": 1.2, "Medium (×1.5)": 1.5, "High (×2.0)": 2.0}
SEV_COLORS = {"Low (×1.2)": "#4CAF50", "Medium (×1.5)": "#FFEB3B", "High (×2.0)": "#F44336"}
POINTS     = 10    # base points per report

# ── Figure layout ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(13, 10), facecolor=BG)
gs  = fig.add_gridspec(2, 2, height_ratios=[1, 1.8], hspace=0.35, wspace=0.35,
                        left=0.07, right=0.97, top=0.93, bottom=0.06)

ax_formula = fig.add_subplot(gs[0, :])   # full-width formula panel
ax_decay   = fig.add_subplot(gs[1, 0])   # half-life comparison
ax_sev     = fig.add_subplot(gs[1, 1])   # severity × decay

for ax in (ax_formula, ax_decay, ax_sev):
    ax.set_facecolor(PANEL_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)

# ══════════════════════════════════════════════════════════════════════════════
# Panel A – Formula Card
# ══════════════════════════════════════════════════════════════════════════════
ax_formula.set_xlim(0, 1)
ax_formula.set_ylim(0, 1)
ax_formula.axis("off")

# Background card
card = FancyBboxPatch((0.01, 0.05), 0.98, 0.88,
                       boxstyle="round,pad=0.02", linewidth=1.5,
                       edgecolor=GRID_COL, facecolor="#0A1929")
ax_formula.add_patch(card)

# Title
ax_formula.text(0.5, 0.90, "TerraAlert Risk Score Decay Formula",
                ha="center", va="center", fontsize=13,
                color=TEXT_MAIN, fontweight="bold",
                transform=ax_formula.transAxes)

# Main formula using LaTeX
formula_str = (
    r"$\mathrm{Risk}(t) = \min\!\left("
    r"\,\sum_{i=1}^{N} w_i \cdot P \cdot e^{-\,age_i\,/\,h}\;,"
    r"\;100\right)$"
)
ax_formula.text(0.5, 0.60, formula_str,
                ha="center", va="center", fontsize=16,
                color="#64B5F6", fontweight="bold",
                transform=ax_formula.transAxes)

# Parameter table
params = [
    ("t",       "Current evaluation timestamp"),
    ("N",       "Total number of reports in the 7-day window"),
    ("wᵢ",      "Severity weight of report i  (Low = 1.2 | Medium = 1.5 | High = 2.0)"),
    ("P",       "Base points per report  (default = 10)"),
    ("age_i",   "Age of report i in days  (0 = just now)"),
    ("h",       "Half-life constant in days  (default = 3.0)"),
    ("e^(−age/h)", "Exponential decay factor  (→ 1 when age = 0, → 0 as age → ∞)"),
]

col_x = [0.07, 0.17]
row_y_start = 0.43
row_step    = 0.065

for idx, (sym, desc) in enumerate(params):
    y = row_y_start - idx * row_step
    ax_formula.text(col_x[0], y, sym,
                    ha="left", va="center", fontsize=9.5,
                    color="#FFD54F", fontweight="bold",
                    transform=ax_formula.transAxes)
    ax_formula.text(col_x[0] + 0.01, y - 0.001, "—",
                    ha="left", va="center", fontsize=9, color=TEXT_DIM,
                    transform=ax_formula.transAxes)
    ax_formula.text(col_x[1], y, desc,
                    ha="left", va="center", fontsize=9,
                    color=TEXT_DIM, transform=ax_formula.transAxes)

ax_formula.set_title("A – Formula Definition", loc="left",
                      fontsize=10, color=TEXT_DIM, pad=6)

# ══════════════════════════════════════════════════════════════════════════════
# Panel B – Half-life Comparison (single report, P=10, w=1.5)
# ══════════════════════════════════════════════════════════════════════════════
days = np.linspace(0, 7, 400)

for hl, col, lbl in zip(HALF_LIVES, HL_COLORS, HL_LABELS):
    score = POINTS * 1.5 * np.exp(-days / hl)
    ax_decay.plot(days, score, color=col, linewidth=2.2, label=lbl)
    ax_decay.fill_between(days, score, alpha=0.07, color=col)

ax_decay.axhline(35 * POINTS * 1.5 / 100, color="#FFD54F", linestyle=":", linewidth=1, alpha=0.6)
ax_decay.axhline(70 * POINTS * 1.5 / 100, color="#FF5722", linestyle=":", linewidth=1, alpha=0.6)

ax_decay.set_xlabel("Age of Report (days)", fontsize=9, color=TEXT_DIM)
ax_decay.set_ylabel("Score Contribution (single report)", fontsize=9, color=TEXT_DIM)
ax_decay.set_title("B – Half-life Comparison  (w = 1.5, P = 10)", fontsize=10, color=TEXT_DIM, pad=6)
ax_decay.legend(fontsize=7.5, labelcolor="white", facecolor=BG,
                edgecolor=GRID_COL, framealpha=0.4)
ax_decay.set_xlim(0, 7)
ax_decay.set_ylim(0)
ax_decay.tick_params(colors=TEXT_DIM)
ax_decay.grid(axis="both", color=GRID_COL, alpha=0.5, linewidth=0.6)

# ══════════════════════════════════════════════════════════════════════════════
# Panel C – Severity × Decay at default half-life (h=3)
# ══════════════════════════════════════════════════════════════════════════════
hl_default = 3.0

for label, weight in SEVERITY.items():
    score = POINTS * weight * np.exp(-days / hl_default)
    ax_sev.plot(days, score, color=SEV_COLORS[label], linewidth=2.2, label=label)
    ax_sev.fill_between(days, score, alpha=0.08, color=SEV_COLORS[label])

ax_sev.set_xlabel("Age of Report (days)", fontsize=9, color=TEXT_DIM)
ax_sev.set_ylabel("Score Contribution (single report)", fontsize=9, color=TEXT_DIM)
ax_sev.set_title("C – Severity Weighting Effect  (h = 3.0 days, P = 10)", fontsize=10, color=TEXT_DIM, pad=6)
ax_sev.legend(fontsize=8, labelcolor="white", facecolor=BG,
              edgecolor=GRID_COL, framealpha=0.4)
ax_sev.set_xlim(0, 7)
ax_sev.set_ylim(0)
ax_sev.tick_params(colors=TEXT_DIM)
ax_sev.grid(axis="both", color=GRID_COL, alpha=0.5, linewidth=0.6)

# ── Master title ─────────────────────────────────────────────────────────
fig.suptitle(
    "Figure 12 – TerraAlert Risk Decay Formula and Parameter Analysis",
    fontsize=13, color=TEXT_MAIN, fontweight="bold", y=0.97
)

out = r"Diagrams/risk_decay_formula_figure.jpg"
plt.savefig(out, dpi=180, format="jpeg",
            bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out}")
