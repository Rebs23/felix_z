import requests
import csv
import os
from datetime import datetime

API_KEY = "AIzaSyDllyRngUouzxdsNlsS-w6Prc6jnwrwsWw"
SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

def search_leads(query, location_bias=None):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.websiteUri,places.primaryType,places.internationalPhoneNumber"
    }
    
    payload = {
        "textQuery": query,
        "maxResultCount": 10 # Pequeños batches para control
    }
    
    response = requests.post(SEARCH_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("places", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def save_to_csv(places, filename="memory/leads.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["id", "name", "title", "company", "sector", "linkedin", "email", "resonance", "rejections_24h", "pain", "status", "website"])
        
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown")
            website = p.get("websiteUri", "")
            # Evitar duplicados simples
            writer.writerow([
                p.get("id"), name, "Founder/CEO", name, "Technology", 
                "", "", 0.85, 0, "support automation", "new", website
            ])

if __name__ == "__main__":
    # Mercados clave: USA, UK, Germany
    queries = ["SaaS companies in San Francisco", "Software agencies in London", "Tech startups in Berlin"]
    for q in queries:
        print(f"Buscando leads para: {q}...")
        results = search_leads(q)
        save_to_csv(results)
    print("Búsqueda completada. Leads guardados en memory/leads.csv")
