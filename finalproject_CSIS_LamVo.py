import requests
from datetime import datetime


class Observation:
    """
    A weather observation record.
    
    Attributes:
        id (int): Auto-incremented observation ID.
        city (str): City name.
        country (str): Country name.
        latitude (float): Latitude of the city.
        longitude (float): Longitude of the city.
        temperature_c (float): Current temperature in Celsius.
        windspeed_kmh (float): Current wind speed in km/h.
        observation_time (datetime): Observation timestamp.
        notes (str, optional): User notes about the observation.
    """

    def __init__(self, obs_id, city, country, latitude, longitude, temp, windspeed, time, notes=None):
        self.id = obs_id
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.temperature_c = temp
        self.windspeed_kmh = windspeed
        self.observation_time = time  
        self.notes = notes

    def __str__(self):
        """Return a human-readable string representation of the observation."""
        note_text = self.notes if self.notes else "No notes"
        return (f"[{self.id}] {self.city}, {self.country} | "
                f"{self.temperature_c}°C, {self.windspeed_kmh} km/h | "
                f"{self.observation_time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"Notes: {note_text}")


observations = []  
next_id = 1        


def fetch_weather(city, country):
    """
    Fetch live weather data from the Open-Meteo API.
    
    Args:
        city (str): City name.
        country (str): Country name.
    
    Returns:
        tuple: (latitude, longitude, temperature, windspeed, datetime object)
               or None if the city is not found.
    """
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = requests.get(geo_url, params={"name": city, "count": 1})
    geo_data = geo_resp.json()

    if "results" not in geo_data or not geo_data["results"]:
        print("City not found.")
        return None

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_resp = requests.get(
        weather_url, params={"latitude": lat, "longitude": lon, "current_weather": "true"}
    )
    weather_data = weather_resp.json()["current_weather"]

    time_obj = datetime.fromisoformat(weather_data["time"].replace("Z", "+00:00"))

    return lat, lon, weather_data["temperature"], weather_data["windspeed"], time_obj


def add_observation(city, country):
    """Create a new observation by calling the weather API."""
    global next_id
    data = fetch_weather(city, country)
    if not data:
        return
    lat, lon, temp, wind, time = data
    obs = Observation(next_id, city, country, lat, lon, temp, wind, time)
    observations.append(obs)
    print(f"Added observation: {obs}")
    next_id += 1


def list_observations():
    """Display all stored observations."""
    if not observations:
        print("No observations available.")
    for obs in observations:
        print(obs)


def update_observation_note(obs_id, note):
    """Update the notes field of an observation by ID."""
    for obs in observations:
        if obs.id == obs_id:
            obs.notes = note
            print(f"Note updated for observation {obs_id}.")
            return
    print("Observation ID not found.")


def delete_observation(obs_id):
    """Delete an observation by ID."""
    global observations
    observations = [obs for obs in observations if obs.id != obs_id]
    print(f"Observation {obs_id} deleted.")


def menu():
    """Console menu for interacting with the Local Weather Tracker."""
    print("Welcome to Local Weather Tracker")
    while True:
        print("\n--- MENU ---")
        print("1. Add new observation")
        print("2. List all observations")
        print("3. Update an observation note")
        print("4. Delete an observation")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            city = input("Enter city: ")
            country = input("Enter country: ")
            add_observation(city, country)
        elif choice == "2":
            list_observations()
        elif choice == "3":
            obs_id = int(input("Enter observation ID: "))
            note = input("Enter new note: ")
            update_observation_note(obs_id, note)
        elif choice == "4":
            obs_id = int(input("Enter observation ID to delete: "))
            delete_observation(obs_id)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()
