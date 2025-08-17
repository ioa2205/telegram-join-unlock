import argparse
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import Database
from app.config import load_config
from app.services.slugs import is_valid_slug

async def main():
    parser = argparse.ArgumentParser(description="Seed or manage slugs in the database.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Add or update a slug.")
    add_parser.add_argument("--slug", required=True, help="The unique slug identifier (e.g., 'ielts_pack').")
    add_parser.add_argument("--label", required=True, help="The user-facing label for the button.")
    add_parser.add_argument("--file-id", default="MISSING", help="Optional Telegram file_id.")

    # 'list' command
    subparsers.add_parser("list", help="List all existing slugs.")

    args = parser.parse_args()

    load_dotenv()
    config = load_config()
    db = Database(config.db_path)
    await db.connect()

    if args.command == "add":
        if not is_valid_slug(args.slug):
            print(f"Error: Invalid slug format for '{args.slug}'. Use a-z, 0-9, _ (2-50 chars).")
            return

        query = """
        INSERT INTO slugs (slug, label, file_id, active) VALUES (?, ?, ?, 1)
        ON CONFLICT(slug) DO UPDATE SET
            label = excluded.label,
            file_id = excluded.file_id;
        """
        await db.execute(query, (args.slug, args.label, args.file_id))
        print(f"Successfully added/updated slug '{args.slug}'.")

    elif args.command == "list":
        slugs = await db.fetchall("SELECT slug, label, file_id FROM slugs")
        if not slugs:
            print("No slugs found in the database.")
            return
        
        print(f"{'SLUG':<25} {'LABEL':<40} {'FILE ID SET'}")
        print("-" * 80)
        for slug in slugs:
            file_id_status = "Yes" if slug['file_id'] != "MISSING" else "No"
            print(f"{slug['slug']:<25} {slug['label']:<40} {file_id_status}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())