# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS
# import json
# import os
# import time
# from datetime import datetime
# from serpapi.google_search import GoogleSearch
# from agno.agent import Agent
# from agno.tools.serpapi import SerpApiTools
# from agno.models.google import Gemini
# from dotenv import load_dotenv

# # -------------------------------------------------------------
# # 🌍 Load environment variables
# # -------------------------------------------------------------
# load_dotenv()

# SERPAPI_KEY = os.getenv("SERPAPI_KEY")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# if not SERPAPI_KEY or not GOOGLE_API_KEY:
#     raise ValueError("❌ Missing SERPAPI_KEY or GOOGLE_API_KEY in .env file")

# os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# # -------------------------------------------------------------
# # ⚙ Flask App Setup
# # -------------------------------------------------------------
# app = Flask(__name__)
# CORS(app)

# # Base params for SerpAPI flight search
# params_base = {
#     "engine": "google_flights",
#     "currency": "INR",
#     "hl": "en",
#     "api_key": SERPAPI_KEY
# }

# # -------------------------------------------------------------
# # ⏰ Helper Functions
# # -------------------------------------------------------------
# def format_datetime(iso_string):
#     try:
#         dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
#         return dt.strftime("%b-%d, %Y | %I:%M %p")
#     except Exception:
#         return "N/A"


# def fetch_flights(source, destination, departure_date, return_date, retries=3, timeout=10):
#     params = {
#         "engine": "google_flights",
#         "departure_id": source,
#         "arrival_id": destination,
#         "outbound_date": str(departure_date),
#         "return_date": str(return_date),
#         "currency": "INR",
#         "hl": "en",
#         "api_key": SERPAPI_KEY
#     }

#     for attempt in range(retries):
#         try:
#             search = GoogleSearch(params)
#             results = search.get_dict()
#             if results:
#                 return results
#         except Exception as e:
#             print(f"Attempt {attempt + 1} failed: {e}")
#         time.sleep(2)

#     return None


# def extract_cheapest_flights(flight_data):
#     """Extract the cheapest flights safely from SerpAPI results."""
#     if not flight_data:
#         return []

#     flights = []

#     # Prefer best_flights
#     if "best_flights" in flight_data:
#         flights.extend(flight_data.get("best_flights", []))

#     # Fallback to other_flights
#     if not flights and "other_flights" in flight_data:
#         flights.extend(flight_data.get("other_flights", []))

#     try:
#         flights = sorted(flights, key=lambda x: x.get("price", float("inf")))[:3]
#     except Exception as e:
#         print("Sorting flights failed:", e)

#     return flights

# # -------------------------------------------------------------
# # 🤖 AI Agents Initialization
# # -------------------------------------------------------------
# research_agent = Agent(
#     name="Researcher",
#     instructions=[
#         "Identify the travel destination specified by the user.",
#         "Gather detailed information on the destination, including climate, culture, and safety tips.",
#         "Find popular attractions, landmarks, and must-visit places.",
#         "Search for activities that match the user's interests and travel style.",
#         "Prioritize reliable sources and official travel guides.",
#         "Provide structured summaries with insights and recommendations."
#     ],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     tools=[SerpApiTools(api_key=SERPAPI_KEY)]
# )

# trip_planner_agent = Agent(
#     name="Planner",
#     instructions=[
#         "Gather user travel preferences and budget.",
#         "Create a detailed itinerary with activities, estimated costs, and travel time.",
#         "Optimize schedule for convenience and enjoyment.",
#         "Present the itinerary in a clear structured format."
#     ],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     tools=[SerpApiTools(api_key=SERPAPI_KEY)]
# )

# hotel_restaurant_agent = Agent(
#     name="Hotel & Restaurant Finder",
#     instructions=[
#         "Identify key locations in the user's travel itinerary.",
#         "Find highly rated hotels near those locations using SerpApi.",
#         "Search for top-rated restaurants based on cuisine and proximity.",
#         "Prioritize based on ratings, budget, and availability.",
#         "Provide booking or reservation links where possible."
#     ],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     tools=[SerpApiTools(api_key=SERPAPI_KEY)]
# )

# # -------------------------------------------------------------
# # 🏨 Hotels & Restaurants Fetch Function
# # -------------------------------------------------------------
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

# # -------------------------------------------------------------
# # 🌐 Routes
# # -------------------------------------------------------------
# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/planner')
# def planner_page():
#     return render_template('planner.html')

# # -------------------------------------------------------------
# # 🧭 API: Generate Travel Plan
# # -------------------------------------------------------------
# @app.route('/api/generate-plan', methods=['POST'])
# def generate_plan():
#     try:
#         data = request.json

#         source = data.get('source', 'BOM')
#         destination = data.get('destination', 'DEL')
#         num_days = int(data.get('num_days', 5))
#         travel_theme = data.get('travel_theme', 'Adventure Trip')
#         activity_preferences = data.get('activity_preferences', '')
#         departure_date = data.get('departure_date')
#         return_date = data.get('return_date')
#         budget = data.get('budget', 'Standard')
#         flight_class = data.get('flight_class', 'Economy')
#         hotel_rating = data.get('hotel_rating', 'Any')
#         visa_required = data.get('visa_required', False)
#         travel_insurance = data.get('travel_insurance', False)

#         result = {
#             'flights': [],
#             'hotels_restaurants': None,
#             'research': None,
#             'itinerary': None,
#             'errors': []
#         }

#         # ✈ Fetch Flights
#         flight_data = None
#         cheapest_flights = []

#         for attempt in range(3):
#             try:
#                 flight_data = fetch_flights(source, destination, departure_date, return_date, retries=3, timeout=15)
#                 if flight_data and ("best_flights" in flight_data or "other_flights" in flight_data):
#                     break
#             except Exception as e:
#                 result['errors'].append(f"Flight fetch attempt {attempt + 1} failed: {str(e)}")
#             time.sleep(2)

#         if not flight_data:
#             result['errors'].append("No flights found or API timed out.")
#         else:
#             cheapest_flights = extract_cheapest_flights(flight_data)
#             formatted_flights = []

#             for flight in cheapest_flights:
#                 flights_info = flight.get("flights", [{}])
#                 departure = flights_info[0].get("departure_airport", {}) if flights_info else {}
#                 arrival = flights_info[-1].get("arrival_airport", {}) if flights_info else {}
#                 airline_name = flight.get("airline") or flights_info[0].get("airline", "Unknown Airline")

#                 formatted_flight = {
#                     'airline': airline_name,
#                     'airline_logo': flight.get("airline_logo", ""),
#                     'price': flight.get("price", "Not Available"),
#                     'total_duration': flight.get("total_duration", "N/A"),
#                     'departure_time': format_datetime(departure.get("time", "N/A")),
#                     'arrival_time': format_datetime(arrival.get("time", "N/A")),
#                     'departure_airport': departure.get("id", ""),
#                     'arrival_airport': arrival.get("id", ""),
#                     'booking_link': None
#                 }
#                 formatted_flights.append(formatted_flight)

#             result['flights'] = formatted_flights

#         # 🏨 Fetch Hotels & Restaurants
#         try:
#             hotel_restaurant_results = fetch_hotels_and_restaurants(
#                 destination=destination,
#                 travel_theme=travel_theme,
#                 budget=budget,
#                 hotel_rating=hotel_rating,
#                 activity_preferences=activity_preferences
#             )
#             if hotel_restaurant_results:
#                 result['hotels_restaurants'] = hotel_restaurant_results.content
#         except Exception as e:
#             if "429" in str(e):
#                 result['errors'].append("Hotel & Restaurant search skipped (API rate limit reached).")
#             else:
#                 result['errors'].append(f"Hotel & Restaurant search failed: {str(e)}")

#         # 🧭 Research
#         try:
#             research_prompt = (
#                 f"Research the best attractions and activities in {destination} "
#                 f"for a {num_days}-day {travel_theme.lower()} trip. "
#                 f"The traveler enjoys: {activity_preferences}. "
#                 f"Budget: {budget}. Flight Class: {flight_class}. "
#                 f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. "
#                 f"Travel Insurance: {travel_insurance}."
#             )
#             research_results = research_agent.run(research_prompt, stream=False)
#             if research_results:
#                 result['research'] = research_results.content
#         except Exception as e:
#             if "429" in str(e):
#                 result['errors'].append("Research skipped (API rate limit reached).")
#             else:
#                 result['errors'].append(f"Research failed: {str(e)}")

#         # 🗓 Generate Itinerary
#         try:
#             research_text = (
#                 result['research']
#                 if result['research'] else f"No live research data. Create a {num_days}-day itinerary for {destination}."
#             )
#             planning_prompt = (
#                 f"Based on the following data, create a {num_days}-day itinerary "
#                 f"for a {travel_theme.lower()} trip to {destination}. "
#                 f"The traveler enjoys: {activity_preferences}. Budget: {budget}. "
#                 f"Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
#                 f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. "
#                 f"Research: {research_text}. "
#                 f"Flights: {json.dumps(cheapest_flights)}. "
#                 f"Hotels & Restaurants: {result['hotels_restaurants'] if result['hotels_restaurants'] else 'N/A'}."
#             )
#             itinerary = trip_planner_agent.run(planning_prompt, stream=False)
#             if itinerary:
#                 result['itinerary'] = itinerary.content
#         except Exception as e:
#             if "429" in str(e):
#                 result['errors'].append("Itinerary generation skipped (API rate limit reached).")
#             else:
#                 result['errors'].append(f"Itinerary generation failed: {str(e)}")

#         return jsonify(result)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # -------------------------------------------------------------
# # 🚀 Run App
# # -------------------------------------------------------------
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)





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

# -------------------------------------------------------------
# 🧪 MOCK DATA (Hotels & Restaurants)
# -------------------------------------------------------------
MOCK_HOTELS_RESTAURANTS = {
    "hotels": [
        {
            "name": "Sea View Residency",
            "location": "Near Baga Beach",
            "price_per_night": "₹3,500",
            "rating": 4.2,
            "amenities": ["Free WiFi", "AC", "Breakfast Included"]
        },
        {
            "name": "Palm Grove Boutique Hotel",
            "location": "Calangute",
            "price_per_night": "₹4,800",
            "rating": 4.5,
            "amenities": ["Pool", "Parking", "Restaurant"]
        },
        {
            "name": "Budget Inn Comfort",
            "location": "Panaji City Center",
            "price_per_night": "₹2,200",
            "rating": 3.9,
            "amenities": ["WiFi", "Room Service"]
        }
    ],
    "restaurants": [
        {
            "name": "Fisherman’s Wharf",
            "cuisine": "Seafood, Goan",
            "price_range": "₹₹₹",
            "rating": 4.6,
            "location": "Ribandar"
        },
        {
            "name": "Gunpowder",
            "cuisine": "South Indian, Fusion",
            "price_range": "₹₹",
            "rating": 4.5,
            "location": "Assagao"
        },
        {
            "name": "Cafe Chocolatti",
            "cuisine": "Cafe, Desserts",
            "price_range": "₹₹",
            "rating": 4.4,
            "location": "Candolim"
        }
    ]
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


def fetch_flights(source, destination, departure_date, return_date, retries=3):
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
            print(f"Flight attempt {attempt + 1} failed: {e}")
        time.sleep(2)

    return None


def extract_cheapest_flights(flight_data):
    if not flight_data:
        return []

    flights = []
    flights.extend(flight_data.get("best_flights", []))
    if not flights:
        flights.extend(flight_data.get("other_flights", []))

    try:
        flights = sorted(flights, key=lambda x: x.get("price", float("inf")))[:3]
    except Exception:
        pass

    return flights

# -------------------------------------------------------------
# 🤖 AI Agents
# -------------------------------------------------------------
research_agent = Agent(
    name="Researcher",
    instructions=["Research destination and attractions."],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

trip_planner_agent = Agent(
    name="Planner",
    instructions=["Create structured multi-day itinerary."],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

hotel_restaurant_agent = Agent(
    name="HotelFinder",
    instructions=["Find hotels and restaurants near attractions."],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

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
    data = request.json

    destination = data.get('destination', 'Goa')
    num_days = int(data.get('num_days', 5))
    travel_theme = data.get('travel_theme', 'Leisure')
    activity_preferences = data.get('activity_preferences', '')
    budget = data.get('budget', 'Standard')

    result = {
        "flights": [],
        "hotels_restaurants": None,
        "research": None,
        "itinerary": None,
        "errors": []
    }

    # 🏨 Hotels & Restaurants (TRY API → FALLBACK TO MOCK)
    try:
        hr_prompt = f"Find hotels and restaurants in {destination}"
        hr_result = hotel_restaurant_agent.run(hr_prompt, stream=False)
        if hr_result:
            result["hotels_restaurants"] = hr_result.content
    except Exception as e:
        result["hotels_restaurants"] = MOCK_HOTELS_RESTAURANTS
        result["errors"].append("Hotel & Restaurant API limit reached → Mock data used")

    # 🧭 Research
    try:
        research = research_agent.run(
            f"Top attractions in {destination} for {num_days} days", stream=False
        )
        result["research"] = research.content
    except Exception:
        result["research"] = f"Popular beaches, markets, and cultural spots in {destination}."

    # 🗓 Itinerary
    try:
        itinerary = trip_planner_agent.run(
            f"Create a {num_days}-day itinerary for {destination}", stream=False
        )
        result["itinerary"] = itinerary.content
    except Exception:
        result["itinerary"] = (
            f"Day 1: Arrival & local exploration\n"
            f"Day 2: Sightseeing\n"
            f"Day 3: Adventure & leisure\n"
            f"Day 4: Relaxation\n"
            f"Day 5: Departure"
        )

    return jsonify(result)

# -------------------------------------------------------------
# 🚀 Run App
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
