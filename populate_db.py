import os
import requests
import openai
import json
from pymongo import MongoClient
import time
import re
import pycountry
import uuid
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# MongoDB Connection (Using Docker Compose Service Name)
MONGO_URI=os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_DB_USERNAME = os.getenv("MONGO_DB_ROOT_USERNAME")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_ROOT_PASSWORD")
COLLECTION_NAME = "destinations"

# OpenRouter AI API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# GeoNames API Configuration
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME")  # Set this in .env
GEONAMES_URL = f"http://api.geonames.org/citiesJSON?north=90&south=-90&east=180&west=-180&maxRows=100&username={GEONAMES_USERNAME}"


def get_country_name(country_code):
    """Convert country code to full country name."""
    country = pycountry.countries.get(alpha_2=country_code)
    return country.name if country else country_code  # Fallback to code if not found

def fetch_top_cities(n):
    """Fetches the top 10 cities dynamically from GeoNames API with full country names."""
    response = requests.get(GEONAMES_URL)
    if response.status_code == 200:
        data = response.json()
        return [(city["name"], get_country_name(city["countrycode"])) for city in data.get("geonames", [])[:n]]  
    else:
        print("❌ Error fetching city data from GeoNames API")
        return []


def clean_json_response(response_text):
    """Extract and clean JSON from the AI response."""
    match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
    return match.group(1) if match else response_text  # Extract JSON or return original text

def generate_travel_data(city, country):
    """Fetches travel clues, fun facts, and trivia using OpenRouter AI."""
    prompt = f"""
    Provide travel data for {city}, {country}:
    - 2 unique clues about the city without telling the city or country
    - 2 fun facts.
    - 2 trivia facts.
    
    Format the response as a JSON object with keys: city, country, clues, fun_fact, trivia.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/ministral-8b",  # ✅ Fixed model name
        "messages": [
            {"role": "system", "content": "You are a travel assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        raw_content = response_data["choices"][0]["message"]["content"]

        # ✅ Clean JSON output by removing backticks
        cleaned_json = clean_json_response(raw_content)

        try:
            return json.loads(cleaned_json)  # ✅ Now it should parse correctly
        except (KeyError, json.JSONDecodeError):
            print(f"❌ Error processing data for {city}, {country}")
            return None
    else:
        print(f"❌ OpenRouter API Error: {response.status_code} - {response.text}")
        return None


def store_data_in_mongodb(data):
    """Bulk inserts travel data into MongoDB using authentication."""
    # client = pymongo.MongoClient(MONGO_URI, username=MONGO_DB_USERNAME, password=MONGO_DB_PASSWORD)
    client = MongoClient(
        "mongodb+srv://mongo_user:mongo_pass@cluster0.eak9p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        authSource="admin"  # 👈 Ensure authentication happens in the "admin" database
    )
    db = client.get_database("globetrotter_mongo")
    collection = db[COLLECTION_NAME]
    
    if data:
        collection.insert_many(data)
        print(f"✅ Inserted {len(data)} records into MongoDB!")

def generate_uuid():
    """Generates a globally unique ID."""
    return str(uuid.uuid4())

if __name__ == "__main__":
    travel_data = []
    n=21
    cities = fetch_top_cities(n)

    for city, country in cities:
        print(f"📍 Fetching data for {city}, {country}...")
        city_data = generate_travel_data(city, country)
        if city_data:
            city_data["_id"] = generate_uuid()
            travel_data.append(city_data)
        
        time.sleep(1.5)  # Prevent API rate limits
    
    if travel_data:
        # breakpoint()
        store_data_in_mongodb(travel_data)

    print("🎉 Dataset expanded & inserted into MongoDB successfully!")

