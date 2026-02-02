import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ============================================================
# SETUP
# ============================================================
plt.rcParams.update({
    "figure.facecolor": "#0A1628",
    "axes.facecolor": "#0A1628",
    "axes.edgecolor": "#1a2d4a",
    "axes.labelcolor": "#8899AA",
    "xtick.color": "#8899AA",
    "ytick.color": "#8899AA",
    "text.color": "#FFFFFF",
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
})

ACCENT = "#00D4AA"
RED = "#FF6B6B"
BLUE = "#3498db"
YELLOW = "#F1C40F"
SUBTLE = "#8899AA"
BG = "#0A1628"
DARK_CARD = "#132039"

booking = pd.read_csv("data/cleaned/booking_cleaned.csv")
tripadvisor = pd.read_csv("data/cleaned/tripadvisor_cleaned.csv")

# ============================================================
# FINDING 1: Paying more does NOT guarantee better experience
# ============================================================
booking["price_bracket"] = pd.cut(booking["price_eur"],
    bins=[0, 500, 1000, 2000, 5000, 10000],
    labels=["<500", "500-1k", "1k-2k", "2k-5k", "5k+"])

pb = (
    booking.groupby("price_bracket", observed=True)
    .agg(mean_rating=("rating", "mean"), count=("hotel_name", "count"))
    .reset_index()
)

fig, ax = plt.subplots(figsize=(12, 7))

colors = [RED if r < 8.1 else YELLOW if r < 8.25 else ACCENT for r in pb["mean_rating"]]
bars = ax.bar(pb["price_bracket"].astype(str), pb["mean_rating"], color=colors, alpha=0.85, width=0.55)

for bar, rating, count in zip(bars, pb["mean_rating"], pb["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
            f"{rating:.2f}", ha="center", fontsize=15, fontweight="bold", color="#FFFFFF")
    ax.text(bar.get_x() + bar.get_width()/2, 7.55,
            f"n={count}", ha="center", fontsize=10, color=SUBTLE)

ax.set_ylim(7.5, 8.7)
ax.set_title("Paying More Does NOT Guarantee a Better Experience", fontsize=18, pad=20)
ax.set_xlabel("Price per Night (EUR)", fontsize=13)
ax.set_ylabel("Average Rating", fontsize=13)

# Annotation - positioned at the top, no overlap
ax.text(0.5, 0.92, "Only +0.28 rating difference between cheapest and most expensive",
        transform=ax.transAxes, ha="center", fontsize=13, color=RED,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=DARK_CARD, edgecolor=RED, alpha=0.9))

plt.tight_layout()
plt.savefig("output/charts/finding_01_price_vs_rating.png", dpi=150, bbox_inches="tight")
plt.close()
print("1/6 saved")

# ============================================================
# FINDING 2: 88% of hotels - Room is the strongest point
# ============================================================
has_both = booking.dropna(subset=["room_score"]).copy()
has_both["gap"] = has_both["room_score"] - has_both["rating"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={"width_ratios": [1, 1.4]})

# Pie chart
room_higher = (has_both["gap"] > 0).sum()
room_equal = (has_both["gap"] == 0).sum()
room_lower = (has_both["gap"] < 0).sum()

sizes = [room_higher, room_equal, room_lower]
pie_colors = [ACCENT, YELLOW, RED]

wedges, texts, autotexts = ax1.pie(
    sizes, colors=pie_colors, startangle=90, autopct="",
    textprops={"color": "#FFFFFF", "fontsize": 11},
    pctdistance=0.75, labeldistance=1.15)

# Manual labels outside
labels_pie = [
    f"Room > Overall\n{room_higher} ({room_higher/len(has_both)*100:.0f}%)",
    f"Equal\n{room_equal} ({room_equal/len(has_both)*100:.0f}%)",
    f"Room < Overall\n{room_lower} ({room_lower/len(has_both)*100:.0f}%)"
]
for text, label in zip(texts, labels_pie):
    text.set_text(label)
    text.set_fontsize(10)

ax1.set_title("Room Score vs Overall Rating", fontsize=15, pad=15, color="#FFFFFF")

# Histogram of gap
ax2.hist(has_both["gap"], bins=40, color=ACCENT, alpha=0.8, edgecolor="none")
ax2.axvline(0, color=RED, linestyle="--", linewidth=2, label="No gap (0)")
ax2.axvline(has_both["gap"].mean(), color=YELLOW, linestyle="--", linewidth=2,
            label=f"Mean gap: +{has_both['gap'].mean():.2f}")
ax2.set_title("Distribution of Gap (Room - Overall)", fontsize=15, pad=15, color="#FFFFFF")
ax2.set_xlabel("Gap (positive = room scores higher than overall)")
ax2.set_ylabel("Number of Hotels")
ax2.legend(facecolor=DARK_CARD, edgecolor="#1a2d4a", fontsize=11, loc="upper right")

plt.tight_layout()
plt.savefig("output/charts/finding_02_room_score_gap.png", dpi=150, bbox_inches="tight")
plt.close()
print("2/6 saved")

# ============================================================
# FINDING 3: Paris = worst value for money
# ============================================================
loc_stats = (
    booking.groupby("location")
    .agg(median_price=("price_eur", "median"), mean_rating=("rating", "mean"),
         count=("hotel_name", "count"))
    .reset_index()
)
loc_stats = loc_stats[loc_stats["count"] >= 10].copy()
loc_stats["value_index"] = (loc_stats["mean_rating"] / loc_stats["median_price"]) * 100

best10 = loc_stats.nlargest(10, "value_index").copy()
worst10 = loc_stats.nsmallest(10, "value_index").copy()

# Two separate subplots side by side
fig, (ax_worst, ax_best) = plt.subplots(1, 2, figsize=(16, 8))

# Worst value (left)
worst10_sorted = worst10.sort_values("value_index", ascending=True)
bars_w = ax_worst.barh(worst10_sorted["location"], worst10_sorted["median_price"],
                        color=RED, alpha=0.85, height=0.6)
for bar, rating in zip(bars_w, worst10_sorted["mean_rating"]):
    ax_worst.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                  f"{rating:.1f}", va="center", fontsize=11, color=YELLOW, fontweight="bold")

ax_worst.set_title("WORST Value (high price, low rating)", fontsize=14, pad=15, color=RED)
ax_worst.set_xlabel("Median Price (EUR)", fontsize=11)
ax_worst.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
# Add "Rating" label at top right
ax_worst.text(1.0, 1.02, "Rating", transform=ax_worst.transAxes, ha="right",
              fontsize=10, color=YELLOW, fontweight="bold")

# Best value (right)
best10_sorted = best10.sort_values("value_index", ascending=True)
bars_b = ax_best.barh(best10_sorted["location"], best10_sorted["median_price"],
                       color=ACCENT, alpha=0.85, height=0.6)
for bar, rating in zip(bars_b, best10_sorted["mean_rating"]):
    ax_best.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
                 f"{rating:.1f}", va="center", fontsize=11, color=YELLOW, fontweight="bold")

ax_best.set_title("BEST Value (low price, high rating)", fontsize=14, pad=15, color=ACCENT)
ax_best.set_xlabel("Median Price (EUR)", fontsize=11)
ax_best.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax_best.text(1.0, 1.02, "Rating", transform=ax_best.transAxes, ha="right",
             fontsize=10, color=YELLOW, fontweight="bold")

fig.suptitle("Best vs Worst Value Destinations", fontsize=20, fontweight="bold",
             color="#FFFFFF", y=1.02)

plt.tight_layout()
plt.savefig("output/charts/finding_03_best_worst_value.png", dpi=150, bbox_inches="tight")
plt.close()
print("3/6 saved")

# ============================================================
# FINDING 4: Most overpriced hotels
# ============================================================
mask = booking["price_eur"] < 5000
coeffs = np.polyfit(booking.loc[mask, "price_eur"], booking.loc[mask, "rating"], 1)
bf = booking[mask].copy()
bf["expected"] = np.polyval(coeffs, bf["price_eur"])
bf["residual"] = bf["rating"] - bf["expected"]

overpriced = bf[bf["num_reviews"] >= 50].nsmallest(7, "residual").copy()

fig, ax = plt.subplots(figsize=(14, 8))

# Scatter all
ax.scatter(bf["price_eur"], bf["rating"], alpha=0.12, s=12, color=SUBTLE)

# Trend line
x_line = np.linspace(0, 5000, 100)
ax.plot(x_line, np.polyval(coeffs, x_line), color=YELLOW, linewidth=2, linestyle="--",
        label="Expected rating (trend)")

# Overpriced highlighted
ax.scatter(overpriced["price_eur"], overpriced["rating"], color=RED, s=100, zorder=5,
           edgecolors="#FFFFFF", linewidth=0.8, label="Most overpriced")

# Stagger annotations to avoid overlap
offsets = [
    (250, 0.6), (-400, 0.8), (250, -0.8), (-400, -0.5),
    (300, 0.5), (-350, -0.7), (200, 0.4)
]
for i, (_, row) in enumerate(overpriced.iterrows()):
    name = row["hotel_name"][:22]
    ox, oy = offsets[i % len(offsets)]
    ax.annotate(
        f"{name}\n{row['location']}\nRating: {row['rating']}",
        xy=(row["price_eur"], row["rating"]),
        xytext=(row["price_eur"] + ox, row["rating"] + oy),
        fontsize=8, color=RED,
        arrowprops=dict(arrowstyle="->", color=RED, lw=0.8),
        bbox=dict(boxstyle="round,pad=0.3", facecolor=DARK_CARD, edgecolor=RED, alpha=0.85))

ax.set_title("Overpriced Hotels: High Price, Low Rating", fontsize=18, pad=20)
ax.set_xlabel("Price per Night (EUR)", fontsize=13)
ax.set_ylabel("Rating", fontsize=13)
ax.set_xlim(0, 5000)
ax.set_ylim(1, 10.5)
ax.legend(facecolor=DARK_CARD, edgecolor="#1a2d4a", fontsize=11, loc="lower right")

plt.tight_layout()
plt.savefig("output/charts/finding_04_overpriced_hotels.png", dpi=150, bbox_inches="tight")
plt.close()
print("4/6 saved")

# ============================================================
# FINDING 5: Popularity bias
# ============================================================
booking["review_bracket"] = pd.cut(booking["num_reviews"],
    bins=[0, 50, 200, 500, 1000, 5000, 100000],
    labels=["<50", "50-200", "200-500", "500-1k", "1k-5k", "5k+"])

rb = (
    booking.groupby("review_bracket", observed=True)
    .agg(mean_rating=("rating", "mean"), median_price=("price_eur", "median"),
         count=("hotel_name", "count"))
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(12, 7))

x = range(len(rb))
bars = ax1.bar(x, rb["mean_rating"], color=ACCENT, alpha=0.85, width=0.5)
ax1.set_xticks(x)
ax1.set_xticklabels(rb["review_bracket"].astype(str), fontsize=12)
ax1.set_ylabel("Mean Rating", color=ACCENT, fontsize=13)
ax1.set_ylim(7.8, 8.6)

for bar, rating, count in zip(bars, rb["mean_rating"], rb["count"]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f"{rating:.2f}", ha="center", fontsize=11, fontweight="bold", color="#FFFFFF")
    ax1.text(bar.get_x() + bar.get_width()/2, 7.83,
             f"n={count}", ha="center", fontsize=9, color=SUBTLE)

ax2 = ax1.twinx()
ax2.plot(x, rb["median_price"], color=RED, marker="o", linewidth=2.5, markersize=10)
ax2.set_ylabel("Median Price (EUR)", color=RED, fontsize=13)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"EUR {v:,.0f}"))

ax1.set_title("Rating & Price by Number of Reviews", fontsize=18, pad=20)
ax1.set_xlabel("Number of Reviews", fontsize=13)

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color=ACCENT, lw=8, alpha=0.85, label="Mean Rating"),
    Line2D([0], [0], color=RED, lw=2.5, marker="o", markersize=8, label="Median Price (EUR)")
]
ax1.legend(handles=legend_elements, facecolor=DARK_CARD, edgecolor="#1a2d4a",
           fontsize=11, loc="upper left")

plt.tight_layout()
plt.savefig("output/charts/finding_05_popularity_bias.png", dpi=150, bbox_inches="tight")
plt.close()
print("5/6 saved")

# ============================================================
# FINDING 6: Cheaper hotels = longer reviews
# ============================================================
ta = tripadvisor.dropna(subset=["comment"]).copy()
ta["comment_words"] = ta["comment"].str.split().str.len()
ta["price_bracket"] = pd.cut(ta["price_eur"],
    bins=[0, 30, 60, 100, 200, 10000],
    labels=["<30", "30-60", "60-100", "100-200", "200+"])

cp = (
    ta.groupby("price_bracket", observed=True)
    .agg(mean_words=("comment_words", "mean"), count=("hotel_name", "count"))
    .reset_index()
)

fig, ax = plt.subplots(figsize=(12, 7))

colors_gradient = [ACCENT, "#2ECC71", YELLOW, "#E67E22", RED]
bars = ax.bar(cp["price_bracket"].astype(str), cp["mean_words"],
              color=colors_gradient, alpha=0.85, width=0.55)

for bar, words, count in zip(bars, cp["mean_words"], cp["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            f"{words:.0f} words", ha="center", fontsize=14, fontweight="bold", color="#FFFFFF")
    ax.text(bar.get_x() + bar.get_width()/2, 1.5,
            f"n={count}", ha="center", fontsize=10, color=SUBTLE)

ax.set_title("Cheaper Hotels Get Longer Reviews", fontsize=18, pad=20)
ax.set_xlabel("Price per Night (EUR)", fontsize=13)
ax.set_ylabel("Average Words per Review", fontsize=13)
ax.set_ylim(0, 35)

# Annotation - clean, at top center
ax.text(0.5, 0.92, "Budget guests write 2x more words than luxury guests  |  Spearman r = -0.43",
        transform=ax.transAxes, ha="center", fontsize=12, color=RED,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=DARK_CARD, edgecolor=RED, alpha=0.9))

plt.tight_layout()
plt.savefig("output/charts/finding_06_review_length.png", dpi=150, bbox_inches="tight")
plt.close()
print("6/6 saved")

print("\nAll 6 finding charts saved!")
