import os

from flask import Flask, jsonify, request
from pymongo import MongoClient, ReadPreference, WriteConcern

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise SystemExit("Set the MONGO_URI environment variable first.")

app = Flask(__name__)

client = MongoClient(MONGO_URI)
vehicles = client["ev_db"]["vehicles"]

fast_collection = vehicles.with_options(write_concern=WriteConcern(w=1))
safe_collection = vehicles.with_options(write_concern=WriteConcern(w="majority"))
primary_collection = vehicles.with_options(read_preference=ReadPreference.PRIMARY)
secondary_collection = vehicles.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)

@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    doc = request.get_json(force=True)
    result = fast_collection.insert_one(doc)
    return jsonify(str(result.inserted_id))

@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    doc = request.get_json(force=True)
    result = safe_collection.insert_one(doc)
    return jsonify(str(result.inserted_id))

@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():
    count = primary_collection.count_documents({"Make": "TESLA"})
    return jsonify({"count": count})

@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():
    count = secondary_collection.count_documents({"Make": "BMW"})
    return jsonify({"count": count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)