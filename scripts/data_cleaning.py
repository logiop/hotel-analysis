import pandas as pd
import re
import os

# Set working directory to project root
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

# ============================================================
# 1. BOOKING HOTEL - CLEANING
# ============================================================

booking_raw = pd.read_csv("data/raw/booking_hotel.csv", encoding="latin1")

booking = booking_raw.copy()

# Rename columns
booking.columns = [
    "hotel_name", "location", "rating", "review_score",
    "num_reviews", "room_score", "room_type", "bed_type", "price_bdt"
]

# Clean price: remove non-numeric chars, convert to float
booking["price_bdt"] = (
    booking["price_bdt"]
    .astype(str)
    .str.replace(r"[^\d]", "", regex=True)
    .replace("", pd.NA)
    .astype(float)
)
booking["price_eur"] = (booking["price_bdt"] / 120).round(2)

# Clean rating
booking["rating"] = pd.to_numeric(booking["rating"], errors="coerce")

# Clean num_reviews
booking["num_reviews"] = (
    booking["num_reviews"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.strip()
)
booking["num_reviews"] = pd.to_numeric(booking["num_reviews"], errors="coerce").astype("Int64")

# Trim strings
for col in ["hotel_name", "location", "review_score", "room_type", "bed_type"]:
    booking[col] = booking[col].str.strip()

# Add source
booking["source"] = "Booking.com"

# Filter outliers and NAs
booking = booking.dropna(subset=["price_bdt", "rating"])
booking = booking[(booking["price_eur"] >= 5) & (booking["price_eur"] <= 10000)]

print("=== BOOKING CLEANED ===")
print(f"Rows: {len(booking)}")
print(f"Rating range: {booking['rating'].min()} - {booking['rating'].max()}")
print(f"Price EUR range: {booking['price_eur'].min()} - {booking['price_eur'].max()}")
print(f"NA room_score: {booking['room_score'].isna().sum()}")
print()

# ============================================================
# 2. TRIPADVISOR - CLEANING
# ============================================================

tripadvisor_raw = pd.read_csv("data/raw/tripadvisor_room.csv", encoding="latin1", on_bad_lines="skip")

tripadvisor = tripadvisor_raw.copy()

# Rename columns
tripadvisor.columns = ["hotel_name", "price_bdt", "num_reviews", "comment"]

# Remove numbering prefix (e.g. "1. Hotel Name" -> "Hotel Name")
tripadvisor["hotel_name"] = (
    tripadvisor["hotel_name"]
    .str.replace(r"^\d+\.\s*", "", regex=True)
    .str.strip()
)

# Clean price
tripadvisor["price_bdt"] = (
    pd.to_numeric(
        tripadvisor["price_bdt"]
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .replace("", pd.NA),
        errors="coerce"
    )
)
tripadvisor["price_eur"] = (tripadvisor["price_bdt"] / 120).round(2)

# Clean num_reviews
tripadvisor["num_reviews"] = (
    tripadvisor["num_reviews"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.strip()
)
tripadvisor["num_reviews"] = pd.to_numeric(tripadvisor["num_reviews"], errors="coerce").astype("Int64")

# Clean comment
tripadvisor["comment"] = tripadvisor["comment"].str.strip()

# Add source
tripadvisor["source"] = "TripAdvisor"

# Filter
tripadvisor = tripadvisor.dropna(subset=["price_bdt"])
tripadvisor = tripadvisor[(tripadvisor["price_eur"] >= 5) & (tripadvisor["price_eur"] <= 10000)]

print("=== TRIPADVISOR CLEANED ===")
print(f"Rows: {len(tripadvisor)}")
print(f"Price EUR range: {tripadvisor['price_eur'].min()} - {tripadvisor['price_eur'].max()}")
print(f"Empty comments: {(tripadvisor['comment'].isna() | (tripadvisor['comment'] == '')).sum()}")
print()

# ============================================================
# 3. SAVE CLEANED FILES
# ============================================================

booking.to_csv("data/cleaned/booking_cleaned.csv", index=False)
tripadvisor.to_csv("data/cleaned/tripadvisor_cleaned.csv", index=False)

print("=== FILES SAVED ===")
print(f"- booking_cleaned.csv ({len(booking)} rows)")
print(f"- tripadvisor_cleaned.csv ({len(tripadvisor)} rows)")
