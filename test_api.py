import requests
import sys
import os

def test_prediction(image_path, crop="Tomato"):
    url = "http://127.0.0.1:5000/predict"
    
    # Handle both relative path from root and direct path
    if not os.path.exists(image_path):
        # Try checking in relative path if run from root
        potential_path = os.path.join("plant_stage_backend", image_path)
        if os.path.exists(potential_path):
            image_path = potential_path
        else:
             # Try checking if run from within plant_stage_backend
             potential_path = os.path.join("test_images", os.path.basename(image_path))
             if os.path.exists(potential_path):
                 image_path = potential_path
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    try:
        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"crop": crop}
            print(f"Sending {image_path} with crop={crop}...")
            response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with the synthetic vegetative image we created earlier
    test_prediction("plant_stage_backend/test_images/tomato_plant(growth predction).jpg", crop="Tomato")
