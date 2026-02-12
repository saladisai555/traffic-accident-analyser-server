Folder Structure (Simple, Clean, Modern, No Extra Stuff)
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── user.py
│   │   └── prediction.py
│   ├── database/
│   │   └── mongo.py
│   ├── routes/
│   │   ├── auth.py          # register, login, logout
│   │   ├── predict.py       # /predict using pipeline.pkl
│   │   ├── dashboard.py     # /predict-location + hotspots
│   │   └── weather.py       # optional direct call pass-through (demo)
│   ├── services/
│   │   ├── model_service.py     # load pipeline, run predict
│   │   ├── weather_service.py   # fetch from OpenWeatherMap
│   │   ├── traffic_service.py   # fetch from HERE/TomTom API
│   │   └── email_service.py     # send alerts (SMTP / SendGrid)
│   ├── schemas/
│   │   ├── auth_schema.py
│   │   ├── predict_schema.py
│   │   ├── dashboard_schema.py
│   │   └── common.py
│   ├── utils/
│   │   ├── mapping.py       # convert weather/traffic to model input fields
│   │   ├── hashing.py       # password hashing
│   │   └── token.py         # JWT handling
│   └── startup.py           # load model on startup
│
├── pipeline/
│   └── pipeline.pkl         # your saved ML model
│
├── requirements.txt
├── .env
└── README.md

🧩 What Each File/Folder Does (short & simple)
main.py

Creates FastAPI app

Includes all routers

Loads model on startup

Reads config (from .env)

config.py

Stores:

Mongo URL

EMAIL settings

WEATHER API key

TRAFFIC API key

JWT secret

MODEL path

Uses pydantic.BaseSettings (modern).

database/mongo.py

One simple MongoDB client using motor (async Mongo).

Expose db.users, db.predictions.

routes/auth.py

Endpoints:

/auth/register

/auth/login

/auth/logout

Uses:

hashing.py for password

token.py for JWT

routes/predict.py

/predict
User manually enters form inputs → send to model_service → return prediction.

routes/dashboard.py

/predict-location
This uses:

weather_service

traffic_service

mapping.py to convert them

model_service to predict

Return: prediction + probability + weather + traffic

/hotspots
Demo static data or from Mongo.

routes/weather.py (OPTIONAL)

Just a pass-through endpoint if you want to debug external API calls.

services/model_service.py

Loads pipeline.pkl once (from /pipeline)

Parses input dict → DataFrame → pipe.predict → return label + probabilities

services/weather_service.py

Sends request to OpenWeatherMap

Return compact JSON:
{ temp, weather_main, rain_mm }

services/traffic_service.py

Same idea but uses HERE/TomTom API.

services/email_service.py

Uses simple Gmail SMTP or SendGrid

One function send_alert_email(to, subject, message)

schemas/*.py

All Pydantic classes (clean typing).
Examples:

RegisterSchema

LoginSchema

PredictInput

PredictOutput

LocationPredictInput

LocationPredictOutput

utils/mapping.py

Convert weather API fields → model’s Weather

Convert traffic API fields → model’s Traffic_Density

Map timezone → Time_of_Day

Rain → Road_Condition

Night/day → Road_Light_Condition

All just pure functions.

pipeline/pipeline.pkl

Drop your trained model here.

FastAPI loads it once.

🪄 Backend Flow (Simple & Clear)
1️⃣ User Flow

Register → Login → Navigate to Prediction → Enter Inputs → Backend → ML Model → Response.

2️⃣ Dashboard Flow

Location → Backend
→ weather_service → OpenWeatherMap
→ traffic_service → HERE/TomTom
→ mapping.py → convert to model-compatible input
→ model_service → predict
→ return: risk + recommendation

3️⃣ If High Risk

email_service → send alert email automatically.

🔌 External APIs Needed

You only need two keys:

OpenWeatherMap API key → for weather

HERE / TomTom Traffic API key → for traffic
(Or you can mock traffic if you want simple demo.)

Both fit easily in .env.

🧱 What You Implement

Since you asked for only structure, here’s your actual to-do list:

A. Create core setup

main.py

config.py

mongo.py

startup.py

B. Implement minimal auth

register/login

store users in Mongo

hash passwords

issue JWT

C. Implement prediction

load model

build one function: predict(data: dict)

D. Implement dashboard

call weather + traffic

map them → full feature dict

use predict

return risk

E. Basic hotspots

Either:

static array, or

store predictions in Mongo and count them around location.

F. Email

One simple SMTP call.

🧩 No extras, No tests, No Redis, No Alembic, No over-engineering

Perfect for a demo, but clean enough that your code looks professional.