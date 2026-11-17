
import sqlite3
import pandas as pd

# Sample air-quality data
data = {
    "station": ["Central", "North", "South", "East", "West"],
    "pm25": [45, 80, 35, 110, 25],
    "pm10": [80, 120, 70, 150, 50],
    "no2": [22, 35, 18, 45, 15]
}

df = pd.DataFrame(data)

# Step 1: Data analysis
print("FINAL AIR QUALITY SYSTEM")
print("=" * 45)

print("\nSTATION-WISE DATA")
print(df.to_string(index=False))

# Step 2: Calculate averages
print("\nAVERAGE POLLUTANT LEVELS")
print("PM2.5:", round(df["pm25"].mean(), 2))
print("PM10 :", round(df["pm10"].mean(), 2))
print("NO2  :", round(df["no2"].mean(), 2))

# Step 3: Identify highest PM2.5 station
highest = df.loc[df["pm25"].idxmax()]

print("\nHIGHEST PM2.5 STATION")
print("Station:", highest["station"])
print("PM2.5:", highest["pm25"])

# Step 4: Store results in SQLite
connection = sqlite3.connect("final_air_quality.db")

df.to_sql(
    "air_quality",
    connection,
    if_exists="replace",
    index=False
)

# Create index
cursor = connection.cursor()

cursor.execute("""
CREATE INDEX IF NOT EXISTS station_index
ON air_quality(station)
""")

# Step 5: Retrieve database records
print("\nDATABASE RECORDS")

cursor.execute("""
SELECT station, pm25, pm10, no2
FROM air_quality
ORDER BY pm25 DESC
""")

for record in cursor.fetchall():
    print(record)

# Step 6: Rule-based chatbot
print("\nAIR QUALITY CHATBOT")
print("Ask about PM2.5, PM10, NO2, or pollution.")

questions = {
    "pm2.5": "PM2.5 refers to fine particulate matter.",
    "pm10": "PM10 refers to inhalable particulate matter.",
    "no2": "NO2 is nitrogen dioxide, an air pollutant.",
    "pollution": "Vehicle emissions and industrial activities contribute to air pollution."
}

user_question = "What is PM2.5?".lower()

response = "Sorry, I do not understand that question."

for keyword, answer in questions.items():
    if keyword in user_question:
        response = answer
        break

print("User:", user_question)
print("Chatbot:", response)

# Step 7: Final decision
print("\nFINAL ENGINEERING DECISION")
print("Python and Pandas: Data processing")
print("SQLite: Structured data storage")
print("AI: Sentiment analysis, summarisation and chatbot")
print("System evaluation completed successfully.")

connection.close()
