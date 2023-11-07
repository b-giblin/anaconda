import sqlite3
import requests
from datetime import datetime

# Replace 'your_api_key' with your actual OpenWeatherMap API key
API_KEY = 'your_api_key'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Connect to SQLite database
conn = sqlite3.connect('weather_trends.db')
cursor = conn.cursor()

# Create a table to store weather data
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    temperature REAL NOT NULL,
    city TEXT NOT NULL
)
''')
conn.commit()

def fetch_weather(city):
    """Fetch weather data from OpenWeatherMap API for a given city."""
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # Fetch temperature in Celsius
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        # Convert Unix timestamp to a readable date format
        date = datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        return date, temperature
    else:
        print(f"Error fetching data from OpenWeatherMap API: {response.status_code}")
        return None, None

def insert_weather_data(date, temperature, city):
    """Insert weather data into the SQLite database."""
    cursor.execute('''
    INSERT INTO weather_data (date, temperature, city)
    VALUES (?, ?, ?)
    ''', (date, temperature, city))
    conn.commit()

def get_average_temperature(city):
    """Get the average temperature for a given city from the SQLite database."""
    cursor.execute('''
    SELECT AVG(temperature) FROM weather_data WHERE city = ?
    ''', (city,))
    result = cursor.fetchone()
    return result[0] if result else None

# Example of fetching weather data for a specific city and inserting it into the database
city_name = input("Enter the city name: ")
date, temperature = fetch_weather(city_name)
if date and temperature:
    insert_weather_data(date, temperature, city_name)
    print(f"Inserted weather data for {city_name}: {temperature}°C on {date}")

# Retrieve and print the average temperature for the city
average_temp = get_average_temperature(city_name)
if average_temp:
    print(f"The average temperature in {city_name} is {average_temp:.2f}°C")
else:
    print("No data available for the given city.")

# Close the database connection
conn.close()