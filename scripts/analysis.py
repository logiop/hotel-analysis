import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.gridspec import GridSpec

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
SUBTLE = "#8899AA"
BG = "#0A1628"

booking = pd.read_csv("data/cleaned/booking_cleaned.csv")
tripadvisor = pd.read_csv("data/cleaned/tripadvisor_cleaned.csv")

# ============================================================
# 1. PRICE DISTRIBUTION - Booking vs TripAdvisor
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))

ax.hist(booking["price_eur"], bins=60, range=(0, 2000), alpha=0.7,
        color=ACCENT, label=f"Booking.com (n={len(booking)})", edgecolor="none")
ax.hist(tripadvisor["price_eur"], bins=60, range=(0, 2000), alpha=0.7,
        color=RED, label=f"TripAdvisor (n={len(tripadvisor)})", edgecolor="none")

ax.axvline(booking["price_eur"].median(), color=ACCENT, linestyle="--", linewidth=1.5,
           label=f"Booking median: EUR {booking['price_eur'].median():.0f}")
ax.axvline(tripadvisor["price_eur"].median(), color=RED, linestyle="--", linewidth=1.5,
           label=f"TripAdvisor median: EUR {tripadvisor['price_eur'].median():.0f}")

ax.set_title("Price Distribution: Booking.com vs TripAdvisor")
ax.set_xlabel("Price per Night (EUR)")
ax.set_ylabel("Number of Hotels")
ax.legend(facecolor="#132039", edgecolor="#1a2d4a", fontsize=10)
ax.set_xlim(0, 2000)

plt.tight_layout()
plt.savefig("output/charts/01_price_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("1/6 Price distribution saved")

# ============================================================
# 2. RATING vs PRICE (Booking)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 7))

scatter = ax.scatter(
    booking["price_eur"], booking["rating"],
    c=booking["room_score"], cmap="RdYlGn", alpha=0.5, s=20,
    edgecolors="none", vmin=5, vmax=10
)

cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label("Room Score", color=SUBTLE)
cbar.ax.yaxis.set_tick_params(color=SUBTLE)
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=SUBTLE)

ax.set_title("Does Higher Price Mean Better Rating?")
ax.set_xlabel("Price per Night (EUR)")
ax.set_ylabel("Overall Rating")
ax.set_xlim(0, 3000)
ax.set_ylim(1, 10.5)

plt.tight_layout()
plt.savefig("output/charts/02_rating_vs_price.png", dpi=150, bbox_inches="tight")
plt.close()
print("2/6 Rating vs Price saved")

# ============================================================
# 3. TOP 20 LOCATIONS BY MEDIAN PRICE
# ============================================================
loc_stats = (
    booking.groupby("location")
    .agg(
        median_price=("price_eur", "median"),
        mean_rating=("rating", "mean"),
        count=("hotel_name", "count")
    )
    .reset_index()
)
# At least 10 hotels per location
loc_stats = loc_stats[loc_stats["count"] >= 10].sort_values("median_price", ascending=True)

top20 = loc_stats.tail(20)

fig, ax = plt.subplots(figsize=(12, 8))

bars = ax.barh(top20["location"], top20["median_price"], color=ACCENT, alpha=0.8, height=0.7)

for bar, rating in zip(bars, top20["mean_rating"]):
    ax.text(bar.get_width() + 15, bar.get_y() + bar.get_height()/2,
            f"Rating: {rating:.1f}", va="center", fontsize=9, color=SUBTLE)

ax.set_title("Top 20 Most Expensive Locations (min. 10 hotels)")
ax.set_xlabel("Median Price per Night (EUR)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"EUR {x:,.0f}"))

plt.tight_layout()
plt.savefig("output/charts/03_top_locations_price.png", dpi=150, bbox_inches="tight")
plt.close()
print("3/6 Top locations saved")

# ============================================================
# 4. REVIEW SCORE CATEGORIES (Booking)
# ============================================================
score_order = ["Exceptional", "Wonderful", "Superb", "Fabulous",
               "Very Good", "Good", "Pleasant", "Review score"]

score_stats = (
    booking[booking["review_score"].isin(score_order)]
    .groupby("review_score")
    .agg(
        median_price=("price_eur", "median"),
        mean_rating=("rating", "mean"),
        count=("hotel_name", "count")
    )
    .reindex(score_order)
    .dropna()
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(12, 6))

x = range(len(score_stats))
bars = ax1.bar(x, score_stats["median_price"], color=ACCENT, alpha=0.8, width=0.5)
ax1.set_xticks(x)
ax1.set_xticklabels(score_stats["review_score"], rotation=30, ha="right")
ax1.set_ylabel("Median Price (EUR)", color=ACCENT)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"EUR {v:,.0f}"))

ax2 = ax1.twinx()
ax2.plot(x, score_stats["mean_rating"], color=RED, marker="o", linewidth=2, markersize=8)
ax2.set_ylabel("Mean Rating", color=RED)
ax2.spines["right"].set_color(RED)

# Count labels on bars
for i, (bar, count) in enumerate(zip(bars, score_stats["count"])):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
             f"n={count}", ha="center", fontsize=9, color=SUBTLE)

ax1.set_title("Price & Rating by Review Category")

plt.tight_layout()
plt.savefig("output/charts/04_review_categories.png", dpi=150, bbox_inches="tight")
plt.close()
print("4/6 Review categories saved")

# ============================================================
# 5. ROOM TYPE ANALYSIS (Booking)
# ============================================================
# Simplify room types
def simplify_room(rt):
    rt = str(rt).lower()
    if "suite" in rt:
        return "Suite"
    elif "villa" in rt:
        return "Villa"
    elif "deluxe" in rt:
        return "Deluxe"
    elif "superior" in rt:
        return "Superior"
    elif "standard" in rt:
        return "Standard"
    elif "double" in rt:
        return "Double"
    elif "twin" in rt:
        return "Twin"
    elif "single" in rt:
        return "Single"
    elif "family" in rt:
        return "Family"
    elif "studio" in rt:
        return "Studio"
    else:
        return "Other"

booking["room_category"] = booking["room_type"].apply(simplify_room)

room_stats = (
    booking.groupby("room_category")
    .agg(
        median_price=("price_eur", "median"),
        mean_rating=("rating", "mean"),
        mean_room_score=("room_score", "mean"),
        count=("hotel_name", "count")
    )
    .reset_index()
    .sort_values("median_price", ascending=True)
)
room_stats = room_stats[room_stats["count"] >= 20]

fig, ax = plt.subplots(figsize=(12, 7))

colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(room_stats)))
bars = ax.barh(room_stats["room_category"], room_stats["median_price"],
               color=colors, alpha=0.85, height=0.6)

for bar, rs, count in zip(bars, room_stats["mean_room_score"], room_stats["count"]):
    label = f"Room score: {rs:.1f}  (n={count})" if not pd.isna(rs) else f"(n={count})"
    ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
            label, va="center", fontsize=9, color=SUBTLE)

ax.set_title("Median Price by Room Category")
ax.set_xlabel("Median Price per Night (EUR)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"EUR {v:,.0f}"))

plt.tight_layout()
plt.savefig("output/charts/05_room_type_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("5/6 Room type analysis saved")

# ============================================================
# 6. VALUE SCORE: Best Bang for Your Buck
# ============================================================
# Value = rating / price_eur * 100
booking_value = booking.dropna(subset=["rating", "price_eur"]).copy()
booking_value["value_score"] = (booking_value["rating"] / booking_value["price_eur"]) * 100

# Top 15 value hotels (min 50 reviews)
top_value = (
    booking_value[booking_value["num_reviews"] >= 50]
    .nlargest(15, "value_score")
)

fig, ax = plt.subplots(figsize=(12, 7))

labels = [f"{name}\n({loc})" for name, loc in zip(top_value["hotel_name"], top_value["location"])]
bars = ax.barh(range(len(top_value)), top_value["value_score"], color=ACCENT, alpha=0.8, height=0.6)
ax.set_yticks(range(len(top_value)))
ax.set_yticklabels(labels, fontsize=9)

for bar, price, rating in zip(bars, top_value["price_eur"], top_value["rating"]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"EUR {price:.0f} | Rating {rating}", va="center", fontsize=9, color=SUBTLE)

ax.set_title("Top 15 Best Value Hotels (Rating / Price, min. 50 reviews)")
ax.set_xlabel("Value Score (higher = better deal)")

plt.tight_layout()
plt.savefig("output/charts/06_best_value_hotels.png", dpi=150, bbox_inches="tight")
plt.close()
print("6/6 Best value hotels saved")

# ============================================================
# SUMMARY STATS
# ============================================================
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Booking hotels analyzed: {len(booking)}")
print(f"TripAdvisor hotels analyzed: {len(tripadvisor)}")
print(f"\nBooking - Median price: EUR {booking['price_eur'].median():.0f}")
print(f"Booking - Mean rating: {booking['rating'].mean():.1f}")
print(f"TripAdvisor - Median price: EUR {tripadvisor['price_eur'].median():.0f}")
print(f"\nLocations with 10+ hotels: {len(loc_stats)}")
print(f"Room categories (20+ hotels): {len(room_stats)}")
print("\nAll charts saved as PNG files.")
