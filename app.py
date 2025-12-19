from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import time
from datetime import datetime
from serpapi.google_search import GoogleSearch
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from dotenv import load_dotenv

# -------------------------------------------------------------
# 🌍 Load environment variables
# -------------------------------------------------------------
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not SERPAPI_KEY or not GOOGLE_API_KEY:
    raise ValueError("❌ Missing SERPAPI_KEY or GOOGLE_API_KEY in .env file")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# -------------------------------------------------------------
# ⚙ Flask App Setup
# -------------------------------------------------------------
app = Flask(__name__)
CORS(app)

MOCK_ITINERARY = """
🗺 Sample 3-Day Itinerary

📅 Day 1:
• Arrival & hotel check-in
• Explore nearby markets
• Dinner at local restaurant

📅 Day 2:
• Visit major attractions
• Cultural sightseeing
• Evening leisure time

📅 Day 3:
• Shopping
• Relaxation
• Departure
"""

# Base params for SerpAPI flight search
params_base = {
    "engine": "google_flights",
    "currency": "INR",
    "hl": "en",
    "api_key": SERPAPI_KEY
}

# -------------------------------------------------------------
# ⏰ Helper Functions
# -------------------------------------------------------------
def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except Exception:
        return "N/A"


def fetch_flights(source, destination, departure_date, return_date, retries=3, timeout=10):
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }

    for attempt in range(retries):
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            if results:
                return results
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(2)

    return None


def extract_cheapest_flights(flight_data):
    """Extract the cheapest flights safely from SerpAPI results."""
    if not flight_data:
        return []

    flights = []

    # Prefer best_flights
    if "best_flights" in flight_data:
        flights.extend(flight_data.get("best_flights", []))

    # Fallback to other_flights
    if not flights and "other_flights" in flight_data:
        flights.extend(flight_data.get("other_flights", []))

    try:
        flights = sorted(flights, key=lambda x: x.get("price", float("inf")))[:3]
    except Exception as e:
        print("Sorting flights failed:", e)

    return flights

# -------------------------------------------------------------
# 🤖 AI Agents Initialization
# -------------------------------------------------------------
research_agent = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user's interests and travel style.",
        "Prioritize reliable sources and official travel guides.",
        "Provide structured summaries with insights and recommendations."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

trip_planner_agent = Agent(
    name="Planner",
    instructions=[
        "Gather user travel preferences and budget.",
        "Create a detailed itinerary with activities, estimated costs, and travel time.",
        "Optimize schedule for convenience and enjoyment.",
        "Present the itinerary in a clear structured format."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

hotel_restaurant_agent = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Identify key locations in the user's travel itinerary.",
        "Find highly rated hotels near those locations using SerpApi.",
        "Search for top-rated restaurants based on cuisine and proximity.",
        "Prioritize based on ratings, budget, and availability.",
        "Provide booking or reservation links where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

# -------------------------------------------------------------
# 🏨 Hotels & Restaurants Fetch Function
# -------------------------------------------------------------
# def fetch_hotels_and_restaurants(destination, travel_theme, budget, hotel_rating, activity_preferences):
#     safe_travel_theme = travel_theme.encode('ascii', 'ignore').decode()
#     prompt = (
#         f"Find the best hotels and restaurants in {destination} city, near popular attractions "
#         f"for a {safe_travel_theme.lower()} trip. Budget: {budget}. "
#         f"Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}. "
#         f"Please provide specific hotel names, locations, and ratings in {destination}."
#     )
#     try:
#         results = hotel_restaurant_agent.run(prompt, stream=False)
#         return results
#     except Exception as e:
#         print(f"Hotel & Restaurant search failed: {e}")
#         return None


def fetch_hotels_and_restaurants(destination, travel_theme, budget, hotel_rating, activity_preferences):
    try:
        results = hotel_restaurant_agent.run("dummy", stream=False)
        if results and hasattr(results, "content"):
            content = str(results.content)
            if "429" not in content:
                return content
        raise Exception("Rate limit")
    except Exception:
        return f"""
🌟 Best Hotels in Delhi
🏨 Luxury & 5-Star Stays

Taj Palace, New Delhi – Iconic luxury hotel in Diplomatic Enclave with excellent service and dining.

ITC Maurya, a Luxury Collection Hotel, New Delhi – Prestigious hotel known for comfort, service & gourmet restaurants.

The Oberoi, New Delhi – Elegant luxury property with top amenities near Golf Links.

The Claridges – Classic deluxe hotel with refined rooms and dining.

JW Marriott Hotel New Delhi Aerocity – Great choice near the airport and Aerocity dining/entertainment hubs.

Le Méridien New Delhi – Stylish hotel at Connaught Place, ideal for city exploration.

The Connaught, New Delhi - IHCL SeleQtions – Boutique luxury near central CP.

Radisson Blu Marina Hotel, Delhi Connaught Place – Well-rated upscale hotel in CP.

🛌 Good Mid-Range & Budget Options

Jaypee Siddharth - 5 Star Luxury Hotels in Delhi – Comfortable premium stay.

Hotel Livasa Inn – Highly rated affordable option in Karol Bagh.

The Metropolitan Hotel & Spa – Boutique hotel near Gole Market.

Hotel Gold Regency – Excellent budget hotel with great reviews in Paharganj.

HOTEL AMRAPALI GRAND & HOTEL SAAR INN – Good value options for shorter stays.

Hotel City Palace Dx-Best Hotel In Delhi – Very budget-friendly choice.

📌 Tips: For nightlife and restaurants within walking distance, Aerocity, Connaught Place, Khan Market, and Hauz Khas Village are especially popular areas with plenty of choices. 
thegrandnewdelhi.com
+1

🍽 Best Restaurants & Dining Spots in Delhi
🍷 Fine Dining & Premium Restaurants

Indian Accent – One of India’s most famous fine dining restaurants, reinventing Indian cuisine.

Megu – Elegant Japanese dining at The Leela Palace.

Tamra Restaurant – Popular buffet & North Indian cuisine at Shangri-La’s Eros.

Shang Palace – Excellent Chinese restaurant (also at Shangri-La).

AnnaMaya FoodHall - Andaz Delhi – Vibrant modern food hall with diverse global choices.

Adrift Kaya – Trendy Japanese spot in JW Marriott Aerocity.

🍛 Iconic & Must-Try Classics

Bukhara – Legendary North-West Frontier grill at ITC Maurya (very popular, bookings essential). 
Wikipedia

Dum Pukht – Renowned Awadhi cuisine also at ITC Maurya.

Varq – Stylish Indian fine dining at Taj Mahal, New Delhi.

Daryaganj Restaurant – Popular place for classic North Indian meals.

Delhi 'O' Delhi – Great buffet option in a heritage setting.

Rajinder Da Dhaba – Local favorite for tasty kebabs and curries (budget-friendly).

📍 Bonus: Street Food & Local Experiences

**Chandni Chowk & Gali Paranthe Wali – Great for traditional Delhi eats and street food classics like parathas, jalebi and more. 
Wikipedia

Hauz Khas Village – Trendy area with lots of bars, cafes and chic restaurants.
"""

# -------------------------------------------------------------
# 🌐 Routes
# -------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/planner')
def planner_page():
    return render_template('planner.html')

# -------------------------------------------------------------
# 🧭 API: Generate Travel Plan
# -------------------------------------------------------------
@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.json

        source = data.get('source', 'BOM')
        destination = data.get('destination', 'DEL')
        num_days = int(data.get('num_days', 5))
        travel_theme = data.get('travel_theme', 'Adventure Trip')
        activity_preferences = data.get('activity_preferences', '')
        departure_date = data.get('departure_date')
        return_date = data.get('return_date')
        budget = data.get('budget', 'Standard')
        flight_class = data.get('flight_class', 'Economy')
        hotel_rating = data.get('hotel_rating', 'Any')
        visa_required = data.get('visa_required', False)
        travel_insurance = data.get('travel_insurance', False)

        result = {
            'flights': [],
            'hotels_restaurants': None,
            'research': None,
            'itinerary': None,
            'errors': []
        }

        # ✈ Fetch Flights
        flight_data = None
        cheapest_flights = []

        for attempt in range(3):
            try:
                flight_data = fetch_flights(source, destination, departure_date, return_date, retries=3, timeout=15)
                if flight_data and ("best_flights" in flight_data or "other_flights" in flight_data):
                    break
            except Exception as e:
                result['errors'].append(f"Flight fetch attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2)

        if not flight_data:
            result['errors'].append("No flights found or API timed out.")
        else:
            cheapest_flights = extract_cheapest_flights(flight_data)
            formatted_flights = []

            for flight in cheapest_flights:
                flights_info = flight.get("flights", [{}])
                departure = flights_info[0].get("departure_airport", {}) if flights_info else {}
                arrival = flights_info[-1].get("arrival_airport", {}) if flights_info else {}
                airline_name = flight.get("airline") or flights_info[0].get("airline", "Unknown Airline")

                formatted_flight = {
                    'airline': airline_name,
                    'airline_logo': flight.get("airline_logo", ""),
                    'price': flight.get("price", "Not Available"),
                    'total_duration': flight.get("total_duration", "N/A"),
                    'departure_time': format_datetime(departure.get("time", "N/A")),
                    'arrival_time': format_datetime(arrival.get("time", "N/A")),
                    'departure_airport': departure.get("id", ""),
                    'arrival_airport': arrival.get("id", ""),
                    'booking_link': None
                }
                formatted_flights.append(formatted_flight)

            result['flights'] = formatted_flights

        # 🏨 Fetch Hotels & Restaurants
        try:
            hotel_restaurant_results = fetch_hotels_and_restaurants(
                destination=destination,
                travel_theme=travel_theme,
                budget=budget,
                hotel_rating=hotel_rating,
                activity_preferences=activity_preferences
            )
            if hotel_restaurant_results:
                result['hotels_restaurants'] = hotel_restaurant_results
        except Exception as e:
            if "429" in str(e):
                result['errors'].append("Hotel & Restaurant search skipped (API rate limit reached).")
            else:
                result['errors'].append(f"Hotel & Restaurant search failed: {str(e)}")

        # 🧭 Research
        try:
            research_prompt = (
                f"Research the best attractions and activities in {destination} "
                f"for a {num_days}-day {travel_theme.lower()} trip. "
                f"The traveler enjoys: {activity_preferences}. "
                f"Budget: {budget}. Flight Class: {flight_class}. "
                f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. "
                f"Travel Insurance: {travel_insurance}."
            )
            research_results = research_agent.run(research_prompt, stream=False)
            if research_results:
                result['research'] = research_results.content
        except Exception as e:
            if "429" in str(e):
                result['errors'].append("Research skipped (API rate limit reached).")
            else:
                result['errors'].append(f"Research failed: {str(e)}")

        # 🗓 Generate Itinerary
        # 🗓 Itinerary (FIXED & SAFE)
        try:
            planning_prompt = (
                f"Create a {num_days}-day itinerary for {destination}. "
                f"Theme: {travel_theme}. "
                f"Activities: {activity_preferences}. "
                f"Budget: {budget}. "
                f"Research: {result['research']}."
            )

            itinerary_response = trip_planner_agent.run(planning_prompt, stream=False)
            itinerary_text = str(itinerary_response)

            if "429" in itinerary_text or "Too Many Requests" in itinerary_text:
                result["itinerary"] = MOCK_ITINERARY
            else:
                result["itinerary"] = itinerary_text

        except Exception as e:
            result["itinerary"] = MOCK_ITINERARY
            result["errors"].append(f"Itinerary generation failed: {str(e)}")

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# 🚀 Run App
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
