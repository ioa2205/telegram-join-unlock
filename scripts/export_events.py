import argparse
import asyncio
import csv
import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import Database
from app.config import load_config

async def main():
    parser = argparse.ArgumentParser(description="Export the events table to a CSV file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    load_dotenv()
    config = load_config()
    db = Database(config.db_path)
    await db.connect()

    events = await db.fetchall("SELECT id, user_id, type, slug, ts FROM events ORDER BY ts ASC")

    if not events:
        print("No events to export.")
        return

    try:
        with open(args.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=events[0].keys())
            writer.writeheader()
            writer.writerows(events)
        print(f"Successfully exported {len(events)} events to {args.output_file}")
    except IOError as e:
        print(f"Error writing to file: {e}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())