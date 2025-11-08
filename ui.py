import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import requests
from api_handler import fetch_weather
from db_handler import clear_cache

def setup_ui():
    root = tk.Tk()
    root.title("Weather App")
    root.geometry("400x400")
    root.configure(bg='#87CEEB')

    city_label = tk.Label(root, text="Enter City:", bg='#87CEEB', fg='white')
    city_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    city_entry = tk.Entry(root, width=30)
    city_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    result_label = tk.Label(root, text="", font=("Arial", 12), bg='#87CEEB', fg='white', justify="left")
    result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    icon_label = tk.Label(root, bg='#87CEEB')
    icon_label.grid(row=5, column=0, columnspan=2, pady=10)

    def get_weather_thread():
        """Runs get_weather in a separate thread to avoid UI freezing."""
        thread = threading.Thread(target=get_weather, daemon=True)
        thread.start()

    def get_weather():
        """Fetch weather data asynchronously and update UI."""
        city = city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Required", "Please enter a city name.")
            return
        
        # Fetch data
        data = fetch_weather(city)
        if data:
            root.after(0, lambda: update_ui(data, result_label, icon_label, root))  # UI update in main thread
        else:
            root.after(0, lambda: messagebox.showerror("Error", "No data available."))

    def clear_results():
        """Clears the UI results."""
        city_entry.delete(0, tk.END)
        result_label.config(text="")
        icon_label.config(image=None)  # Correct way to clear an image
        icon_label.image = None   

    get_weather_button = tk.Button(root, text="Get Weather", command=get_weather_thread, bg='#4CAF50', fg='white')
    get_weather_button.grid(row=1, column=0, columnspan=2, pady=10)

    clear_button = tk.Button(root, text="Clear", command=clear_results, bg='#f44336', fg='white')
    clear_button.grid(row=2, column=0, columnspan=2, pady=5)

    clear_cache_button = tk.Button(root, text="Clear Cache", command=clear_cache, bg='#FFC107', fg='white')
    clear_cache_button.grid(row=3, column=0, columnspan=2, pady=5)

    root.mainloop()  # Start the Tkinter event loop

def update_ui(data, result_label, icon_label, root):
    """Updates UI with fetched weather data."""
    weather = data['weather'][0]['description'].capitalize()
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    feels_like = data['main']['feels_like']
    icon_code = data['weather'][0]['icon']

    result_label.config(
        text=f"{weather}\nTemperature: {temp}°C\nFeels Like: {feels_like}°C\n"
             f"Humidity: {humidity}%\nWind Speed: {wind_speed} m/s"
    )

    def fetch_icon():
        try:
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
            icon_img = Image.open(requests.get(icon_url, stream=True).raw)
            icon_img = icon_img.resize((50, 50), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
            root.after(0, lambda: icon_label.config(image=icon_photo))
            icon_label.image = icon_photo  # Keep reference
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Image Error", f"Failed to load weather icon: {e}"))

    # Fetch the icon in a separate thread
    threading.Thread(target=fetch_icon, daemon=True).start()
