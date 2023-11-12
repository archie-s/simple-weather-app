import tkinter as tk
from tkinter import ttk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime, timedelta

# Initialize Window
root = tk.Tk()
root.title("Weather App")

# Create a themed ttk style
style = ttk.Style(root)
style.theme_use("clam")

# Function to get weather information from OpenWeatherMapAPI
def get_weather(city):
    API_key = "cbf75635d2b92ecc0fb5937a868b6ccc"
    
    # Modify the URL to fetch forecast data
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_key}"
    res = requests.get(url)

    if res.status_code == 404:
        messagebox.showerror("Error", "City not found")
        return None

    # Parse the response JSON to get weather information
    weather_data = res.json()

    # Extract the current weather information (you can modify this as needed)
    current_weather = weather_data['list'][0]
    icon_id = current_weather['weather'][0]['icon']
    temperature = current_weather['main']['temp'] - 273.15
    description = current_weather['weather'][0]['description']
    city = weather_data['city']['name']
    country = weather_data['city']['country']

    # Get the icon URL and return all the weather information
    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
    return icon_url, temperature, description, city, country, weather_data['list'][1:]

# Function to search for weather in a city
def search():
    city = city_entry.get()
    result = get_weather(city)
    if result is None:
        return

    # If the city is found, unpack the weather information
    icon_url, temperature, description, city, country, forecast = result
    location_label.configure(text=f"{city}, {country}")

    # Get the weather icon image from the URL and update the icon label
    response = requests.get(icon_url, stream=True)
    image = Image.open(response.raw).convert("RGBA")
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon

    # Update the temperature and description labels
    temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
    description_label.configure(text=f"Description: {description}")

    # Display future weather predictions for the next day
    next_day_forecast = filter_next_day_forecast(forecast)
    formatted_forecast = "\n".join([f"{format_future_date(entry['dt_txt'])}: {entry['weather'][0]['description']}" for entry in next_day_forecast])
    forecast_label.configure(text=f"Future Predictions for the Next Day:\n{formatted_forecast}")

def filter_next_day_forecast(forecast):
    # Filter the forecast data to include only entries for the next day
    tomorrow = datetime.now() + timedelta(days=1)
    next_day_forecast = [entry for entry in forecast if datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S") < tomorrow + timedelta(days=1) and datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S") >= tomorrow]
    return next_day_forecast

def format_future_date(date_str):
    # Convert the date string to a more readable format
    dt_object = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    formatted_date = dt_object.strftime("%A, %B %d, %Y %I:%M %p")
    return formatted_date

# Entry widget -> to enter the city name
city_entry = ttk.Entry(root, font=("Helvetica", 18), width=30)
city_entry.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Button widget -> to search for weather information
search_button = ttk.Button(root, text="Search", command=search, style="TButton")
search_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

# Label widget -> to show the city/country name
location_label = tk.Label(root, font=("Helvetica", 25))
location_label.grid(row=1, column=0, columnspan=2, pady=10)

# Label widget -> to show the weather icon
icon_label = tk.Label(root)
icon_label.grid(row=2, column=0, columnspan=2, pady=10)

# Label widget -> to show the temperature
temperature_label = tk.Label(root, font=("Helvetica", 20))
temperature_label.grid(row=3, column=0, columnspan=2, pady=5)

# Label widget -> to show the weather description
description_label = tk.Label(root, font=("Helvetica", 20))
description_label.grid(row=4, column=0, columnspan=2, pady=5)

# Label widget -> to show future weather predictions
forecast_label = tk.Label(root, font=("Helvetica", 12), wraplength=400, justify="left")
forecast_label.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
