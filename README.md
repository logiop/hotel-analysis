# What 5,500 Hotels Teach Us About Value for Money

A data-driven analysis of **Booking.com** and **TripAdvisor** hotel data, exploring the relationship between price, ratings, and guest behavior.

## Key Findings

| # | Finding | Key Metric |
|---|---------|------------|
| 1 | **Price is a poor predictor of quality** | Only +0.28 rating difference across a 10x price range |
| 2 | **Rooms are the strongest asset** | 88% of hotels score higher on rooms than overall |
| 3 | **Paris is the worst value destination** | 6 of 10 worst value locations are Parisian arrondissements |
| 4 | **Overpriced hotels are identifiable** | Residual analysis reveals consistent underperformers |
| 5 | **Budget guests leave richer feedback** | 2x longer reviews at cheap hotels (Spearman r = -0.43) |

## Charts

### Price vs Rating
![Price vs Rating](output/charts/finding_01_price_vs_rating.png)

### Room Score Gap
![Room Score Gap](output/charts/finding_02_room_score_gap.png)

### Best vs Worst Value Destinations
![Best vs Worst Value](output/charts/finding_03_best_worst_value.png)

### Overpriced Hotels
![Overpriced Hotels](output/charts/finding_04_overpriced_hotels.png)

### Review Length by Price
![Review Length](output/charts/finding_06_review_length.png)

## Project Structure

```
HotelAnalysis/
├── hotel_analysis.ipynb       # Full analysis notebook (start here)
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                   # Original datasets
│   │   ├── booking_hotel.csv
│   │   └── tripadvisor_room.csv
│   └── cleaned/               # Cleaned datasets
│       ├── booking_cleaned.csv
│       └── tripadvisor_cleaned.csv
├── scripts/                   # Standalone Python scripts
│   ├── data_cleaning.py
│   ├── analysis.py
│   ├── deep_analysis.py
│   ├── findings_charts.py
│   └── presentation.py
├── output/
│   ├── charts/                # All generated charts (PNG)
│   └── presentation/          # PDF presentation
└── docs/
    └── analysis_report.md     # Detailed written report
```

## How to Run

```bash
# Clone the repo
git clone https://github.com/logiop/hotel-analysis.git
cd hotel-analysis

# Install dependencies
pip install -r requirements.txt

# Option 1: Open the Jupyter Notebook (recommended)
jupyter notebook hotel_analysis.ipynb

# Option 2: Run scripts individually
python scripts/data_cleaning.py
python scripts/findings_charts.py
python scripts/presentation.py
```

## Dataset

**Source:** [Hotel Dataset: Rates, Reviews & Amenities (6k+)](https://www.kaggle.com/datasets/joyshil0599/hotel-dataset-rates-reviews-and-amenities5k) — Kaggle, CC0 License

- **Booking.com:** 3,465 hotels (3,290 after cleaning) — ratings, room scores, room types, prices
- **TripAdvisor:** 5,330 hotels (2,248 after cleaning) — prices, review counts, guest comments

**Note:** Prices were in BDT and converted to EUR at approximately 120:1. The two datasets cover different market segments (Booking skews luxury, TripAdvisor skews budget).

## Tools

- Python (pandas, numpy, scipy, matplotlib)
- Jupyter Notebook

## Author

**Giorgio Vernarecci** — Data Analyst

Former hospitality professional with 6 years of experience, now applying data analytics to the industry I know from the inside.

- [LinkedIn](https://www.linkedin.com/in/giorgio-vernarecci-4b5a8a23b)
- [GitHub](https://github.com/logiop)
