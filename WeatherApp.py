import customtkinter as ctk
import requests
import geocoder
import time
from PIL import Image, ImageTk
from plyer import notification
from datetime import datetime

# OpenWeather API Key
API_KEY = "cbf75635d2b92ecc0fb5937a868b6ccc"

# Set Dark Mode Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create App Window
app = ctk.CTk()
app.geometry("500x700")
app.title("Weather App")

# Function to Get GPS-Based Location
def get_location():
    try:
        g = geocoder.ip("me")  # Get approximate location using IP
        if g.ok:
            return g.city, g.latlng[0], g.latlng[1]
    except:
        return None, None, None

# Function to Fetch Weather Data
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    weather_data = res.json()
    current_weather = weather_data['list'][0]

    icon_id = current_weather['weather'][0]['icon']
    temperature = current_weather['main']['temp'] - 273.15
    description = current_weather['weather'][0]['description']
    humidity = current_weather['main']['humidity']
    wind_speed = current_weather['wind']['speed']

    city = weather_data['city']['name']
    country = weather_data['city']['country']

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"

    return icon_url, temperature, description, humidity, wind_speed, city, country, weather_data['list'][1:]

# Function to Check Rain in Next Few Hours
def check_rain(forecast):
    for entry in forecast[:5]:  # Check next ~15 hours
        if "rain" in entry["weather"][0]["description"].lower():
            return True
    return False

# Function to Update Weather Information
def update_weather():
    city, lat, lon = get_location()
    if not city:
        return

    result = get_weather(lat, lon)
    if result is None:
        return

    icon_url, temperature, description, humidity, wind_speed, city, country, forecast = result
    location_label.configure(text=f"{city}, {country}")

    # Fetch and display weather icon
    response = requests.get(icon_url, stream=True)
    image = Image.open(response.raw).convert("RGBA")
    # Convert to CTkImage and specify size
    icon = ctk.CTkImage(light_image=image, size=(100, 100))
    icon_label.configure(image=icon)
    icon_label.image = icon

    # Update temperature, humidity, and wind speed
    temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
    description_label.configure(text=f"Condition: {description.capitalize()}")
    humidity_label.configure(text=f"Humidity: {humidity}%")
    wind_label.configure(text=f"Wind Speed: {wind_speed} m/s")

    # Check for Rain Alert
    if check_rain(forecast):
        notification.notify(
            title="Weather Alert ☔",
            message="Rain is expected in your area in the next few hours.",
            timeout=10
        )

# UI Elements
location_label = ctk.CTkLabel(app, text="Fetching location...", font=("Arial", 20))
location_label.pack(pady=15)

icon_label = ctk.CTkLabel(app, text="")
icon_label.pack()

temperature_label = ctk.CTkLabel(app, text="Temperature: --°C", font=("Arial", 18))
temperature_label.pack(pady=10)

description_label = ctk.CTkLabel(app, text="Condition: --", font=("Arial", 16))
description_label.pack(pady=5)

humidity_label = ctk.CTkLabel(app, text="Humidity: --%", font=("Arial", 14))
humidity_label.pack(pady=5)

wind_label = ctk.CTkLabel(app, text="Wind Speed: -- m/s", font=("Arial", 14))
wind_label.pack(pady=5)

update_button = ctk.CTkButton(app, text="Update Weather", command=update_weather)
update_button.pack(pady=20)

# Fetch Weather on Startup
update_weather()

# Run App
app.mainloop()
