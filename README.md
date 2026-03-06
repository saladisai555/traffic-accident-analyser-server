# Traffic Accident Analyser - FastAPI Backend

FastAPI application for traffic accident risk prediction.

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB
- Poetry package manager

### Installation

```bash
cd traffic-accident-analyser
pip install poetry
py -3.12 -m venv venv
venv\Scripts\activate

poetry lock
poetry install
```

### Configure

```bash
cp .env .env.bak
# Edit .env with your API keys
```

### Run Server

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server: http://localhost:8000
API Docs: http://localhost:8000/docs

## Project Structure

```
app/
├── main.py              
├── config.py            
├── startup.py           
├── models/
│   ├── user.py          
│   └── prediction.py    
├── database/
│   └── mongo.py         
├── routes/
│   ├── auth.py          
│   ├── predict.py       
│   ├── dashboard.py     
│   └── weather.py       
├── services/
│   ├── model_service.py      
│   ├── weather_service.py    
│   ├── traffic_service.py    
│   └── email_service.py      
├── schemas/
│   ├── auth_schema.py        
│   ├── predict_schema.py     
│   ├── dashboard_schema.py   
│   └── common.py             
└── utils/
    ├── token.py          
    └── mapping.py        

model/
└── model.pkl         
```

## API Endpoints

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`

### Prediction
- `POST /predict/`

### Dashboard
- `POST /dashboard/predict-location`
- `GET /dashboard/hotspots`

### Health
- `GET /health`

## Environment Variables

```
MONGO_URL=mongodb://localhost:27017
MONGO_DB=traffic_db
JWT_SECRET=your-secret-key
OPENWEATHER_API_KEY=your-key
TRAFFIC_API_KEY=your-key
SMTP_USER=your-email
SMTP_PASSWORD=your-password
```

## Dependencies

- FastAPI 0.109.0
- Uvicorn 0.27.0
- Motor 3.3.2
- Pydantic 2.5.3
- python-jose
- passlib
- httpx

## Development

```bash
uv sync --extra dev
uv run black .
uv run ruff check .
uv run mypy app/
```
