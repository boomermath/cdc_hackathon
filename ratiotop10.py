"""
Incident-to-death ratio for the top 10 hydrometeorological hazards
Reads countdeath.csv (event_type, sum(deaths_direct), count_star())
NOAA Storm Events Database, 2010 - June 2026

Put this file next to countdeath.csv, then run in Windows Terminal:
    py -m pip install pandas matplotlib
    py incident_death_ratio_csv.py
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.transforms import blended_transform_factory

# ---------------------------------------------------------------- settings
CSV_FILE = "countdeath.csv"
OUTPUT_FILE = "incident_death_ratio.png"
HIGHLIGHT = "Rip Current"
TOP_N = 10

# Hydrometeorological (water-related) types, as tagged in the team's export
HYDRO_TYPES = [
    "Flash Flood", "Rip Current", "Thunderstorm Wind", "Flood", "High Surf",
    "Hurricane (Typhoon)", "Tropical Storm", "Marine Strong Wind", "Coastal Flood",
    "Marine Thunderstorm Wind", "Heavy Rain", "Marine Tropical Storm",
    "Storm Surge/Tide", "Waterspout", "Marine High Wind", "Lakeshore Flood",
    "Tsunami", "Marine Lightning", "Tropical Depression", "Marine Hurricane/Typhoon",
    "Marine Tropical Depression", "Marine Hail",
]

# Rip Current theme colors
HIGHLIGHT_COLOR = "#22537f"   # rip: the one highlighted bar
OTHER_COLOR = "#b5e4f6"       # shallow: every other bar
BACKGROUND = "#ffffff"        # surface
INK = "#0b0b0b"               # titles, labels, values
INK_MUTED = "#52514e"         # subtitle, ticks, notes
GRID = "#e2e1db"              # gridlines
AXIS = "#cac9c0"              # zero line

# ---------------------------------------------------------------- load data
if not Path(CSV_FILE).exists():
    sys.exit(f"Can't find {CSV_FILE} in {Path('.').resolve()}")

df = pd.read_csv(CSV_FILE)
df.columns = ["event_type", "direct_deaths", "incidents"]

# "Hurricane" is a newer label for the same hazard as "Hurricane (Typhoon)"
df["event_type"] = df["event_type"].replace({"Hurricane": "Hurricane (Typhoon)"})
df = df.groupby("event_type", as_index=False)[["direct_deaths", "incidents"]].sum()

# Top 10 hydrometeorological hazards by direct deaths
top = (df[df["event_type"].isin(HYDRO_TYPES)]
       .sort_values("direct_deaths", ascending=False)
       .head(TOP_N)
       .copy())
top["deaths_per_100"] = 100 * top["direct_deaths"] / top["incidents"]
top = top.sort_values("deaths_per_100", ascending=False).reset_index(drop=True)

print(top.round(2).to_string(index=False))

# ---------------------------------------------------------------- plot
names = top["event_type"].tolist()
values = top["deaths_per_100"].tolist()
counts = top["incidents"].tolist()
colors = [HIGHLIGHT_COLOR if n == HIGHLIGHT else OTHER_COLOR for n in names]

available = {f.name for f in font_manager.fontManager.ttflist}
font = next((f for f in ["Jost", "Futura", "Century Gothic", "Avenir Next"] if f in available), "DejaVu Sans")
plt.rcParams["font.family"] = font

fig_height = 2.4 + 0.5 * len(names)
fig, ax = plt.subplots(figsize=(11, fig_height), dpi=100)
fig.patch.set_facecolor(BACKGROUND)
ax.set_facecolor(BACKGROUND)

y = range(len(names))
ax.barh(y, values, height=0.5, color=colors, zorder=3)
ax.invert_yaxis()  # highest ratio on top

ax.set_yticks(list(y))
ax.set_yticklabels(names, fontsize=12, color=INK)

xmax = max(values) * 1.15
for i, v in enumerate(values):
    ax.text(v + xmax * 0.01, i, f"{v:.1f}", va="center", ha="left", fontsize=11,
            color=INK, fontweight="normal")

# Number of incidents behind each ratio, at the right edge
col = blended_transform_factory(ax.transAxes, ax.transData)
ax.text(1.03, -0.9, "Incidents", transform=col, ha="left", va="bottom", fontsize=9, color=INK_MUTED)
for i, n in enumerate(counts):
    ax.text(1.03, i, f"{n:,}", transform=col, ha="left", va="center", fontsize=10, color=INK_MUTED)

ax.set_xlim(0, xmax)
ax.xaxis.grid(True, color=GRID, linewidth=1, zorder=0)
ax.tick_params(axis="both", length=0)
ax.tick_params(axis="x", colors=INK_MUTED, labelsize=10)
for side in ["top", "right", "bottom"]:
    ax.spines[side].set_visible(False)
ax.spines["left"].set_color(AXIS)
ax.set_xlabel("Direct Deaths per 100 Reported Incidents", fontsize=11, color=INK_MUTED)

rank = names.index(HIGHLIGHT) + 1 if HIGHLIGHT in names else None
if rank == 1:
    title = "Rip Currents Have the Most Deaths per Reported Incident"
elif rank:
    title = f"Rip Currents Rank #{rank} in Deaths per Reported Incident"
else:
    title = f"Deaths per Reported Incident, Top {TOP_N} Hydrometeorological Hazards"
fig.text(0.02, 1 - 0.45 / fig_height, title, fontsize=17, fontweight="bold", color=INK)
fig.text(0.02, 1 - 0.75 / fig_height,
         f"Direct deaths per 100 reported incidents, top {TOP_N} hydrometeorological hazards, "
         "NOAA Storm Events Database, 2010 to June 2026",
         fontsize=10.5, color=INK_MUTED)


fig.subplots_adjust(left=0.22, right=0.88, top=1 - 1.25 / fig_height, bottom=0.95 / fig_height)
fig.savefig(OUTPUT_FILE, facecolor=BACKGROUND, dpi=200)
print(f"\nSaved chart to {OUTPUT_FILE}")
#plt.show()