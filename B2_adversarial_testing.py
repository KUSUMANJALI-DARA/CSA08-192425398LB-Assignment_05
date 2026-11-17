
import csv
import sqlite3
import os
from datetime import datetime

CSV_FILE = "adversarial_data.csv"

# Step 1: Create test data
test_data = [
    ["S01", "Central", "2026-11-01", "09:00", "45", "80"],
    ["S02", "North", "2026-11-01", "10:00", "abc", "90"],
    ["S03", "South", "2026-11-01", "11:00", "-10", "70"],
    ["S04", "East", "invalid-date", "12:00", "30", "60"],
    ["S01", "Central", "2026-11-01", "09:00", "45", "80"],
    ["S05", "'; DROP TABLE readings; --", "2026-11-01", "13:00", "55", "85"],
    ["S06", "West", "2026-11-01", "14:00", "40"]
]

with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "station_id", "station_name", "date",
        "time", "pm25", "pm10"
    ])
    writer.writerows(test_data)

print("ADVERSARIAL DATA TESTING")
print("------------------------")

# Step 2: Create database
connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE readings (
    station_id TEXT,
    station_name TEXT,
    reading_date TEXT,
    reading_time TEXT,
    pm25 REAL,
    pm10 REAL
)
""")

accepted = 0
rejected = 0
duplicates = 0
seen = set()

# Step 3: Validate records
with open(CSV_FILE, "r", newline="") as file:
    reader = csv.reader(file)
    header = next(reader)

    for line_number, row in enumerate(reader, start=2):

        if len(row) != 6:
            print(f"Row {line_number}: Rejected - incorrect columns")
            rejected += 1
            continue

        station_id, name, date, time, pm25, pm10 = row

        try:
            datetime.strptime(date, "%Y-%m-%d")
            pm25 = float(pm25)
            pm10 = float(pm10)

            if pm25 < 0 or pm10 < 0:
                raise ValueError("Negative pollutant value")

        except ValueError:
            print(f"Row {line_number}: Rejected - invalid data")
            rejected += 1
            continue

        key = (station_id, date, time)

        if key in seen:
            print(f"Row {line_number}: Duplicate record")
            duplicates += 1
            continue

        seen.add(key)

        # Parameterised query protects against SQL injection
        cursor.execute("""
            INSERT INTO readings VALUES (?, ?, ?, ?, ?, ?)
        """, (station_id, name, date, time, pm25, pm10))

        accepted += 1

# Step 4: Display results
connection.commit()

print("\nTEST RESULTS")
print("Accepted records:", accepted)
print("Rejected records:", rejected)
print("Duplicate records:", duplicates)

cursor.execute("SELECT * FROM readings")

print("\nSTORED DATABASE RECORDS")
for record in cursor.fetchall():
    print(record)

# Step 5: Verify database still exists
cursor.execute("""
SELECT name FROM sqlite_master
WHERE type='table' AND name='readings'
""")

if cursor.fetchone():
    print("\nSQL injection protection test: PASSED")
    print("Database table remains safe.")

connection.close()
os.remove(CSV_FILE)
