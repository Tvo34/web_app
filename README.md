# Local Weather Tracker
A simple aplication to track the local weather from the Open-Meteo API
## Getting Started

Follow these steps to run the project locally:

1. Clone repository
   ```bash
   git clone https://github.com/your-username/web_app.git
   cd web_app
   
2. Set up the virtual environment
   ```bash
   python3 -m venv .venv

   source .venv/bin/activate

4. Install dependencies
   ```bash
   pip install -r requirements.txt

6. Set up PostgreSQL
- install PostgreSQL
- Create a database:
   ```bash
   CREATE DATABASE weatherdb;

   CREATE TABLE observations (
    id SERIAL PRIMARY KEY,
    city TEXT,
    country TEXT,
    latitude REAL,
    longitude REAL,
    temperature_c REAL,
    windspeed_kmh REAL,
    observation_time TIMESTAMP,
    notes TEXT
);

5. Run the server
   ```bash
   uvicorn finalproject_CSIS_LamVo:app --reload --port 8001

7. Open the app in your browser
root URL: http://127.0.0.1:8001
Swagger UI docs: http://127.0.0.1:8001/docs

### What the project does
- Fetches live weather data (temperature, windspeed, time) for a specific city.
- Stores the weather observation into PostgreSQL.
- Provides endpoints to: Create a new weather observation (POST /ingest), Read all or one observation (GET /observations, GET /observations/{id}), Update notes for an observation (PUT /observations/{id}), Delete an observation (DELETE /observations/{id}).

### Author
Lam Hoai Trung Vo 
North Park University_CSIS 1230
