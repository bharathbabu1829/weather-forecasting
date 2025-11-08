import requests
import time
import os
import logging
from dotenv import load_dotenv
from db_handler import cache_weather_data, load_cached_data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'


def fetch_weather(city: str) -> dict | None:
    """Fetch weather data from API or return cached data if API fails."""
    if not API_KEY:
        logging.error("API key not found. Check .env file.")
        return None

    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    retries = 3

    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()  # Raises an error for HTTP errors (4xx, 5xx)

            # Handle invalid responses explicitly
            if response.status_code == 404:
                logging.error(f"City '{city}' not found. Please check the name.")
                return None
            elif response.status_code >= 500:
                logging.warning("Weather service temporarily unavailable. Retrying...")
                time.sleep(2)  # Brief pause before retrying
                continue

            data = response.json()
            cache_weather_data(city, data)  # Save successful response to cache
            return data

        except requests.exceptions.RequestException as e:
            logging.error(f"API Request Failed: {e}")
            if attempt < retries - 1:
                logging.warning(f"Retrying API request for '{city}' (Attempt {attempt+1}/{retries})...")
                time.sleep(2)  # Retry delay
            else:
                logging.error(f"Fetching live data failed for '{city}'. Checking cache...")
                cached_data = load_cached_data(city)
                if cached_data:
                    logging.info(f"Loaded cached data for '{city}'.")
                return cached_data  # Return cached data if available

    return None  # In case all attempts and cache fail
