from datetime import datetime, timedelta

BASELINE_SHELF_LIFE = {
    "apple": {"room_temp": 7, "refrigerator": 28},
    "banana": {"room_temp": 4, "refrigerator": 7},
    "orange": {"room_temp": 10, "refrigerator": 21}
}

def compute_shelf_life_prediction(fruit: str, storage: str, visual_label: str, confidence_score: float):
    fruit_key = fruit.lower()
    storage_key = "refrigerator" if "fridge" in storage.lower() or "refrigerat" in storage.lower() else "room_temp"
    
    if fruit_key not in BASELINE_SHELF_LIFE:
        raise ValueError(f"Unsupported fruit type: {fruit}")
        
    max_days = BASELINE_SHELF_LIFE[fruit_key][storage_key]
    
    if visual_label.lower() == "rotten":
        remaining_days_min = 0
        remaining_days_max = 0
        recommendation = "Discard immediately. Visible decay, mold, or breakdown detected."
        risk_level = "High"
    else:
        vitality_factor = max(0.2, (confidence_score - 0.5) / 0.5)
        expected_days = round(max_days * vitality_factor, 1)
        remaining_days_min = max(1, int(expected_days * 0.75))
        remaining_days_max = max(remaining_days_min, int(expected_days * 1.25))
        
        if remaining_days_min <= 2:
            recommendation = "Consume soon; visible signs indicate near-peak ripeness."
            risk_level = "Moderate"
        else:
            recommendation = f"Optimal condition. Store at recommended {storage_key.replace('_', ' ')}."
            risk_level = "Low"

    eat_by_date = (datetime.now() + timedelta(days=remaining_days_max)).strftime("%Y-%m-%d")

    return {
        "estimated_days_remaining": {
            "min": remaining_days_min,
            "max": remaining_days_max,
            "display": f"{remaining_days_min}-{remaining_days_max} days" if remaining_days_min != remaining_days_max else f"{remaining_days_min} days"
        },
        "eat_by_date": eat_by_date,
        "risk_level": risk_level,
        "action_recommendation": recommendation
      }
  
