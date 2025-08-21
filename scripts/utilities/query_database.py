import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('music_database.db')

# Query Elvis songs that hit #1
query = """
SELECT song, performer, chart_date, peak_position, time_on_chart
FROM billboard_hot100 
WHERE performer LIKE '%Elvis%' AND peak_position = 1
ORDER BY chart_date
"""

results = pd.read_sql_query(query, conn)
print("Elvis #1 hits:")
print(results)

conn.close()