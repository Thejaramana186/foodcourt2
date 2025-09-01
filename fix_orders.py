import sqlite3

db_path = "fooddelivery_auth.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN customer_id INTEGER;")
    print("✅ Added customer_id column to orders table.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Skipped: {e}")

conn.commit()
conn.close()
