import json
import os
import io
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array

BASE_DIR = os.path.dirname(__file__)

_model = None
_class_names = None


def get_model():
    global _model, _class_names
    if _model is None:
        _model = load_model(os.path.join(BASE_DIR, "plant_disease_model.keras"))
        with open(os.path.join(BASE_DIR, "class_names.json")) as f:
            _class_names = json.load(f)
    return _model, _class_names


def predict_disease(image_file):
    model, class_names = get_model()

    if hasattr(image_file, "read"):
        image_bytes = image_file.read()
        image_file = io.BytesIO(image_bytes)

    img = load_img(image_file, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array, verbose=0)
    predicted_idx = np.argmax(predictions, axis=1)[0]
    confidence = float(np.max(predictions))

    return {
        "class_name": class_names[predicted_idx],
        "confidence": confidence,
    }