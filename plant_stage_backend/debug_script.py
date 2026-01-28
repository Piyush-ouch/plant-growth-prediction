import cv2
import numpy as np
from app import preprocess_image, normalize_lighting, get_plant_mask, calculate_green_ratio, predict_stage, CROP_THRESHOLDS

def analyze_image(image_path, crop_name="Onion"):
    print(f"Analyzing {image_path} for crop: {crop_name}")
    
    # Load image manually to simulate file upload read
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    img = preprocess_image(image_bytes)
    if img is None:
        print("Error: Image preprocessing failed (returned None)")
        return

    img = normalize_lighting(img)
    mask = get_plant_mask(img)
    
    # Save debug mask
    cv2.imwrite("debug_test_mask.png", mask)
    print("Saved debug_test_mask.png")
    
    green_ratio = calculate_green_ratio(img, mask)
    print(f"Green Ratio: {green_ratio:.4f}")
    
    stage, ranges = predict_stage(green_ratio, crop_name)
    print(f"Predicted Stage: {stage}")
    print(f"Stage Ranges: {ranges}")

    # Check why it might be unknown
    print("\nRange Check:")
    stages = CROP_THRESHOLDS.get(crop_name)
    if stages:
        for s, (low, high) in stages.items():
            match = low <= green_ratio < high
            print(f"  {s}: [{low}, {high}) -> {match}")
    else:
        print(f"  Crop {crop_name} not found in threshold dictionary")

def test_hsv_ranges(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    img = preprocess_image(image_bytes)
    img = normalize_lighting(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    ranges = [
        ("Original", np.array([35, 40, 40]), np.array([85, 255, 255])),
        ("Wider", np.array([25, 30, 30]), np.array([95, 255, 255])),
        ("Cyan-Heavy", np.array([30, 30, 30]), np.array([100, 255, 255])),
        ("Aggressive", np.array([20, 20, 20]), np.array([100, 255, 255])),
        ("Yellow-Green", np.array([20, 30, 30]), np.array([85, 255, 255])),
    ]

    for name, lower, upper in ranges:
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        ratio = np.count_nonzero(mask) / (img.shape[0] * img.shape[1])
        print(f"HSV Profile '{name}': Ratio = {ratio:.4f}")
        
        # Test what stage this ratio would be for Onion
        stage, _ = predict_stage(ratio, "Onion")
        print(f"  -> Stage: {stage}")


if __name__ == "__main__":
    analyze_image("debug_onion.png", "Onion")
    print("\n--- Testing HSV Ranges ---")
    test_hsv_ranges("debug_onion.png")

