import mysql.connector
import logging
import os
from dotenv import load_dotenv
# from tkinter import messagebox  # Uncomment this if using a GUI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}


def connect_to_db() -> mysql.connector.MySQLConnection | None:
    """Connects to MySQL database and returns the connection object."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        logging.error(f"Database Connection Error: {err}")
        return None


def cache_weather_data(city: str, data: dict) -> None:
    """Stores weather data without overwriting old records, keeping historical data."""
    db = connect_to_db()
    if not db:
        return

    cursor = db.cursor()
    try:
        query = """
        INSERT INTO weather_cache 
        (city, weather_description, temperature, feels_like, humidity, wind_speed, icon_code, timestamp) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            city, data['weather'][0]['description'], data['main']['temp'], 
            data['main']['feels_like'], data['main']['humidity'], 
            data['wind']['speed'], data['weather'][0]['icon']
        ))
        db.commit()
    except mysql.connector.Error as err:
        logging.error(f"Error saving data to database: {err}")
        # messagebox.showerror("Database Error", f"Error saving data to database: {err}")  # Uncomment if using GUI
    finally:
        cursor.close()
        db.close()


def load_cached_data(city: str) -> dict | None:
    """Fetches cached weather data if it's less than 10 minutes old."""
    db = connect_to_db()
    if not db:
        return None

    cursor = db.cursor(dictionary=True)
    try:
        query = """
        SELECT * FROM weather_cache 
        WHERE city = %s AND TIMESTAMPDIFF(MINUTE, timestamp, NOW()) < 10
        """
        cursor.execute(query, (city,))
        result = cursor.fetchone()

        if not result:
            logging.info(f"No recent cache available for '{city}'.")
            return None

        return result
    except mysql.connector.Error as err:
        logging.error(f"Database Fetch Error: {err}")
        return None
    finally:
        cursor.close()
        db.close()


def clear_cache() -> None:
    """Clears the weather cache table."""
    db = connect_to_db()
    if not db:
        return

    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM weather_cache")
        db.commit()
        logging.info("Cache cleared successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Cache Clearing Error: {err}")
    finally:
        cursor.close()
        db.close()
