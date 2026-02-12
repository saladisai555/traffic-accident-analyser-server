import joblib
import pandas as pd
from pathlib import Path
from app.config import settings

_model = None


def load_model():
    global _model
    ml_model_path = Path(settings.ml_model_path)
    
    if not ml_model_path.exists():
        print(f"Warning: Model not found at {ml_model_path}")
        return None
    
    try:
        _model = joblib.load(ml_model_path)
        print(f"Model loaded from {ml_model_path}")
        return _model
    except Exception as e:
        print(f"Warning: Failed to load model: {e}")
        return None


def get_model():
    global _model
    if _model is None:
        load_model()
    return _model


def predict(features: dict) -> dict:
    model = get_model()
    if model is None:
        return {
            "severity": "Medium",
            "probabilities": {"Low": 0.33, "Medium": 0.34, "High": 0.33},
            "confidence": 0.0,
            "model_available": False
        }
    
    try:
        if "Accident" not in features:
            features["Accident"] = 0
        
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        probabilities = model.predict_proba(df)[0]
        
        severity_labels = ["Low", "Medium", "High"]
        severity = severity_labels[int(prediction)] if int(prediction) < len(severity_labels) else "Medium"
        
        probs_dict = {}
        for i, label in enumerate(severity_labels):
            probs_dict[label] = float(probabilities[i]) if i < len(probabilities) else 0.0
        
        confidence = float(max(probabilities))
        
        return {
            "severity": severity,
            "probabilities": probs_dict,
            "confidence": confidence,
            "model_available": True
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {
            "severity": "Medium",
            "probabilities": {"Low": 0.33, "Medium": 0.34, "High": 0.33},
            "confidence": 0.0,
            "model_available": False
        }


def get_recommendation(risk_level: str) -> str:
    recommendations = {
        "low": "Road conditions are safe. Maintain normal driving habits.",
        "medium": "Exercise caution. Be aware of surroundings and reduce speed slightly.",
        "high": "High risk area. Reduce speed significantly and increase alertness.",
        "critical": "Avoid this area if possible. If unavoidable, drive extremely cautiously.",
    }
    return recommendations.get(risk_level, "Unknown risk level.")