from serpapi import GoogleSearch
from pymongo import MongoClient
from datetime import datetime

API_KEY  = "6c73db39942c97d338175a39e7d9c856a1c4a2df5487587405e9f21d8fce7d12"
MONGO_URI = "mongodb+srv://welly_db_user:user123@testingp2.hcayut5.mongodb.net/"

client = MongoClient(MONGO_URI)
db     = client["serpapi_db"]
collection = db["product_data"]


def get_thumbnail(item: dict) -> str | None:
    """
    Coba ambil thumbnail dari beberapa kemungkinan lokasi
    yang berbeda-beda tergantung tipe hasil Google.
    """
    return (
        item.get("thumbnail")
        or item.get("image")
        or item.get("rich_snippet", {}).get("top", {}).get("thumbnail")
        or item.get("about_page_serpapi_link")   # fallback minimal
        or None
    )

params = {
    "api_key": API_KEY,
    "engine": "google",
    "q": "Asics Metaspeed",
    "google_domain": "google.com",
    "gl": "us",
    "hl": "en",
    "tbm": "",          # kosong = semua hasil; ganti "shop" untuk Shopping tab
}

try:
    search  = GoogleSearch(params)
    results = search.get_dict()
except Exception as e:
    print(f"❌ Gagal menghubungi SerpAPI: {e}")
    exit()

print("📦 Keys tersedia di response:", list(results.keys()))

data_to_insert = []
source_used    = None

if "organic_results" in results:
    source_used = "organic_results"
    for item in results["organic_results"]:
        data = {
            "result_type": "organic",
            "title":     item.get("title"),
            "link":      item.get("link"),
            "snippet":   item.get("snippet"),
            "position":  item.get("position"),
            "source":    item.get("source"),
            # date hanya tersedia untuk halaman berita/artikel
            "date":      item.get("date"),
            # thumbnail pakai helper karena field-nya tidak konsisten
            "thumbnail": get_thumbnail(item),
            "created_at": datetime.utcnow(),
        }
        data_to_insert.append(data)

if "shopping_results" in results:
    source_used = (source_used or "") + "+shopping_results"
    for product in results["shopping_results"]:
        data = {
            "result_type": "shopping",
            "title":       product.get("title"),
            "link":        product.get("link"),
            "snippet":     product.get("snippet"),
            "price":       product.get("price"),
            "rating":      product.get("rating"),
            "reviews":     product.get("reviews"),
            "source":      product.get("source"),
            "thumbnail":   product.get("thumbnail"),   # hampir selalu ada
            "date":        None,                        # tidak relevan untuk produk
            "created_at":  datetime.utcnow(),
        }
        data_to_insert.append(data)

if "immersive_products" in results:
    source_used = (source_used or "") + "+immersive_products"
    for product in results["immersive_products"]:
        data = {
            "result_type": "immersive",
            "title":       product.get("title"),
            "link":        product.get("link"),
            "snippet":     product.get("snippet"),
            "price":       product.get("price"),
            "rating":      product.get("rating"),
            "thumbnail":   product.get("thumbnail"),
            "date":        None,
            "created_at":  datetime.utcnow(),
        }
        data_to_insert.append(data)

if data_to_insert:
    try:
        result = collection.insert_many(data_to_insert)
        print(f"✅ {len(result.inserted_ids)} data berhasil disimpan ke MongoDB")
        print(f"   Sumber data: {source_used}")

        # Ringkasan: berapa yang punya thumbnail / date
        has_thumbnail = sum(1 for d in data_to_insert if d.get("thumbnail"))
        has_date      = sum(1 for d in data_to_insert if d.get("date"))
        print(f"   🖼  Punya thumbnail : {has_thumbnail}/{len(data_to_insert)}")
        print(f"   📅  Punya date      : {has_date}/{len(data_to_insert)}"
              "  ← wajar jika sedikit (hanya artikel/berita)")
    except Exception as e:
        print("❌ Error saat insert ke MongoDB:", e)
else:
    print("⚠️  Tidak ada data yang ditemukan.")
    print("    Keys tersedia:", list(results.keys()))