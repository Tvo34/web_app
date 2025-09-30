import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
import psycopg2

app = FastAPI(title="Local Weather Tracker")

def get_connection():
    """Return a connection to PostgreSQL database."""
    return psycopg2.connect(
        dbname="weatherdb",
        user="jennie",   
        password="",    
        host="localhost",
        port=5432
    )


def fetch_weather(city: str, country: str):
    """Get live weather data for a city using Open-Meteo API."""
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = requests.get(geo_url, params={"name": city, "count": 1})
    geo_data = geo_resp.json()

    if "results" not in geo_data or not geo_data["results"]:
        return None

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_resp = requests.get(
        weather_url,
        params={"latitude": lat, "longitude": lon, "current_weather": "true"}
    )
    weather_data = weather_resp.json()["current_weather"]

    time_obj = datetime.fromisoformat(weather_data["time"].replace("Z", "+00:00"))

    return {
        "city": city,
        "country": country,
        "latitude": lat,
        "longitude": lon,
        "temperature_c": weather_data["temperature"],
        "windspeed_kmh": weather_data["windspeed"],
        "observation_time": time_obj.isoformat(),
        "notes": None
    }


@app.post("/ingest")
def ingest_weather(city: str, country: str):
    """Fetch weather for a city, save it into PostgreSQL, and return the record."""
    weather = fetch_weather(city, country)
    if not weather:
        raise HTTPException(status_code=404, detail="City not found")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO observations (city, country, latitude, longitude, temperature_c, windspeed_kmh, observation_time, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (weather["city"], weather["country"], weather["latitude"], weather["longitude"],
          weather["temperature_c"], weather["windspeed_kmh"], weather["observation_time"], weather["notes"]))
    obs_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    weather["id"] = obs_id
    return weather

@app.get("/observations")
def list_observations():
    """Retrieve all stored observations."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM observations")
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "city": row[1],
            "country": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "temperature_c": row[5],
            "windspeed_kmh": row[6],
            "observation_time": row[7],
            "notes": row[8]
        })
    return results

@app.get("/observations/{obs_id}")
def get_observation(obs_id: int):
    """Retrieve a specific observation by ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM observations WHERE id = %s", (obs_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Observation not found")

    return {
        "id": row[0],
        "city": row[1],
        "country": row[2],
        "latitude": row[3],
        "longitude": row[4],
        "temperature_c": row[5],
        "windspeed_kmh": row[6],
        "observation_time": row[7],
        "notes": row[8]
    }

@app.put("/observations/{obs_id}")
def update_observation(obs_id: int, notes: str):
    """Update the notes field of an observation by ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE observations SET notes = %s WHERE id = %s", (notes, obs_id))
    conn.commit()
    updated = cur.rowcount
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Observation not found")

    return {"id": obs_id, "notes": notes}

@app.delete("/observations/{obs_id}")
def delete_observation(obs_id: int):
    """Delete an observation by ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM observations WHERE id = %s", (obs_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Observation not found")

    return {"deleted": obs_id}
