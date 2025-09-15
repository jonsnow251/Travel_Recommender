import pandas as pd
import streamlit as st
import urllib.parse
import requests
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# ========================
# OpenWeatherMap API
# ========================
API_KEY = "f591cb47f2a0cf363029e7c302d3202b"

def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].title()
        }
    return None

# ========================
# Load CSV
# ========================
df = pd.read_csv("places.csv")

# ========================
# Encode Interest for ML
# ========================
le = LabelEncoder()
df['Interest_enc'] = le.fit_transform(df['Interest'])

# Features & target
X = df[['Cost', 'Interest_enc']]
y = df['Name']

# Train Decision Tree
model = DecisionTreeClassifier()
model.fit(X, y)

# ========================
# Streamlit UI
# ========================
st.set_page_config(page_title="Travel Recommender", layout="wide")
st.title("🌍 ML-Based Travel Recommender")

budget = st.number_input("Enter your budget (₹)", min_value=10000, value=12000)
days = st.number_input("Enter number of days", min_value=1, value=3)

# ========================
# Session State
# ========================
if 'city_index' not in st.session_state:
    st.session_state.city_index = 0
if 'filtered_cities' not in st.session_state:
    st.session_state.filtered_cities = pd.DataFrame()

# ========================
# Recommend Button
# ========================
if st.button("Recommend Me!"):
    # Encode interest values for prediction (we don't take interest input)
    features = [[budget, val] for val in df['Interest_enc'].unique()]
    predictions = model.predict(features)

    # Filter predictions within ±2000 budget
    filtered = df[(df["Cost"] >= budget - 2000) & (df["Cost"] <= budget + 2000)]
    if filtered.empty:
        st.warning("No city matches your budget 😞")
        st.session_state.filtered_cities = pd.DataFrame()
    else:
        st.session_state.filtered_cities = filtered.reset_index(drop=True)
        st.session_state.city_index = 0

# ========================
# Show current recommendation
# ========================
if not st.session_state.filtered_cities.empty:
    city_row = st.session_state.filtered_cities.iloc[st.session_state.city_index]

    st.subheader(f"{city_row['Name']} 🌆")
    st.write(f"**Interest:** {city_row['Interest']}")
    st.write(f"**Cost:** ₹{city_row['Cost']}")
    st.write(f"**Best Time to Visit:** {city_row['Best_Time']}")
    st.write(f"**Places to Visit:** {city_row['Plan']}")

    # Weather
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

    # Next Recommendation Button
    if st.button("Next Recommendation"):
        st.session_state.city_index += 1
        if st.session_state.city_index >= len(st.session_state.filtered_cities):
            st.session_state.city_index = 0
        st.experimental_rerun()
