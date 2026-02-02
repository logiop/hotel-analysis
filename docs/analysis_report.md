# Hotel Data Analysis Report
### Booking.com & TripAdvisor — 5,500+ Hotels

---

## Dataset Overview

This analysis covers two datasets:
- **Booking.com**: 3,290 hotels with ratings, room scores, room types, bed types and prices
- **TripAdvisor**: 2,248 hotels with prices, review counts and guest comments

Prices were originally in BDT (Bangladeshi Taka) and converted to EUR at a rate of 120 BDT = 1 EUR.

---

## Finding 1 — Paying More Does NOT Guarantee a Better Experience

**Chart: `finding_01_price_vs_rating.png`**

This bar chart compares the average guest rating across five price brackets, from under EUR 500 to over EUR 5,000 per night.

**What the data shows:**
- The cheapest bracket (<500 EUR) has an average rating of 7.96
- The most expensive bracket (5k+) has an average rating of 8.35
- The total difference is only **+0.28 points** across a 10x price increase

**Why it matters:**
A guest paying EUR 5,000 per night gets an experience rated only 0.28 points higher than someone paying EUR 500. The correlation between price and rating is statistically weak (Spearman r = 0.19). This suggests that price is largely driven by location and brand, not by actual guest satisfaction.

---

## Finding 2 — Rooms Are the Strongest Point for 88% of Hotels

**Chart: `finding_02_room_score_gap.png`**

The left panel is a pie chart showing the proportion of hotels where the room score is higher, equal to, or lower than the overall rating. The right panel shows the distribution of the gap (room score minus overall rating).

**What the data shows:**
- **88% of hotels** have a room score higher than their overall rating
- Only 7% have rooms scoring lower than the overall rating
- The average gap is +0.30 points in favor of the room

**Why it matters:**
Rooms are consistently the strongest aspect of a hotel stay. What drags overall ratings down is typically service, cleanliness, location convenience, or value for money. For hotel operators, this means investing in staff training, service quality and non-room amenities would likely have the biggest impact on improving overall ratings.

---

## Finding 3 — Paris Is the Worst Value Destination; Thailand Dominates Best Value

**Chart: `finding_03_best_worst_value.png`**

This side-by-side chart compares the 10 worst value and 10 best value destinations, measured by a Value Index (rating divided by median price). Only locations with at least 10 hotels are included.

**What the data shows:**

*Worst Value (left, red):*
- 6 out of 10 worst value destinations are Paris arrondissements
- 8th arr. Paris: median price EUR 5,960, rating 7.4
- 3rd arr. Paris: median price EUR 5,116, rating 6.5
- Singapore (Orchard, Novena) also appears in the worst value list

*Best Value (right, green):*
- Thailand dominates: Udon Thani, Chiang Mai, Pattaya, Phuket, Ao Nang Beach
- Udon Thani: median price EUR 549, rating 8.3
- Best value locations deliver ratings of 7.6–8.6 at a fraction of the price

**Why it matters:**
Paris hotels charge premium prices but consistently underdeliver on guest satisfaction. A traveler can get a significantly better-rated experience in Thailand at 1/10th of the price. This doesn't mean Paris hotels are bad — it means expectations are higher and harder to meet at premium price points.

---

## Finding 4 — Overpriced Hotels Identified Through Residual Analysis

**Chart: `finding_04_overpriced_hotels.png`**

This scatter plot shows all hotels by price (x-axis) and rating (y-axis). The yellow dashed line represents the expected rating based on price (linear trend). Red dots highlight hotels that fall significantly below the expected rating for their price point.

**What the data shows:**
- **Modern's Hotel** (12th arr., Paris): EUR 2,523/night, rating 3.2 (expected: 8.2) — 1,101 reviews
- **Hotel Montana La Fayette** (10th arr., Paris): EUR 2,959/night, rating 3.4 — 503 reviews
- **Hotel Novex Paris** (13th arr., Paris): EUR 2,309/night, rating 4.6 — 903 reviews
- Several Singapore hotels (Geylang district) also appear as overpriced

**Methodology:**
A linear regression model was fitted (Rating = 0.00007 × Price + 8.06). Hotels with the largest negative residuals (actual rating far below expected) and at least 50 reviews were flagged as overpriced. The high review counts confirm these are not anomalies — they reflect consistent guest dissatisfaction.

**Why it matters:**
These hotels charge premium prices while delivering well below average experiences. For travelers, checking actual ratings rather than relying on price as a quality indicator is essential.

---

## Finding 5 — More Popular Hotels Tend to Be More Expensive, Not Better Rated

**Chart: `finding_05_popularity_bias.png`**

This dual-axis chart shows mean rating (green bars) and median price (red line) grouped by the number of reviews each hotel has received.

**What the data shows:**
- Hotels with fewer than 50 reviews: mean rating 8.08, median price EUR 1,645
- Hotels with 5,000+ reviews: mean rating 8.37, median price EUR 2,293
- The rating difference across all review brackets is minimal (~0.3 points)
- Price increases consistently with review count

**Why it matters:**
Hotels with more reviews tend to be more expensive, which means they are in popular (and pricey) locations. The slight rating advantage of popular hotels is likely driven by survivorship bias — poorly rated hotels in expensive areas lose business and eventually close or rebrand. The Spearman correlation between review count and rating is weak (r = -0.07), confirming that popularity does not equal quality.

---

## Finding 6 — Guests at Cheaper Hotels Write Significantly Longer Reviews

**Chart: `finding_06_review_length.png`**

This bar chart shows the average number of words per TripAdvisor review, grouped by hotel price bracket.

**What the data shows:**
- Hotels under EUR 30/night: average **27 words** per review
- Hotels over EUR 200/night: average **12 words** per review
- Budget guests write **2.25x more words** than luxury guests
- The correlation is strong and statistically significant (Spearman r = -0.43, p < 0.001)

**Possible explanations:**
1. **More to report**: Budget hotels have more variance in quality, so guests feel the need to describe their experience in detail (both good and bad)
2. **Higher expectations met**: Luxury hotel guests receive what they expected, leading to shorter, confirmatory reviews ("Everything was perfect")
3. **Different guest profiles**: Budget travelers may be more engaged in the review community, sharing detailed information to help other budget-conscious travelers

**Why it matters:**
For hotel operators, longer reviews from budget guests represent a rich source of actionable feedback. For data analysts, this finding highlights that review length is not random — it correlates with price and can be used as a feature in sentiment analysis models.

---

## Tools & Methodology

- **Language**: Python (pandas, numpy, scipy, matplotlib)
- **Statistical tests**: Pearson and Spearman correlations, linear regression for residual analysis
- **Data cleaning**: Encoding fixes, currency conversion, outlier removal, string normalization
- **Visualization**: Custom dark theme, consistent color palette across all charts

---

*Analysis by Giorgio Vernarecci — Data Analyst*
