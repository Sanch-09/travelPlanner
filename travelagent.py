# import streamlit as st
# import json
# import os
# from serpapi import GoogleSearch
# from agno.agent import Agent
# from agno.tools.serpapi import SerpApiTools
# from agno.models.google import Gemini
# from datetime import datetime
# import time
# import requests

# st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
# st.markdown(
#     """
#     <style>
#         .title {
#             text-align: center;
#             font-size: 36px;
#             font-weight: bold;
#             color: #ff5733;
#         }
#         .subtitle {
#             text-align: center;
#             font-size: 20px;
#             color: #555;
#         }
#         .stSlider > div {
#             background-color: #f9f9f9;
#             padding: 10px;
#             border-radius: 10px;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
# st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# st.markdown("### 🌍 Where are you headed?")
# source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
# destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

# st.markdown("### 📅 Plan Your Adventure")
# num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
# travel_theme = st.selectbox(
#     "🎭 Select Your Travel Theme:",
#     ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
# )

# st.markdown("---")
# st.markdown(
#     f"""
#     <div style="
#         text-align: center; 
#         padding: 15px; 
#         background-color: #ffecd1; 
#         border-radius: 10px; 
#         margin-top: 20px;
#     ">
#         <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
#         <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# def format_datetime(iso_string):
#     try:
#         dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
#         return dt.strftime("%b-%d, %Y | %I:%M %p")
#     except:
#         return "N/A"

# activity_preferences = st.text_area(
#     "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
#     "Relaxing on the beach, exploring historical sites"
# )

# departure_date = st.date_input("Departure Date")
# return_date = st.date_input("Return Date")

# st.sidebar.title("🌎 Travel Assistant")
# st.sidebar.subheader("Personalize Your Trip")
# budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
# flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
# hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# st.sidebar.subheader("🎒 Packing Checklist")
# packing_list = {
#     "👕 Clothes": True,
#     "🩴 Comfortable Footwear": True,
#     "🕶️ Sunglasses & Sunscreen": False,
#     "📖 Travel Guidebook": False,
#     "💊 Medications & First-Aid": True
# }
# for item, checked in packing_list.items():
#     st.sidebar.checkbox(item, value=checked)

# st.sidebar.subheader("🛂 Travel Essentials")
# visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
# travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
# currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# SERPAPI_KEY = "5571f0d71d1c38dadfcb62bdc8fa524df4f237e2716ebe1fc6fea9d20aa3a539"
# os.environ["GOOGLE_API_KEY"] = "AIzaSyDgr3ylT5jKHNncBB5vky_NRNfyTeYdM0Y"

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
#             results = search.get_dict()  # timeout handled internally by SerpAPI
#             if results:
#                 return results
#         except Exception as e:
#             print(f"Attempt {attempt + 1} failed: {e}")
#         time.sleep(2)

#     return None


# def extract_cheapest_flights(flight_data):
#     best_flights = flight_data.get("best_flights", [])
#     sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
#     return sorted_flights

# researcher = Agent(
#     name="Researcher",
#     instructions=[
#         "Identify the travel destination specified by the user.",
#         "Gather detailed information on the destination, including climate, culture, and safety tips.",
#         "Find popular attractions, landmarks, and must-visit places.",
#         "Search for activities that match the user’s interests and travel style.",
#         "Prioritize information from reliable sources and official travel guides.",
#         "Provide well-structured summaries with key insights and recommendations."
#     ],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     tools=[SerpApiTools(api_key=SERPAPI_KEY)]
# )

# planner = Agent(
#     name="Planner",
#     instructions=[
#         "Gather details about the user's travel preferences and budget.",
#         "Create a detailed itinerary with scheduled activities and estimated costs.",
#         "Ensure the itinerary includes transportation options and travel time estimates.",
#         "Optimize the schedule for convenience and enjoyment.",
#         "Present the itinerary in a structured format."
#     ],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     tools=[SerpApiTools(api_key=SERPAPI_KEY)]
# )

# # Hotel & Restaurant Finder Agent
# hotel_restaurant_finder = Agent(
#     name="Hotel & Restaurant Finder",
#     instructions=[
#         "Identify key locations in the user's travel itinerary.",
#         "Search for highly rated hotels near those locations using SerpApi.",
#         "Search for top-rated restaurants based on cuisine preferences and proximity.",
#         "Prioritize results based on user preferences, ratings, and availability.",
#         "Provide direct booking links or reservation options where possible."
#     ],
#     model=Gemini(id="gemini-2.0-flash-exp"),
#     tools=[SerpApiTools(api_key=SERPAPI_KEY)]
# )

# def fetch_hotels_and_restaurants(destination, travel_theme, budget, hotel_rating, activity_preferences):
#     safe_travel_theme = travel_theme.encode('ascii', 'ignore').decode()
#     prompt = (
#         f"Find the best hotels and restaurants near popular attractions in {destination} "
#         f"for a {safe_travel_theme.lower()} trip. Budget: {budget}. "
#         f"Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
#     )
#     try:
#         results = hotel_restaurant_finder.run(prompt, stream=False)
#         return results
#     except Exception as e:
#         st.warning(f"Hotel & Restaurant search failed: {e}")
#         return None


# flight_data = None
# cheapest_flights = []
# hotel_restaurant_results = None
# research_results = None
# itinerary = None

# if st.button("🚀 Generate Travel Plan"):
#     # ----------------- Flights -----------------
#     with st.spinner("✈️ Fetching best flight options..."):
#         flight_data, cheapest_flights = None, []
#         for attempt in range(3):
#             try:
#                 flight_data = fetch_flights(source, destination, departure_date, return_date, retries=3, timeout=15)
#                 if flight_data:
#                     break
#             except Exception as e:
#                 st.warning(f"Attempt {attempt + 1} failed: {e}")
#             time.sleep(2)

#         if not flight_data:
#             st.warning("⚠️ No flights found or API timed out.")
#         else:
#             cheapest_flights = extract_cheapest_flights(flight_data)
#             st.success(f"✅ Found {len(cheapest_flights)} flight options!")

#     # ----------------- Hotels & Restaurants -----------------
#     with st.spinner("🏨 Searching for hotels & restaurants..."):
#         try:
#             hotel_restaurant_results = fetch_hotels_and_restaurants(
#                 destination=destination,
#                 travel_theme=travel_theme,
#                 budget=budget,
#                 hotel_rating=hotel_rating,
#                 activity_preferences=activity_preferences
#             )
#         except Exception as e:
#             if "429" in str(e):
#                 st.warning("⚠️ Hotel & Restaurant search skipped (API rate limit reached).")
#             else:
#                 st.warning(f"Hotel & Restaurant search failed: {e}")
#             hotel_restaurant_results = None

#     # ----------------- Research -----------------
#     with st.spinner("🔍 Researching best attractions & activities..."):
#         try:
#             research_prompt = (
#                 f"Research the best attractions and activities in {destination} "
#                 f"for a {num_days}-day {travel_theme.lower()} trip. "
#                 f"The traveler enjoys: {activity_preferences}. "
#                 f"Budget: {budget}. Flight Class: {flight_class}. "
#                 f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. "
#                 f"Travel Insurance: {travel_insurance}."
#             )
#             research_results = researcher.run(research_prompt, stream=False)
#         except Exception as e:
#             if "429" in str(e):
#                 st.warning("⚠️ Research skipped (API rate limit reached). Using fallback info.")
#                 research_results = None
#             else:
#                 st.warning(f"Research failed: {e}")
#                 research_results = None

#     # ----------------- Itinerary -----------------
#     with st.spinner("🗺️ Creating your personalized itinerary..."):
#         try:
#             research_text = (
#                 research_results.content
#                 if research_results else f"No live research data. Create a {num_days}-day itinerary for {destination}."
#             )
#             planning_prompt = (
#                 f"Based on the following data, create a {num_days}-day itinerary "
#                 f"for a {travel_theme.lower()} trip to {destination}. "
#                 f"The traveler enjoys: {activity_preferences}. Budget: {budget}. "
#                 f"Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
#                 f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. "
#                 f"Research: {research_text}. "
#                 f"Flights: {json.dumps(cheapest_flights)}. "
#                 f"Hotels & Restaurants: {hotel_restaurant_results.content if hotel_restaurant_results else 'N/A'}."
#             )
#             itinerary = planner.run(planning_prompt, stream=False)
#         except Exception as e:
#             if "429" in str(e):
#                 st.warning("⚠️ Itinerary generation skipped (API rate limit reached). Showing generic itinerary.")
#                 itinerary = None
#             else:
#                 st.warning(f"Itinerary generation failed: {e}")
#                 itinerary = None

#     # ----------------- Display Results -----------------
#     st.subheader("✈️ Cheapest Flight Options")
#     if cheapest_flights:
#         for flight in cheapest_flights:
#             st.json(flight)  # render flight info as small expandable JSON cards
#     else:
#         st.write("No flight data available.")

#     st.subheader("🏨 Hotels & Restaurants")
#     if hotel_restaurant_results:
#         st.write(hotel_restaurant_results.content)
#     else:
#         st.write("⚠️ No hotel/restaurant data available.")

#     st.subheader("🗺️ Your Personalized Itinerary")
#     if itinerary:
#         st.write(itinerary.content)
#     else:
#         st.write(f"⚠️ No live itinerary. Here's a generic {num_days}-day itinerary suggestion for {destination}.")
#         st.write(f"- Day 1: Arrival and local exploration\n- Day 2: Sightseeing\n- Day 3: Adventure activities\n- Day 4: Relaxation\n- Day 5: Departure")

#     st.success("🎉 Travel plan generated successfully!")


import streamlit as st
import json
import os
from serpapi import GoogleSearch
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime
import time
import requests

st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

st.markdown("### 🌍 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)

st.markdown("---")
st.markdown(
    f"""
    <div style="
        text-align: center; 
        padding: 15px; 
        background-color: #ffecd1; 
        border-radius: 10px; 
        margin-top: 20px;
    ">
        <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")
    except:
        return "N/A"

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites"
)

departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# --- Keys (replace with your keys or use st.secrets in production) ---
SERPAPI_KEY = "5571f0d71d1c38dadfcb62bdc8fa524df4f237e2716ebe1fc6fea9d20aa3a539"
os.environ["GOOGLE_API_KEY"] ="AIzaSyDgr3ylT5jKHNncBB5vky_NRNfyTeYdM0Y"

# params_base used if we need to call flights with departure_token for booking link
params_base = {
    "engine": "google_flights",
    "currency": "INR",
    "hl": "en",
    "api_key": SERPAPI_KEY
}

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
            results = search.get_dict()  # SerpAPI client does internal timeout handling
            if results:
                return results
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(2)

    return None


def extract_cheapest_flights(flight_data):
    """
    Extracts the cheapest flights safely from SerpAPI results.
    Handles both best_flights and other_flights keys.
    """
    if not flight_data:
        return []

    flights = []

    # Prefer best_flights
    if "best_flights" in flight_data:
        flights.extend(flight_data.get("best_flights", []))

    # Sometimes results are in other_flights
    if not flights and "other_flights" in flight_data:
        flights.extend(flight_data.get("other_flights", []))

    # Defensive sort by price if available
    try:
        flights = sorted(flights, key=lambda x: x.get("price", float("inf")))[:3]
    except Exception as e:
        print("Sorting flights failed:", e)

    return flights


researcher = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user’s interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

planner = Agent(
    name="Planner",
    instructions=[
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

# Hotel & Restaurant Finder Agent
hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations using SerpApi.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide direct booking links or reservation options where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)]
)

def fetch_hotels_and_restaurants(destination, travel_theme, budget, hotel_rating, activity_preferences):
    safe_travel_theme = travel_theme.encode('ascii', 'ignore').decode()
    prompt = (
        f"Find the best hotels and restaurants near popular attractions in {destination} "
        f"for a {safe_travel_theme.lower()} trip. Budget: {budget}. "
        f"Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
    )
    try:
        results = hotel_restaurant_finder.run(prompt, stream=False)
        return results
    except Exception as e:
        st.warning(f"Hotel & Restaurant search failed: {e}")
        return None


flight_data = None
cheapest_flights = []
hotel_restaurant_results = None
research_results = None
itinerary = None

if st.button("🚀 Generate Travel Plan"):
    # ----------------- Flights -----------------
    with st.spinner("✈️ Fetching best flight options..."):
        flight_data, cheapest_flights = None, []
        for attempt in range(3):
            try:
                flight_data = fetch_flights(source, destination, departure_date, return_date, retries=3, timeout=15)
                if flight_data and ("best_flights" in flight_data or "other_flights" in flight_data):
                    break
            except Exception as e:
                st.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

        if not flight_data:
            st.warning("⚠️ No flights found or API timed out.")
        else:
            cheapest_flights = extract_cheapest_flights(flight_data)
            if cheapest_flights:
                st.success(f"✅ Found {len(cheapest_flights)} flight options!")
            else:
                st.warning("⚠️ Flights found, but no parsable options in response.")


    # ----------------- Hotels & Restaurants -----------------
    with st.spinner("🏨 Searching for hotels & restaurants..."):
        try:
            hotel_restaurant_results = fetch_hotels_and_restaurants(
                destination=destination,
                travel_theme=travel_theme,
                budget=budget,
                hotel_rating=hotel_rating,
                activity_preferences=activity_preferences
            )
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Hotel & Restaurant search skipped (API rate limit reached).")
            else:
                st.warning(f"Hotel & Restaurant search failed: {e}")
            hotel_restaurant_results = None

    # ----------------- Research -----------------
    with st.spinner("🔍 Researching best attractions & activities..."):
        try:
            research_prompt = (
                f"Research the best attractions and activities in {destination} "
                f"for a {num_days}-day {travel_theme.lower()} trip. "
                f"The traveler enjoys: {activity_preferences}. "
                f"Budget: {budget}. Flight Class: {flight_class}. "
                f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. "
                f"Travel Insurance: {travel_insurance}."
            )
            research_results = researcher.run(research_prompt, stream=False)
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Research skipped (API rate limit reached). Using fallback info.")
                research_results = None
            else:
                st.warning(f"Research failed: {e}")
                research_results = None

    # ----------------- Itinerary -----------------
    with st.spinner("🗺️ Creating your personalized itinerary..."):
        try:
            research_text = (
                research_results.content
                if research_results else f"No live research data. Create a {num_days}-day itinerary for {destination}."
            )
            planning_prompt = (
                f"Based on the following data, create a {num_days}-day itinerary "
                f"for a {travel_theme.lower()} trip to {destination}. "
                f"The traveler enjoys: {activity_preferences}. Budget: {budget}. "
                f"Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
                f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. "
                f"Research: {research_text}. "
                f"Flights: {json.dumps(cheapest_flights)}. "
                f"Hotels & Restaurants: {hotel_restaurant_results.content if hotel_restaurant_results else 'N/A'}."
            )
            itinerary = planner.run(planning_prompt, stream=False)
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Itinerary generation skipped (API rate limit reached). Showing generic itinerary.")
                itinerary = None
            else:
                st.warning(f"Itinerary generation failed: {e}")
                itinerary = None

    # ----------------- Display Results (Beautiful flight cards) -----------------
    st.subheader("✈️ Cheapest Flight Options")
    if cheapest_flights:
        # limit to actual number of flights (should be <=3) and create columns
        cols = st.columns(len(cheapest_flights))
        for idx, flight in enumerate(cheapest_flights):
            with cols[idx]:
                # basic fields
                airline_logo = flight.get("airline_logo", "")
                # some responses have airline at top-level, or inside flights list
                airline_name = flight.get("airline", None)
                price = flight.get("price", "Not Available")
                total_duration = flight.get("total_duration", "N/A")

                flights_info = flight.get("flights", [{}])
                departure = flights_info[0].get("departure_airport", {}) if flights_info else {}
                arrival = flights_info[-1].get("arrival_airport", {}) if flights_info else {}
                airline_name = airline_name or flights_info[0].get("airline", "Unknown Airline")

                departure_time = format_datetime(departure.get("time", "N/A"))
                arrival_time = format_datetime(arrival.get("time", "N/A"))

                # booking link handling (defensive)
                departure_token = flight.get("departure_token", "")
                booking_token = None
                if departure_token:
                    try:
                        params_with_token = {
                            **params_base,
                            "departure_id": source,
                            "arrival_id": destination,
                            "outbound_date": str(departure_date),
                            "return_date": str(return_date),
                            "departure_token": departure_token
                        }
                        search_with_token = GoogleSearch(params_with_token)
                        results_with_booking = search_with_token.get_dict()
                        best_flights = results_with_booking.get("best_flights", [])
                        if best_flights and len(best_flights) > 0:
                            booking_token = best_flights[0].get("booking_token")
                    except Exception as e:
                        # don't fail the whole app for booking token issues
                        print("Booking-token lookup failed:", e)
                        booking_token = None

                booking_link = f"https://www.google.com/travel/flights?tfs={booking_token}" if booking_token else "#"

                # Nice card
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ddd;
                        border-radius: 10px;
                        padding: 12px;
                        text-align: center;
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
                        background-color: #fff;
                        margin-bottom: 12px;
                    ">
                        <div style="display:flex;align-items:center;justify-content:center;gap:12px;">
                            <img src="{airline_logo}" width="72" alt="Airline logo" />
                            <div style="text-align:left;">
                                <div style="font-size:16px;font-weight:700;">{airline_name}</div>
                                <div style="font-size:13px;color:#666;">{departure.get('id','')} → {arrival.get('id','')}</div>
                            </div>
                        </div>
                        <div style="margin-top:10px;">
                            <div><strong>Departure:</strong> {departure_time}</div>
                            <div><strong>Arrival:</strong> {arrival_time}</div>
                            <div><strong>Duration:</strong> {total_duration} min</div>
                        </div>
                        <div style="margin-top:12px;">
                            <span style="font-size:20px;font-weight:800;color:#008000;">₹{price}</span>
                        </div>
                        <div style="margin-top:10px;">
                            <a href="{booking_link}" target="_blank" style="
                                display:inline-block;padding:8px 14px;border-radius:6px;background-color:#007bff;color:#fff;text-decoration:none;font-weight:600;
                            ">{'🔗 Book Now' if booking_token else '🔍 View Details'}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("⚠ No flight data available.")

    st.subheader("🏨 Hotels & Restaurants")
    if hotel_restaurant_results:
        st.write(hotel_restaurant_results.content)
    else:
        st.write("⚠️ No hotel/restaurant data available.")

    st.subheader("🗺️ Your Personalized Itinerary")
    if itinerary:
        st.write(itinerary.content)
    else:
        st.write(f"⚠️ No live itinerary. Here's a generic {num_days}-day itinerary suggestion for {destination}.")
        st.write(f"- Day 1: Arrival and local exploration\n- Day 2: Sightseeing\n- Day 3: Adventure activities\n- Day 4: Relaxation\n- Day 5: Departure")

    st.success("🎉 Travel plan generated successfully!")
