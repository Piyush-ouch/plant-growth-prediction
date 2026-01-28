import cv2
import numpy as np
import os

def create_test_image(filename, green_intensity=200, green_percentage=0.5):
    """
    Creates an image where a certain percentage is green.
    """
    width, height = 512, 512
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Fill background with brown/black (Soil)
    img[:] = [30, 30, 60] # BGR
    
    # Create a green square in the middle to simulate plant
    # Calculate side length needed for the percentage
    total_area = width * height
    target_area = total_area * green_percentage
    side = int(np.sqrt(target_area))
    
    start_x = (width - side) // 2
    start_y = (height - side) // 2
    end_x = start_x + side
    end_y = start_y + side
    
    # Set green pixels (BGR: 20, 200, 20)
    img[start_y:end_y, start_x:end_x] = [20, green_intensity, 20]
    
    output_path = os.path.join("plant_stage_backend/test_images", filename)
    cv2.imwrite(output_path, img)
    print(f"Created {output_path} with approx {green_percentage*100}% green.")

if __name__ == "__main__":
    if not os.path.exists("plant_stage_backend/test_images"):
        os.makedirs("plant_stage_backend/test_images")
        
    # Create a few variations
    create_test_image("seedling.jpg", green_percentage=0.10)
    create_test_image("vegetative.jpg", green_percentage=0.35)
    create_test_image("flowering.jpg", green_percentage=0.50)
    create_test_image("fruiting.jpg", green_percentage=0.60)
    create_test_image("maturity.jpg", green_percentage=0.80)
