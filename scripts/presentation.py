import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib import gridspec

# ============================================================
# SETUP
# ============================================================
BG = "#0A1628"
ACCENT = "#00D4AA"
RED = "#FF6B6B"
YELLOW = "#F1C40F"
SUBTLE = "#8899AA"
WHITE = "#FFFFFF"
CARD = "#132039"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "axes.edgecolor": "#1a2d4a",
    "axes.labelcolor": SUBTLE,
    "xtick.color": SUBTLE,
    "ytick.color": SUBTLE,
    "text.color": WHITE,
    "font.size": 12,
})

booking = pd.read_csv("data/cleaned/booking_cleaned.csv")
tripadvisor = pd.read_csv("data/cleaned/tripadvisor_cleaned.csv")

# Precompute stats
has_both = booking.dropna(subset=["room_score"]).copy()
has_both["gap"] = has_both["room_score"] - has_both["rating"]
room_higher_pct = (has_both["gap"] > 0).mean() * 100

from matplotlib.backends.backend_pdf import PdfPages

pdf = PdfPages("output/presentation/hotel_presentation.pdf")
W, H = 13, 9

# ============================================================
# SLIDE 1: COVER
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.62, "What 5,500 Hotels\nTeach Us About\nValue for Money",
         ha="center", va="center", fontsize=46, fontweight="bold", color=WHITE,
         linespacing=1.3)
fig.text(0.5, 0.35, "A data-driven analysis of Booking.com & TripAdvisor",
         ha="center", fontsize=20, color=ACCENT, style="italic")
fig.text(0.5, 0.18, "3,290 Booking.com hotels  |  2,248 TripAdvisor hotels  |  Real data",
         ha="center", fontsize=14, color=SUBTLE)
fig.text(0.5, 0.08, "Giorgio Vernarecci  -  Data Analyst",
         ha="center", fontsize=14, color=SUBTLE)
pdf.savefig(fig)
plt.close()
print("Slide 1/10 - Cover")

# ============================================================
# SLIDE 2: THE QUESTION
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.65, "The Question",
         ha="center", fontsize=38, fontweight="bold", color=ACCENT)
fig.text(0.5, 0.45,
         "Does paying more for a hotel\nactually get you a better experience?",
         ha="center", fontsize=28, color=WHITE, linespacing=1.4)
fig.text(0.5, 0.22,
         "I analyzed 5,500+ hotels across Booking.com and TripAdvisor\n"
         "to find out what really drives guest satisfaction\n"
         "and where travelers get the best (and worst) value.",
         ha="center", fontsize=16, color=SUBTLE, linespacing=1.5)
pdf.savefig(fig)
plt.close()
print("Slide 2/10 - Question")

# ============================================================
# SLIDE 3: KEY NUMBER
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.78, "The Short Answer", ha="center", fontsize=20, color=SUBTLE)
fig.text(0.5, 0.55, "+0.28", ha="center", fontsize=130, fontweight="bold", color=RED)
fig.text(0.5, 0.30,
         "That's the rating difference between\na EUR 500/night hotel and a EUR 5,000/night hotel",
         ha="center", fontsize=22, color=WHITE, linespacing=1.4)
fig.text(0.5, 0.12, "Spearman correlation: r = 0.19 (weak positive)",
         ha="center", fontsize=14, color=SUBTLE)
pdf.savefig(fig)
plt.close()
print("Slide 3/10 - Key Number")

# ============================================================
# SLIDE 4: CHART - Price vs Rating
# ============================================================
booking["price_bracket"] = pd.cut(booking["price_eur"],
    bins=[0, 500, 1000, 2000, 5000, 10000],
    labels=["<500", "500-1k", "1k-2k", "2k-5k", "5k+"])

pb = (booking.groupby("price_bracket", observed=True)
      .agg(mean_rating=("rating", "mean"), count=("hotel_name", "count"))
      .reset_index())

fig, ax = plt.subplots(figsize=(W, H))
colors = [RED if r < 8.1 else YELLOW if r < 8.25 else ACCENT for r in pb["mean_rating"]]
bars = ax.bar(pb["price_bracket"].astype(str), pb["mean_rating"], color=colors, alpha=0.85, width=0.55)
for bar, rating, count in zip(bars, pb["mean_rating"], pb["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
            f"{rating:.2f}", ha="center", fontsize=16, fontweight="bold", color=WHITE)
    ax.text(bar.get_x() + bar.get_width()/2, 7.55,
            f"n={count}", ha="center", fontsize=10, color=SUBTLE)
ax.set_ylim(7.5, 8.7)
ax.set_title("Paying More Does NOT Guarantee a Better Experience",
             fontsize=20, fontweight="bold", pad=20)
ax.set_xlabel("Price per Night (EUR)", fontsize=14)
ax.set_ylabel("Average Rating", fontsize=14)
ax.text(0.5, 0.92, "Only +0.28 rating difference across a 10x price increase",
        transform=ax.transAxes, ha="center", fontsize=14, color=RED,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=CARD, edgecolor=RED, alpha=0.9))
plt.tight_layout()
pdf.savefig(fig)
plt.close()
print("Slide 4/10 - Price vs Rating")

# ============================================================
# SLIDE 5: CHART - Room Score Gap
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W, H), gridspec_kw={"width_ratios": [1, 1.4]})

room_higher = (has_both["gap"] > 0).sum()
room_equal = (has_both["gap"] == 0).sum()
room_lower = (has_both["gap"] < 0).sum()

sizes = [room_higher, room_equal, room_lower]
pie_colors = [ACCENT, YELLOW, RED]
wedges, texts, _ = ax1.pie(sizes, colors=pie_colors, startangle=90, autopct="",
                            textprops={"color": WHITE, "fontsize": 11},
                            pctdistance=0.75, labeldistance=1.15)
labels_pie = [
    f"Room > Overall\n{room_higher} ({room_higher/len(has_both)*100:.0f}%)",
    f"Equal\n{room_equal} ({room_equal/len(has_both)*100:.0f}%)",
    f"Room < Overall\n{room_lower} ({room_lower/len(has_both)*100:.0f}%)"
]
for text, label in zip(texts, labels_pie):
    text.set_text(label)
    text.set_fontsize(11)
ax1.set_title("Room Score vs Overall Rating", fontsize=16, fontweight="bold", pad=15)

ax2.hist(has_both["gap"], bins=40, color=ACCENT, alpha=0.8, edgecolor="none")
ax2.axvline(0, color=RED, linestyle="--", linewidth=2, label="No gap (0)")
ax2.axvline(has_both["gap"].mean(), color=YELLOW, linestyle="--", linewidth=2,
            label=f"Mean gap: +{has_both['gap'].mean():.2f}")
ax2.set_title("88% of Hotels: Room Is the Strongest Point",
              fontsize=16, fontweight="bold", pad=15)
ax2.set_xlabel("Gap (Room Score - Overall Rating)")
ax2.set_ylabel("Number of Hotels")
ax2.legend(facecolor=CARD, edgecolor="#1a2d4a", fontsize=11)
plt.tight_layout()
pdf.savefig(fig)
plt.close()
print("Slide 5/10 - Room Score Gap")

# ============================================================
# SLIDE 6: CHART - Best vs Worst Value
# ============================================================
loc_stats = (booking.groupby("location")
    .agg(median_price=("price_eur", "median"), mean_rating=("rating", "mean"),
         count=("hotel_name", "count"))
    .reset_index())
loc_stats = loc_stats[loc_stats["count"] >= 10].copy()
loc_stats["value_index"] = (loc_stats["mean_rating"] / loc_stats["median_price"]) * 100

best10 = loc_stats.nlargest(10, "value_index")
worst10 = loc_stats.nsmallest(10, "value_index")

fig, (ax_w, ax_b) = plt.subplots(1, 2, figsize=(W, H))

worst_s = worst10.sort_values("value_index", ascending=True)
bars_w = ax_w.barh(worst_s["location"], worst_s["median_price"], color=RED, alpha=0.85, height=0.6)
for bar, rating in zip(bars_w, worst_s["mean_rating"]):
    ax_w.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
              f"{rating:.1f}", va="center", fontsize=11, color=YELLOW, fontweight="bold")
ax_w.set_title("WORST Value", fontsize=16, fontweight="bold", pad=15, color=RED)
ax_w.set_xlabel("Median Price (EUR)")
ax_w.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax_w.text(1.0, 1.02, "Rating", transform=ax_w.transAxes, ha="right",
          fontsize=10, color=YELLOW, fontweight="bold")

best_s = best10.sort_values("value_index", ascending=True)
bars_b = ax_b.barh(best_s["location"], best_s["median_price"], color=ACCENT, alpha=0.85, height=0.6)
for bar, rating in zip(bars_b, best_s["mean_rating"]):
    ax_b.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
              f"{rating:.1f}", va="center", fontsize=11, color=YELLOW, fontweight="bold")
ax_b.set_title("BEST Value", fontsize=16, fontweight="bold", pad=15, color=ACCENT)
ax_b.set_xlabel("Median Price (EUR)")
ax_b.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax_b.text(1.0, 1.02, "Rating", transform=ax_b.transAxes, ha="right",
          fontsize=10, color=YELLOW, fontweight="bold")

fig.suptitle("Paris vs Thailand: Where Does Your Money Go?",
             fontsize=22, fontweight="bold", color=WHITE, y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
pdf.savefig(fig)
plt.close()
print("Slide 6/10 - Best vs Worst Value")

# ============================================================
# SLIDE 7: CHART - Overpriced Hotels
# ============================================================
mask = booking["price_eur"] < 5000
coeffs = np.polyfit(booking.loc[mask, "price_eur"], booking.loc[mask, "rating"], 1)
bf = booking[mask].copy()
bf["expected"] = np.polyval(coeffs, bf["price_eur"])
bf["residual"] = bf["rating"] - bf["expected"]
overpriced = bf[bf["num_reviews"] >= 50].nsmallest(7, "residual")

fig, ax = plt.subplots(figsize=(W, H))
ax.scatter(bf["price_eur"], bf["rating"], alpha=0.12, s=12, color=SUBTLE)
x_line = np.linspace(0, 5000, 100)
ax.plot(x_line, np.polyval(coeffs, x_line), color=YELLOW, linewidth=2, linestyle="--",
        label="Expected rating")
ax.scatter(overpriced["price_eur"], overpriced["rating"], color=RED, s=100, zorder=5,
           edgecolors=WHITE, linewidth=0.8, label="Most overpriced")

offsets = [(250, 0.6), (-400, 0.8), (250, -0.8), (-400, -0.5),
           (300, 0.5), (-350, -0.7), (200, 0.4)]
for i, (_, row) in enumerate(overpriced.iterrows()):
    name = row["hotel_name"][:22]
    ox, oy = offsets[i % len(offsets)]
    ax.annotate(f"{name}\n{row['location']}\nRating: {row['rating']}",
                xy=(row["price_eur"], row["rating"]),
                xytext=(row["price_eur"] + ox, row["rating"] + oy),
                fontsize=8, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD, edgecolor=RED, alpha=0.85))

ax.set_title("Overpriced: High Price, Low Rating", fontsize=20, fontweight="bold", pad=20)
ax.set_xlabel("Price per Night (EUR)", fontsize=14)
ax.set_ylabel("Rating", fontsize=14)
ax.set_xlim(0, 5000)
ax.set_ylim(1, 10.5)
ax.legend(facecolor=CARD, edgecolor="#1a2d4a", fontsize=11, loc="lower right")
plt.tight_layout()
pdf.savefig(fig)
plt.close()
print("Slide 7/10 - Overpriced Hotels")

# ============================================================
# SLIDE 8: CHART - Review Length
# ============================================================
ta = tripadvisor.dropna(subset=["comment"]).copy()
ta["comment_words"] = ta["comment"].str.split().str.len()
ta["price_bracket"] = pd.cut(ta["price_eur"],
    bins=[0, 30, 60, 100, 200, 10000],
    labels=["<30", "30-60", "60-100", "100-200", "200+"])
cp = (ta.groupby("price_bracket", observed=True)
      .agg(mean_words=("comment_words", "mean"), count=("hotel_name", "count"))
      .reset_index())

fig, ax = plt.subplots(figsize=(W, H))
colors_g = [ACCENT, "#2ECC71", YELLOW, "#E67E22", RED]
bars = ax.bar(cp["price_bracket"].astype(str), cp["mean_words"],
              color=colors_g, alpha=0.85, width=0.55)
for bar, words, count in zip(bars, cp["mean_words"], cp["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            f"{words:.0f} words", ha="center", fontsize=15, fontweight="bold", color=WHITE)
    ax.text(bar.get_x() + bar.get_width()/2, 1.5,
            f"n={count}", ha="center", fontsize=10, color=SUBTLE)
ax.set_title("Cheaper Hotels Get Longer Reviews", fontsize=20, fontweight="bold", pad=20)
ax.set_xlabel("Price per Night (EUR)", fontsize=14)
ax.set_ylabel("Average Words per Review", fontsize=14)
ax.set_ylim(0, 35)
ax.text(0.5, 0.92,
        "Budget guests write 2x more words than luxury guests  |  Spearman r = -0.43",
        transform=ax.transAxes, ha="center", fontsize=13, color=RED,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=CARD, edgecolor=RED, alpha=0.9))
plt.tight_layout()
pdf.savefig(fig)
plt.close()
print("Slide 8/10 - Review Length")

# ============================================================
# SLIDE 9: KEY TAKEAWAYS
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.88, "Key Takeaways", ha="center", fontsize=36, fontweight="bold", color=ACCENT)

takeaways = [
    ("1.", "Price is a poor predictor of quality", "+0.28 rating difference across 10x price range"),
    ("2.", "Rooms are the strongest asset", "88% of hotels score higher on rooms than overall"),
    ("3.", "Paris is the worst value destination", "6 of the 10 worst value locations are in Paris"),
    ("4.", "Overpriced hotels are identifiable", "Residual analysis reveals consistent underperformers"),
    ("5.", "Budget guests leave richer feedback", "2x longer reviews at cheap hotels (r = -0.43)"),
]

for i, (num, title, detail) in enumerate(takeaways):
    y = 0.72 - i * 0.13
    fig.text(0.08, y, num, fontsize=22, fontweight="bold", color=ACCENT)
    fig.text(0.14, y, title, fontsize=20, fontweight="bold", color=WHITE)
    fig.text(0.14, y - 0.04, detail, fontsize=14, color=SUBTLE)

pdf.savefig(fig)
plt.close()
print("Slide 9/12 - Key Takeaways")

# ============================================================
# SLIDE 10: METHODOLOGY
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.88, "Methodology", ha="center", fontsize=36, fontweight="bold", color=ACCENT)

methods = [
    ("Data Source", "Kaggle - Hotel Dataset: Rates, Reviews & Amenities (6k+)\nby joyshil0599 - CC0 License"),
    ("Datasets", "Booking.com (3,465 rows) + TripAdvisor (5,330 rows)"),
    ("Cleaning", "Encoding fixes, currency conversion (BDT to EUR at 1:120),\noutlier removal, string normalization, duplicate handling"),
    ("After Cleaning", "Booking: 3,290 hotels  |  TripAdvisor: 2,248 hotels"),
    ("Analysis", "Pearson & Spearman correlations, linear regression\nfor residual analysis, descriptive statistics"),
    ("Tools", "Python (pandas, numpy, scipy, matplotlib)"),
]

for i, (label, desc) in enumerate(methods):
    y = 0.74 - i * 0.11
    fig.text(0.08, y, label, fontsize=16, fontweight="bold", color=ACCENT)
    fig.text(0.30, y, desc, fontsize=14, color=WHITE, linespacing=1.3)

fig.text(0.5, 0.08,
         "Note: BDT/EUR conversion rate is approximate. The two datasets cover\n"
         "different market segments and are analyzed separately where appropriate.",
         ha="center", fontsize=12, color=SUBTLE, linespacing=1.4)

pdf.savefig(fig)
plt.close()
print("Slide 10/12 - Methodology")

# ============================================================
# SLIDE 11: ABOUT / CTA
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.70, "Giorgio Vernarecci",
         ha="center", fontsize=40, fontweight="bold", color=WHITE)
fig.text(0.5, 0.60, "Data Analyst",
         ha="center", fontsize=26, color=ACCENT)
fig.text(0.5, 0.48,
         "SQL  |  Python  |  R  |  Tableau  |  n8n",
         ha="center", fontsize=18, color=SUBTLE)
fig.text(0.5, 0.34,
         "Former hospitality professional turned data analyst.\n"
         "I combine operational experience with analytics\n"
         "to find insights others miss.",
         ha="center", fontsize=18, color=WHITE, linespacing=1.5)
fig.text(0.5, 0.15,
         "Let's connect - follow me for more data stories.",
         ha="center", fontsize=16, color=ACCENT, style="italic")
fig.text(0.5, 0.06,
         "github.com/logiop  |  Built with Python",
         ha="center", fontsize=12, color=SUBTLE)
pdf.savefig(fig)
plt.close()
print("Slide 11/12 - About")

# ============================================================
# SLIDE 12: SOURCES
# ============================================================
fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor(BG)
fig.text(0.5, 0.80, "Sources & Links", ha="center", fontsize=32, fontweight="bold", color=ACCENT)

sources = [
    "Dataset: kaggle.com/datasets/joyshil0599/hotel-dataset-rates-reviews-and-amenities5k",
    "GitHub:  github.com/logiop",
    "LinkedIn: linkedin.com/in/giorgio-vernarecci-4b5a8a23b",
]
for i, s in enumerate(sources):
    fig.text(0.12, 0.60 - i * 0.10, s, fontsize=16, color=WHITE)

fig.text(0.5, 0.20, "Thank you for reading.",
         ha="center", fontsize=22, color=SUBTLE, style="italic")

pdf.savefig(fig)
plt.close()
print("Slide 12/12 - Sources")

pdf.close()
print("\nPresentation saved: hotel_presentation.pdf")
