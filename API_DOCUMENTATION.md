# Traffic Accident Analyser API Documentation

Base URL: `http://localhost:8000` (Development)

All protected endpoints require JWT authentication via Bearer token in the Authorization header.

---

## Authentication

### 1. Register User
**POST** `/auth/register`

Register a new user and send OTP to email for verification.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "latitude": 51.5074,
  "longitude": -0.1278
}
```

**Validation:**
- `email`: Valid email format
- `password`: 8-72 characters
- `latitude`: -90 to 90
- `longitude`: -180 to 180

**Response:** `200 OK`
```json
{
  "message": "OTP sent to email. Please verify to complete registration.",
  "email": "user@example.com"
}
```

**Errors:**
- `400`: Email already registered
- `500`: Email sending failed

---

### 2. Verify OTP
**POST** `/auth/verify-otp`

Verify email with OTP code sent during registration.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Email verified successfully. You can now login.",
  "email": "user@example.com"
}
```

**Errors:**
- `400`: Invalid OTP or OTP expired (10 min expiry)
- `404`: No pending verification found

---

### 3. Login
**POST** `/auth/login`

Login with verified email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "email": "user@example.com"
}
```

**Errors:**
- `401`: Invalid credentials
- `403`: Email not verified

---

### 4. Get User Details
**GET** `/auth/me`

Get current authenticated user details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "email": "user@example.com",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "is_verified": true,
  "created_at": "2025-12-11T10:30:00Z"
}
```

**Errors:**
- `401`: Invalid or expired token

---

## Prediction

### 5. Predict Accident Severity
**POST** `/predict/`

Predict accident severity based on location and user inputs. Fetches real-time weather and traffic data.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "latitude": 51.5074,
  "longitude": -0.1278,
  "road_type": "Highway",
  "speed_limit": 100,
  "number_of_vehicles": 3,
  "driver_alcohol": 0,
  "vehicle_type": "Car",
  "driver_age": 28,
  "driver_experience": 5
}
```

**Field Constraints:**
- `latitude`: -90 to 90
- `longitude`: -180 to 180
- `road_type`: "Highway", "City Road", "Rural Road", "Mountain Road"
- `speed_limit`: 0-200 km/h
- `number_of_vehicles`: 1-5
- `driver_alcohol`: 0 (No) or 1 (Yes)
- `vehicle_type`: "Car", "Truck", "Bus", "Motorcycle"
- `driver_age`: 18-70
- `driver_experience`: 0-50 years

**Response:** `200 OK`
```json
{
  "severity": "High",
  "probabilities": {
    "Low": 0.15,
    "Medium": 0.25,
    "High": 0.60
  },
  "confidence": 0.60,
  "weather": {
    "temp": 15.5,
    "weather_main": "Rain",
    "rain_mm": 5.2,
    "humidity": 80,
    "wind_speed": 12.5,
    "feels_like": 13.2,
    "visibility": 8000,
    "pressure": 1013,
    "clouds": 75
  },
  "traffic": {
    "traffic_density": 2,
    "jam_factor": 8.5,
    "current_speed": 25,
    "free_flow_speed": 100,
    "confidence": 0.85,
    "nearby_accidents": 2,
    "source": "here_api"
  },
  "location": {
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "timestamp": "2025-12-11T14:30:00Z"
}
```

**Severity Levels:**
- `Low`: Safe conditions, normal driving
- `Medium`: Moderate risk, increased caution
- `High`: Dangerous conditions, high alert

**Traffic Density:**
- `0`: Low traffic
- `1`: Medium traffic
- `2`: High traffic/congestion

**Traffic Source:**
- `here_api`: Real-time data from HERE Traffic API
- `time_based`: Estimated from time of day (when API unavailable)
- `time_based_fallback`: Fallback after API error

**Errors:**
- `401`: Authentication required
- `422`: Validation error (invalid field values)
- `500`: Prediction failed

---

## Dashboard

### 6. Predict by Location Only
**POST** `/dashboard/predict-location`

Simplified prediction using only location (uses default values for user inputs).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "latitude": 51.5074,
  "longitude": -0.1278
}
```

**Response:** `200 OK`
```json
{
  "risk_level": "medium",
  "risk_probability": 0.45,
  "recommendation": "Exercise caution. Be aware of surroundings and reduce speed slightly.",
  "weather": { /* weather data */ },
  "traffic": { /* traffic data */ },
  "location": {
    "latitude": 51.5074,
    "longitude": -0.1278
  }
}
```

**Errors:**
- `401`: Authentication required
- `500`: Prediction failed

---

### 7. Get Accident Hotspots
**GET** `/dashboard/hotspots`

Get list of accident-prone areas based on historical predictions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "hotspots": [
    {
      "latitude": 51.5074,
      "longitude": -0.1278,
      "severity": "High",
      "count": 15,
      "last_updated": "2025-12-11T12:00:00Z"
    },
    {
      "latitude": 51.5100,
      "longitude": -0.1300,
      "severity": "Medium",
      "count": 8,
      "last_updated": "2025-12-11T11:30:00Z"
    }
  ],
  "total": 2
}
```

**Errors:**
- `401`: Authentication required

---

## Weather API

### 8. Get Weather by Location
**GET** `/weather/?latitude={lat}&longitude={lon}`

Get current weather data for a location (testing endpoint).

**Query Parameters:**
- `latitude`: -90 to 90
- `longitude`: -180 to 180

**Response:** `200 OK`
```json
{
  "temp": 20.5,
  "weather_main": "Clear",
  "rain_mm": 0,
  "humidity": 65,
  "wind_speed": 5.2,
  "feels_like": 19.8,
  "visibility": 10000,
  "pressure": 1015,
  "clouds": 20
}
```

---

## Error Responses

All endpoints may return these error formats:

**400 Bad Request**
```json
{
  "detail": "Email already registered"
}
```

**401 Unauthorized**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden**
```json
{
  "detail": "Email not verified. Please verify your email first."
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "speed_limit"],
      "msg": "ensure this value is less than or equal to 200",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**500 Internal Server Error**
```json
{
  "detail": "Prediction failed: Model error"
}
```

---

## Authentication Flow

1. **Register**: POST `/auth/register` → OTP sent to email
2. **Verify**: POST `/auth/verify-otp` → Email verified
3. **Login**: POST `/auth/login` → Receive JWT token
4. **Use Token**: Add `Authorization: Bearer <token>` header to all protected endpoints

**Token Expiry**: 24 hours

---

## Rate Limits

- No rate limits currently implemented
- Recommended: Cache predictions for same location within 5 minutes

---

## CORS

Allowed origins configured in backend. Default: all origins allowed in development.

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Weather data from OpenWeather API (2.5)
- Traffic data from HERE Traffic API v7 (when available)
- Model predicts based on 13 features including real-time conditions
- Predictions are logged to MongoDB for hotspot analysis
