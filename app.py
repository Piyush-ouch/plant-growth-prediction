from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

# CROP-WISE GREEN THRESHOLDS
CROP_THRESHOLDS = {
    "Tomato": {
        "Seedling": (0.00, 0.18),
        "Vegetative": (0.18, 0.45),
        "Flowering": (0.45, 0.60),
        "Fruiting": (0.60, 0.75),
        "Maturity": (0.75, 1.00)
    },
    "Wheat": {
        "Seedling": (0.00, 0.12),
        "Vegetative": (0.12, 0.35),
        "Flowering": (0.35, 0.50),
        "Fruiting": (0.50, 0.65),
        "Maturity": (0.65, 1.00)
    },
    "Rice": {
        "Seedling": (0.00, 0.20),
        "Vegetative": (0.20, 0.55),
        "Flowering": (0.55, 0.70),
        "Fruiting": (0.70, 0.85),
        "Maturity": (0.85, 1.00)
    }
}

# IMAGE PREPROCESSING
def preprocess_image(image_bytes):
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        return None

    img = cv2.resize(img, (512, 512))
    return img

# LIGHTING NORMALIZATION (CLAHE)
def normalize_lighting(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)

    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

# BACKGROUND REMOVAL (HSV)
def get_plant_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

# GREEN PROPORTION (PLANT-ONLY)
def calculate_green_ratio(img, mask):
    # Logic Correction: We need "Plant Coverage" (How big is the plant?), not "Plant Greenness" (How green is the mask?).
    # The thresholds (0.15, 0.45...) refer to the percentage of the image covered by the plant.
    
    plant_pixels = np.count_nonzero(mask)
    total_pixels = img.shape[0] * img.shape[1]

    if total_pixels == 0:
        return 0.0

    return plant_pixels / total_pixels

# CONFIDENCE COMPONENTS
# Stage certainty
def stage_certainty(green_ratio, low, high):
    center = (low + high) / 2
    dist = abs(green_ratio - center)
    max_dist = (high - low) / 2

    if max_dist == 0:
        return 0

    score = 1 - (dist / max_dist)
    return max(0, score) * 100

# Plant visibility
def plant_visibility(mask):
    ratio = np.sum(mask > 0) / mask.size

    if ratio < 0.05:
        return 40
    elif ratio < 0.15:
        return 70
    elif ratio < 0.60:
        return 90
    elif ratio < 0.85:
        return 70
    else:
        return 50

# Image sharpness
def image_sharpness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    var = cv2.Laplacian(gray, cv2.CV_64F).var()

    if var < 50:
        return 40
    elif var < 100:
        return 65
    elif var < 200:
        return 80
    else:
        return 95

# FINAL STAGE + CONFIDENCE LOGIC
def predict_stage(green_ratio, crop):
    stages = CROP_THRESHOLDS.get(crop)

    if not stages:
        return "Unknown", (0, 0)

    for stage, (low, high) in stages.items():
        if low <= green_ratio < high:
            return stage, (low, high)

    # Edge case: green_ratio >= 1.0 (though rare with new logic)
    if green_ratio >= 1.0:
        return "Maturity", (0.75, 1.0) # Assume maturity range

    return "Unknown", (0, 1)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Plant Growth Backend is Running",
        "usage": "Send a POST request to /predict with 'image' and 'crop' data."
    })

# FLASK API ENDPOINT
@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files or "crop" not in request.form:
        return jsonify({"error": "Image and crop required"}), 400

    crop = request.form["crop"]
    image_bytes = request.files["image"].read()

    img = preprocess_image(image_bytes)
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    img = normalize_lighting(img)
    mask = get_plant_mask(img)
    
    # Debug images (Optional, can comment out for prod)
    cv2.imwrite("plant_stage_backend/debug_final.png", cv2.bitwise_and(img, img, mask=mask))
    
    green_ratio = calculate_green_ratio(img, mask)

    stage, (low, high) = predict_stage(green_ratio, crop)

    stage_score = stage_certainty(green_ratio, low, high)
    visibility_score = plant_visibility(mask)
    sharpness_score = image_sharpness(img)

    confidence = int(min((stage_score + visibility_score + sharpness_score) / 3, 95))

    return jsonify({
        "crop": crop,
        "growth_stage": stage,
        "green_ratio": round(green_ratio, 3),
        "confidence": confidence
    })

if __name__ == "__main__":
    # host='0.0.0.0' allows access from other devices on the network (like your phone)
    app.run(host='0.0.0.0', port=5000, debug=True)
