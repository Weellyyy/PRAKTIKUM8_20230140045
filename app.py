from gc import collect
from http import client
from re import search

from serpapi import GoogleSearch
from pymongo import MongoClient
from datetime import datetime

API_KEY = "6c73db39942c97d338175a39e7d9c856a1c4a2df5487587405e9f21d8fce7d12"
MONGO_URI = "mongodb+srv://welly_db_user:user123@testingp2.hcayut5.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["serpapi_db"]
collection = db["search_us"]

params = {
    "api_key": API_KEY,
    "engine": "google",
    "q": "manchester united",
    "google_domain": "google.co.id",
    "gl": "us",
    "hl": "en",
}

search = GoogleSearch(params)
results = search.get_dict()

data_to_insert = []

if "organic_results" in results:
    for result in results["organic_results"]:
        data = {
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet"),
            "position": result.get("position"),
            "created_at": datetime.utcnow()
        }
        data_to_insert.append(data)
        
if data_to_insert:
    try:
        collection.insert_many(data_to_insert)
        print(f"{len(data_to_insert)} data berhasil disimpan")
    except Exception as e:
        print(f"Error saat insert:", e)
else:
    print("keys:", results.keys())