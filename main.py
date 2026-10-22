from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import json

from predictive_service import compute_shelf_life_prediction

app = FastAPI(title="FreshEye Predictive API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "model.keras"
model = tf.keras.models.load_model(MODEL_PATH)
with open("class_names.json", "r") as f:
    class_names = json.load(f)

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    fruit_type: str = Form(...),
    storage_condition: str = Form(...)
):
    contents = await file.read()
    tensor = preprocess_image(contents)
    
    predictions = model.predict(tensor)[0]
    pred_idx = np.argmax(predictions)
    label = class_names[pred_idx]
    confidence = float(predictions[pred_idx])

    predictive_metrics = compute_shelf_life_prediction(
        fruit=fruit_type,
        storage=storage_condition,
        visual_label=label,
        confidence_score=confidence
    )

    return {
        "status": "success",
        "fruit": fruit_type,
        "condition": storage_condition,
        "classification": {
            "label": label,
            "confidence": f"{round(confidence * 100, 2)}%"
        },
        "shelf_life_analysis": predictive_metrics
  }
  
