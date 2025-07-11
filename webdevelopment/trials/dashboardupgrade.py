from flask import Blueprint, jsonify
import json
import os
import time

dashboard_bp = Blueprint("dashboard", __name__)

# File to store the last known data
DATA_FILE = "last_data.json"

# Function to load the last known data
def load_last_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "time": [],
        "temperature": [[] for _ in range(6)],
        "humidity": [[] for _ in range(6)],
        "soil_moisture": [[] for _ in range(4)]
    }

# Function to save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Global variable to store last known data
last_data = load_last_data()
last_update_time = time.time()

@dashboard_bp.route("/data")
def get_data():
    global last_data, last_update_time

    new_data = fetch_sensor_data()  # Replace this with your actual function

    if new_data:  # If there's new data, update the stored data
        last_data = new_data
        last_update_time = time.time()
        save_data(last_data)  # Save updated data

    return jsonify(last_data)

def fetch_sensor_data():
    """
    Simulates getting new sensor data.
    Replace this with your actual function that gets data from sensors.
    Returns None if no new data.
    """
    # Simulated condition where sometimes no new data arrives
    if time.time() - last_update_time < 10:  # Assume no new data within 10 sec
        return None  

    # Simulated new data (Replace with real sensor data fetching)
    return {
        "time": ["2025-02-22 12:00:00"],  # Add real timestamp
        "temperature": [[22.3, 22.5, 22.7, 22.6, 22.8, 22.9]],
        "humidity": [[50, 51, 49, 48, 52, 50]],
        "soil_moisture": [[30, 32, 29, 31]]
    }
