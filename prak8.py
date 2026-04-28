from serpapi import GoogleSearch
from pymongo import MongoClient
from datetime import datetime


API_KEY = "6c73db39942c97d338175a39e7d9c856a1c4a2df5487587405e9f21d8fce7d12"
MONGO_URI = "mongodb+srv://welly_db_user:user123@testingp2.hcayut5.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["serpapi_db"]

collection = db["product_data"]

params = {
    "api_key": API_KEY,
    "engine": "google",
    "q": "Asics Metaspeed", 
    "google_domain": "google.com",
    "gl": "us",
    "hl": "en"
}

search = GoogleSearch(params)

# Debug: Cek raw response
try:
    results = search.get_dict()
except Exception as e:
    print(f"Error: {e}")
    # Cek raw response dari API
    raw_response = search.get_results()
    print(f"Raw API Response: {raw_response}")
    print(f"Response length: {len(raw_response)}")
    exit()

data_to_insert = []

if "organic_results" in results:
    organic_results = results["organic_results"]
    
    for item in organic_results:
        data = {
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
            "position": item.get("position"),
            "source": item.get("source"),
            "date": item.get("date"),
            "thumbnail": item.get("thumbnail"),
            "created_at": datetime.utcnow()
        }
        data_to_insert.append(data)

elif "immersive_products" in results:
    immersive_products = results["immersive_products"]
    
    for product in immersive_products:
        data = {
            "title": product.get("title"),
            "link": product.get("link"),
            "snippet": product.get("snippet"),
            "price": product.get("price"),
            "rating": product.get("rating"),
            "thumbnail": product.get("thumbnail"),
            "created_at": datetime.utcnow()
        }
        data_to_insert.append(data)

if data_to_insert:
    try:
        collection.insert_many(data_to_insert)
        print(f"✅ {len(data_to_insert)} data berhasil disimpan ke MongoDB")
    except Exception as e:
        print("❌ Error saat insert:", e)
else:
    print("⚠️ Data tidak ditemukan")
    print("Keys yang tersedia:", list(results.keys()))