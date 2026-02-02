import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from scipy import stats

pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 120)

booking = pd.read_csv("data/cleaned/booking_cleaned.csv")
tripadvisor = pd.read_csv("data/cleaned/tripadvisor_cleaned.csv")

print("=" * 70)
print("DEEP ANALYSIS - HOTEL DATASET")
print("=" * 70)

# ============================================================
# 1. CORRELATION: Price vs Rating
# ============================================================
print("\n\n--- 1. CORRELATION: PRICE vs RATING ---")
corr, pvalue = stats.pearsonr(booking["price_eur"], booking["rating"])
print(f"Pearson correlation: {corr:.4f} (p-value: {pvalue:.2e})")
spearman, sp_pvalue = stats.spearmanr(booking["price_eur"], booking["rating"])
print(f"Spearman correlation: {spearman:.4f} (p-value: {sp_pvalue:.2e})")

# By price bracket
booking["price_bracket"] = pd.cut(booking["price_eur"],
    bins=[0, 50, 100, 200, 500, 1000, 10000],
    labels=["<50", "50-100", "100-200", "200-500", "500-1000", "1000+"])

price_rating = (
    booking.groupby("price_bracket", observed=True)
    .agg(
        mean_rating=("rating", "mean"),
        median_rating=("rating", "median"),
        mean_room_score=("room_score", "mean"),
        count=("hotel_name", "count")
    )
)
print("\nRating by price bracket:")
print(price_rating.to_string())

# ============================================================
# 2. REVIEW SCORE vs ACTUAL RATING - Are labels accurate?
# ============================================================
print("\n\n--- 2. REVIEW LABELS vs ACTUAL RATINGS ---")
label_stats = (
    booking.groupby("review_score")
    .agg(
        mean_rating=("rating", "mean"),
        std_rating=("rating", "std"),
        min_rating=("rating", "min"),
        max_rating=("rating", "max"),
        median_price=("price_eur", "median"),
        count=("hotel_name", "count")
    )
    .sort_values("mean_rating", ascending=False)
)
print(label_stats[label_stats["count"] >= 10].to_string())

# ============================================================
# 3. ROOM SCORE vs OVERALL RATING - Gap analysis
# ============================================================
print("\n\n--- 3. ROOM SCORE vs OVERALL RATING (GAP) ---")
has_both = booking.dropna(subset=["room_score"])
has_both = has_both.copy()
has_both["gap"] = has_both["room_score"] - has_both["rating"]

print(f"Hotels with both scores: {len(has_both)}")
print(f"Mean gap (room - overall): {has_both['gap'].mean():.2f}")
print(f"Hotels where room > overall: {(has_both['gap'] > 0).sum()} ({(has_both['gap'] > 0).mean()*100:.1f}%)")
print(f"Hotels where room < overall: {(has_both['gap'] < 0).sum()} ({(has_both['gap'] < 0).mean()*100:.1f}%)")

# Biggest negative gaps (room much worse than overall)
print("\nBiggest negative gaps (room disappoints vs overall):")
worst_rooms = has_both.nsmallest(10, "gap")[["hotel_name", "location", "rating", "room_score", "gap", "price_eur"]]
print(worst_rooms.to_string(index=False))

# ============================================================
# 4. LOCATION DEEP DIVE - Price vs Quality
# ============================================================
print("\n\n--- 4. LOCATION: PRICE vs QUALITY ---")
loc_deep = (
    booking.groupby("location")
    .agg(
        median_price=("price_eur", "median"),
        mean_rating=("rating", "mean"),
        mean_room_score=("room_score", "mean"),
        count=("hotel_name", "count")
    )
    .reset_index()
)
loc_deep = loc_deep[loc_deep["count"] >= 10].copy()

# Value index: rating per EUR spent (normalized)
loc_deep["value_index"] = (loc_deep["mean_rating"] / loc_deep["median_price"]) * 100

print("\nBEST VALUE locations (high rating, low price):")
print(loc_deep.nlargest(10, "value_index")[["location", "median_price", "mean_rating", "value_index", "count"]].to_string(index=False))

print("\nWORST VALUE locations (low rating, high price):")
print(loc_deep.nsmallest(10, "value_index")[["location", "median_price", "mean_rating", "value_index", "count"]].to_string(index=False))

# ============================================================
# 5. OVERPRICED vs UNDERPRICED hotels
# ============================================================
print("\n\n--- 5. OVERPRICED vs UNDERPRICED HOTELS ---")
# Fit a simple linear model: expected_rating = f(price)
from numpy.polynomial import polynomial as P

mask = booking["price_eur"] < 5000
x = booking.loc[mask, "price_eur"].values
y = booking.loc[mask, "rating"].values

coeffs = np.polyfit(x, y, 1)
booking_fit = booking[mask].copy()
booking_fit["expected_rating"] = np.polyval(coeffs, booking_fit["price_eur"])
booking_fit["rating_residual"] = booking_fit["rating"] - booking_fit["expected_rating"]

print(f"Linear model: Rating = {coeffs[0]:.6f} * Price + {coeffs[1]:.2f}")

print("\nMost OVERPRICED (low rating for price, min 50 reviews):")
overpriced = booking_fit[booking_fit["num_reviews"] >= 50].nsmallest(10, "rating_residual")
print(overpriced[["hotel_name", "location", "price_eur", "rating", "expected_rating", "rating_residual", "num_reviews"]].to_string(index=False))

print("\nMost UNDERPRICED / best surprises (high rating for price, min 50 reviews):")
underpriced = booking_fit[booking_fit["num_reviews"] >= 50].nlargest(10, "rating_residual")
print(underpriced[["hotel_name", "location", "price_eur", "rating", "expected_rating", "rating_residual", "num_reviews"]].to_string(index=False))

# ============================================================
# 6. BED TYPE impact on price and rating
# ============================================================
print("\n\n--- 6. BED TYPE IMPACT ---")
bed_stats = (
    booking.groupby("bed_type")
    .agg(
        median_price=("price_eur", "median"),
        mean_rating=("rating", "mean"),
        count=("hotel_name", "count")
    )
    .reset_index()
    .sort_values("median_price", ascending=False)
)
print(bed_stats[bed_stats["count"] >= 30].to_string(index=False))

# ============================================================
# 7. NUMBER OF REVIEWS vs RATING - popularity bias?
# ============================================================
print("\n\n--- 7. POPULARITY BIAS: REVIEWS vs RATING ---")
booking["review_bracket"] = pd.cut(booking["num_reviews"],
    bins=[0, 50, 200, 500, 1000, 5000, 100000],
    labels=["<50", "50-200", "200-500", "500-1k", "1k-5k", "5k+"])

rev_rating = (
    booking.groupby("review_bracket", observed=True)
    .agg(
        mean_rating=("rating", "mean"),
        median_price=("price_eur", "median"),
        count=("hotel_name", "count")
    )
)
print(rev_rating.to_string())

corr_rev, p_rev = stats.spearmanr(
    booking["num_reviews"].dropna(),
    booking.loc[booking["num_reviews"].notna(), "rating"]
)
print(f"\nSpearman corr (num_reviews vs rating): {corr_rev:.4f} (p={p_rev:.2e})")

# ============================================================
# 8. TRIPADVISOR: Comment length vs price
# ============================================================
print("\n\n--- 8. TRIPADVISOR: COMMENT LENGTH ANALYSIS ---")
ta = tripadvisor.dropna(subset=["comment"]).copy()
ta["comment_len"] = ta["comment"].str.len()
ta["comment_words"] = ta["comment"].str.split().str.len()

ta["price_bracket"] = pd.cut(ta["price_eur"],
    bins=[0, 30, 60, 100, 200, 10000],
    labels=["<30", "30-60", "60-100", "100-200", "200+"])

comment_price = (
    ta.groupby("price_bracket", observed=True)
    .agg(
        mean_words=("comment_words", "mean"),
        median_price=("price_eur", "median"),
        count=("hotel_name", "count")
    )
)
print(comment_price.to_string())

corr_c, p_c = stats.spearmanr(ta["price_eur"], ta["comment_words"])
print(f"\nSpearman corr (price vs comment length): {corr_c:.4f} (p={p_c:.2e})")

# ============================================================
# FINAL KEY FINDINGS
# ============================================================
print("\n\n" + "=" * 70)
print("KEY FINDINGS")
print("=" * 70)
print(f"""
1. PRICE-RATING CORRELATION: Weak positive (Spearman={spearman:.3f}).
   Paying more does NOT guarantee a significantly better experience.

2. ROOM SCORE GAP: {(has_both['gap'] > 0).mean()*100:.0f}% of hotels have room scores
   HIGHER than their overall rating. Rooms are generally the strongest point.

3. BEST VALUE LOCATIONS: Budget-friendly areas deliver ratings nearly as
   high as premium destinations.

4. OVERPRICED HOTELS EXIST: Some expensive hotels consistently underperform
   relative to their price point (see residual analysis).

5. POPULARITY BIAS: Hotels with more reviews tend to have slightly higher
   ratings (Spearman={corr_rev:.3f}), suggesting a survivorship/visibility effect.

6. REVIEW LENGTH: Guests at cheaper hotels write {'longer' if corr_c < 0 else 'shorter'}
   comments (corr={corr_c:.3f}), possibly because they have more to report.
""")
