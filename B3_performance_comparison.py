
import time
import random
import sqlite3
import pandas as pd

random.seed(42)

# Dataset sizes for comparison
dataset_sizes = [10000, 50000, 100000]
station_names = ["Central", "North", "South", "East", "West"]

print("AIR QUALITY PERFORMANCE COMPARISON")
print("=" * 65)

for size in dataset_sizes:

    # Generate sample air-quality data
    records = [
        (
            random.choice(station_names),
            round(random.uniform(10, 150), 2)
        )
        for _ in range(size)
    ]

    print(f"\nDataset size: {size} records")

    # Method 1: Python loops
    loop_times = []

    for _ in range(3):
        start = time.perf_counter()

        totals = {}
        counts = {}

        for station, pm25 in records:
            totals[station] = totals.get(station, 0) + pm25
            counts[station] = counts.get(station, 0) + 1

        loop_result = {
            station: totals[station] / counts[station]
            for station in totals
        }

        loop_times.append(time.perf_counter() - start)

    loop_time = min(loop_times)

    # Method 2: Pandas
    df = pd.DataFrame(records, columns=["station", "pm25"])
    pandas_times = []

    for _ in range(3):
        start = time.perf_counter()

        pandas_result = df.groupby("station")["pm25"].mean()

        pandas_times.append(time.perf_counter() - start)

    pandas_time = min(pandas_times)

    # Method 3: SQLite
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE readings (
            station TEXT,
            pm25 REAL
        )
    """)

    cursor.executemany(
        "INSERT INTO readings VALUES (?, ?)", records
    )

    cursor.execute(
        "CREATE INDEX station_index ON readings(station)"
    )

    sql_times = []

    for _ in range(3):
        start = time.perf_counter()

        cursor.execute("""
            SELECT station, AVG(pm25)
            FROM readings
            GROUP BY station
        """)

        sql_result = cursor.fetchall()

        sql_times.append(time.perf_counter() - start)

    sql_time = min(sql_times)

    # Display comparison
    print("Python Loop :", round(loop_time, 6), "seconds")
    print("Pandas      :", round(pandas_time, 6), "seconds")
    print("SQLite      :", round(sql_time, 6), "seconds")

    fastest = min(
        [
            (loop_time, "Python Loop"),
            (pandas_time, "Pandas"),
            (sql_time, "SQLite")
        ]
    )

    print("Fastest method:", fastest[1])

    connection.close()

print("\nPerformance comparison completed successfully.")
