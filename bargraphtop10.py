"""
Top 10 marine natural disasters by direct deaths
NOAA Storm Events Database, 2010 - June 2026

Run in Windows Terminal:
    py -m pip install matplotlib
    py top10_marine_deaths.py
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Futura']

# Event types marked "a" (marine) in the export, with sum(deaths_direct)
MARINE_DEATHS = {
    "Flash Flood": 1303,
    "Rip Current": 929,
    "Thunderstorm Wind": 528,
    "Flood": 437,
    "High Surf": 168,
    "Hurricane (Typhoon)": 126,
    "Tropical Storm": 111,
    "Marine Strong Wind": 58,
    "Coastal Flood": 47,
    "Marine Thunderstorm Wind": 38,
    "Heavy Rain": 35,
    "Marine Tropical Storm": 29,
    "Storm Surge/Tide": 23,
    "Hurricane": 7,
    "Waterspout": 3,
    "Marine High Wind": 2,
    "Lakeshore Flood": 2,
    "Tsunami": 1,
    "Marine Lightning": 1,
    "Tropical Depression": 1,
    "Marine Hurricane/Typhoon": 0,
    "Marine Tropical Depression": 0,
    "Marine Hail": 0,
}

EXCLUDE = []            
HIGHLIGHT = "Rip Current"
TOP_N = 10
OUTPUT_FILE = "top10_marine_deaths.png"

HIGHLIGHT_COLOR = "#015482"   # Blue: the bar that stands out
OTHER_COLOR = "#a7e6f8"       # Light Blue for the rest
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"
BACKGROUND = "#ffffff"

# "Hurricane" is a newer label for the same hazard as "Hurricane (Typhoon)"
deaths = dict(MARINE_DEATHS)
deaths["Hurricane (Typhoon)"] += deaths.pop("Hurricane", 0)
for name in EXCLUDE:
    deaths.pop(name, None)

# Top N, largest first
top = sorted(deaths.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
names = [n for n, _ in top]
values = [v for _, v in top]
colors = [HIGHLIGHT_COLOR if n == HIGHLIGHT else OTHER_COLOR for n in names]

# Figure height grows with the number of bars
fig_height = 1.8 + 0.5 * TOP_N
fig, ax = plt.subplots(figsize=(10, fig_height), dpi=100)
fig.patch.set_facecolor(BACKGROUND)
ax.set_facecolor(BACKGROUND)

y = range(len(names))
ax.barh(y, values, height=0.5, color=colors, zorder=3)
ax.invert_yaxis()  # largest bar on top

# Category labels (rip current in bold)
ax.set_yticks(list(y))
ax.set_yticklabels(names, fontsize=12, color=INK)

# Value at the end of each bar
xmax = max(values) * 1.15
for i, v in enumerate(values):
    ax.text(v + xmax * 0.01, i, f"{v:,}", va="center", ha="left", fontsize=11,
            color=INK, fontweight="normal")

# Quiet axes and gridlines
ax.set_xlim(0, xmax)
ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax.xaxis.grid(True, color=GRID, linewidth=1, zorder=0)
ax.tick_params(axis="both", length=0)
ax.tick_params(axis="x", colors=INK_SECONDARY, labelsize=10)
for side in ["top", "right", "bottom"]:
    ax.spines[side].set_visible(False)
ax.spines["left"].set_color("#c3c2b7")
ax.set_xlabel("Direct deaths", fontsize=11, color=INK_SECONDARY)

# Title and subtitle
rank = names.index(HIGHLIGHT) + 1 if HIGHLIGHT in names else None
title = ("Rip Currents Rank #2 in Deadliest Hydrometeorological Hazards")
fig.text(0.02, 1 - 0.45 / fig_height, title, fontsize=17, fontweight="bold", color=INK)
fig.text(0.02, 1 - 0.75 / fig_height,
         f"Top {TOP_N} hydrometeorological hazards by direct deaths, "
         "NOAA Storm Events Database, 2010 to June 2026",
         fontsize=11, color=INK_SECONDARY)

fig.subplots_adjust(left=0.25, right=0.95, top=1 - 1.1 / fig_height, bottom=0.65 / fig_height)
fig.savefig(OUTPUT_FILE, facecolor=BACKGROUND, dpi=200)
print(f"Saved chart to {OUTPUT_FILE}")
# plt.show()