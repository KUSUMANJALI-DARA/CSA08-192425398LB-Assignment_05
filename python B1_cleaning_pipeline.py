
import csv
import sqlite3
import os
from statistics import median
from datetime import datetime

CSV_FILE = "air_quality.csv"
DB_FILE = "air_quality.db"

# Step 1: Create sample CSV data if the file does not exist
if not os.path.exists(CSV_FILE):
    sample_data = [
        ["S01", "Central", "2026-11-01", "09:00", "45", "80", "22", "30", "C"],
        ["S01", "Central", "2026-11-01", "10:00", "50", "85", "24", "31", "C"],
        ["S02", "North", "2026-11-01", "09:00", "60", "100", "30", "86", "F"],
        ["S02", "North", "2026-11-01", "10:00", "", "95", "28", "87", "F"],
        ["S03", "South", "2026-11-01", "09:00", "-5", "70", "18", "29", "C"],
        ["S03", "South", "2026-11-01", "10:00", "35", "75", "20", "30", "C"],
        ["S01", "Central", "2026-11-01", "09:00", "45", "80", "22", "30", "C"]
    ]

    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "station_id", "station_name", "date", "time",
            "pm25", "pm10", "no2", "temperature", "unit"
        ])
        writer.writerows(sample_data)

# Step 2: Read CSV data
with open(CSV_FILE, "r", newline="") as file:
    reader = csv.DictReader(file)
    records = list(reader)

print("Original records:", len(records))

# Step 3: Remove duplicate records
unique_records = []
seen = set()

for row in records:
    key = (row["station_id"], row["date"], row["time"])
    if key not in seen:
        seen.add(key)
        unique_records.append(row)

print("Duplicate records removed:", len(records) - len(unique_records))

# Step 4: Validate and convert pollutant values
pollutants = ["pm25", "pm10", "no2"]

for row in unique_records:
    for column in pollutants:
        try:
            value = float(row[column])
            if value < 0:
                row[column] = None
            else:
                row[column] = value
        except (ValueError, TypeError):
            row[column] = None

# Step 5: Replace missing values with median
for column in pollutants:
    valid_values = [
        row[column] for row in unique_records
        if row[column] is not None
    ]

    replacement = median(valid_values) if valid_values else 0

    for row in unique_records:
        if row[column] is None:
            row[column] = replacement

# Step 6: Standardise names, dates and temperature
for row in unique_records:
    row["station_name"] = row["station_name"].strip().title()

    row["date"] = datetime.strptime(
        row["date"], "%Y-%m-%d"
    ).strftime("%Y-%m-%d")

    temperature = float(row["temperature"])

    if row["unit"].upper() == "F":
        temperature = (temperature - 32) * 5 / 9

    row["temperature"] = round(temperature, 2)

# Step 7: Min-Max normalisation of PM2.5
pm25_values = [row["pm25"] for row in unique_records]

minimum = min(pm25_values)
maximum = max(pm25_values)

for row in unique_records:
    if maximum != minimum:
        row["pm25_normalised"] = round(
            (row["pm25"] - minimum) / (maximum - minimum), 3
        )
    else:
        row["pm25_normalised"] = 0

# Step 8: Create SQLite database and table
connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS air_quality (
    station_id TEXT,
    station_name TEXT,
    reading_date TEXT,
    reading_time TEXT,
    pm25 REAL,
    pm10 REAL,
    no2 REAL,
    temperature_c REAL,
    pm25_normalised REAL,
    UNIQUE(station_id, reading_date, reading_time)
)
""")

# Step 9: Store cleaned records
cursor.execute("DELETE FROM air_quality")

for row in unique_records:
    cursor.execute("""
    INSERT INTO air_quality VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["station_id"],
        row["station_name"],
        row["date"],
        row["time"],
        row["pm25"],
        row["pm10"],
        row["no2"],
        row["temperature"],
        row["pm25_normalised"]
    ))

connection.commit()

# Step 10: Display stored records
print("\nCLEANED AIR QUALITY DATA")
cursor.execute("SELECT * FROM air_quality")

for record in cursor.fetchall():
    print(record)

print("\nTotal cleaned records:", len(unique_records))
print("Database created successfully:", DB_FILE)

connection.close()
