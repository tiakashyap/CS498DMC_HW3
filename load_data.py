import csv
import os
import sys
import time

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    sys.exit("Error: MONGO_URI environment variable not set.")

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "ev.csv"
if not os.path.exists(CSV_PATH):
    sys.exit(f"Could not find CSV file at: {CSV_PATH}")
BATCH_SIZE = 5000

INT_FIELDS = {"Model Year", "Electric Range", "Base MSRP", "Legislative District", "DOL Vehicle ID"}


def clean(row):
    doc = {}
    for key, value in row.items():
        if key is None:
            continue
        value = value.strip() if isinstance(value, str) else value
        if value == "" or value is None:
            continue 
        if key in INT_FIELDS:
            try:
                value = int(value)
            except ValueError:
                pass
        doc[key] = value
    return doc


def main():
    client = MongoClient(MONGO_URI)
    client.admin.command("ping") 
    print("Connected to Atlas")

    collection = client["ev_db"]["vehicles"]
    collection.drop() 

    start = time.time()
    batch, total = [], 0
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            batch.append(clean(row))
            if len(batch) >= BATCH_SIZE:
                collection.insert_many(batch, ordered=False)
                total += len(batch)
                batch = []
                print(f"-> Inserted batch, total so far: {total}")
    if batch:
        collection.insert_many(batch, ordered=False)
        total += len(batch)

    print(f"{total} documents in {time.time() - start:.1f}s")
    print("Count in DB:", collection.count_documents({}))


if __name__ == "__main__":
    main()