import pandas as pd
import streamlit as st
import urllib.parse
import requests

# ========================
# OpenWeatherMap API
# ========================
API_KEY = "f591cb47f2a0cf363029e7c302d3202b"


def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].title()
        }
        return weather
    else:
        return None


# ========================
# Load CSV
# ========================
df = pd.read_csv("places.csv")

# ========================
# App Title
# ========================
st.set_page_config(page_title="Travel Recommender", layout="wide")
st.title("🌍 Travel Recommender System")

# ========================
# User Inputs
# ========================
budget = st.number_input("Enter your budget (₹)", min_value=10000, value=12000)
days = st.number_input("Enter number of days", min_value=1, value=3)

# ========================
# Session State for Next Recommendation
# ========================
if 'city_index' not in st.session_state:
    st.session_state.city_index = 0
if 'filtered_cities' not in st.session_state:
    st.session_state.filtered_cities = pd.DataFrame()

# ========================
# Recommendation Button
# ========================
if st.button("Recommend Me!"):
    # Filter cities with exact budget OR close to budget ±2000
    filtered = df[(df["Cost"] >= budget - 2000) & (df["Cost"] <= budget + 2000)]

    if filtered.empty:
        st.warning("No city matches your budget 😞")
        st.session_state.filtered_cities = pd.DataFrame()
    else:
        st.session_state.filtered_cities = filtered.reset_index(drop=True)
        st.session_state.city_index = 0

# ========================
# Show current city
# ========================
if not st.session_state.filtered_cities.empty:
    city_row = st.session_state.filtered_cities.iloc[st.session_state.city_index]

    st.subheader(f"{city_row['Name']} 🌆")
    st.write(f"**Interest:** {city_row['Interest']}")
    st.write(f"**Cost:** ₹{city_row['Cost']}")
    st.write(f"**Best Time to Visit:** {city_row['Best_Time']}")
    st.write(f"**Places to Visit:** {city_row['Plan']}")

    # ✅ Fetch real-time weather
    weather = get_current_weather(city_row['Name'])
    if weather:
        st.write(f"**Weather:** {weather['description']}, {weather['temperature']}°C 🌤️")
    else:
        st.write("**Weather:** Data not available")

    # Directions
    places = city_row['Plan'].split(", ")
    directions_list = [urllib.parse.quote(f"{place}, {city_row['Name']}") for place in places]
    directions_link = "https://www.google.com/maps/dir/" + "/".join(directions_list)
    st.markdown(f"**Directions from current location:** [Click Here]({directions_link}) 🗺️", unsafe_allow_html=True)

    # ========================
    # Next Recommendation Button
    # ========================
    if st.button("Next Recommendation"):
        st.session_state.city_index += 1
        if st.session_state.city_index >= len(st.session_state.filtered_cities):
            st.session_state.city_index = 0  # Loop back to first city
