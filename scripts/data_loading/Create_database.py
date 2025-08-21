import pandas as pd
import sqlite3

# Read the CSV
df = pd.read_csv(r'C:\Users\Arjan\Desktop\Music_Project\Hot 100.csv')

# Create database connection
conn = sqlite3.connect('music_database.db')

# Save dataframe to database table
df.to_sql('billboard_hot100', conn, if_exists='replace', index=False)

print("Database created successfully!")
print(f"Saved {len(df)} records to 'billboard_hot100' table")

# Close connection
conn.close()