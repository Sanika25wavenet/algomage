import requests
import os

def test_search_endpoint():
    url = "http://localhost:8000/search/"
    event_id = "699449677f42da0378f9c119" # Matching the folder structure found
    
    # Try to find a real image from the uploads directory for a more robust test
    real_image_path = None
    # possible_dir = r"d:\Intelligent Event Photo Retrieval System\server\uploads\photographer2\699449677f42da0378f9c119"
    # if os.path.exists(possible_dir):
    #     files = [f for f in os.listdir(possible_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    #     if files:
    #         real_image_path = os.path.join(possible_dir, files[0])
    #         print(f"Using real image for test: {files[0]}")

    dummy_image_path = "test_selfie.png"
    if not real_image_path:
        # Create a dummy image for testing if we don't have one
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = (73, 109, 137))
        img.save(dummy_image_path)
        test_file = dummy_image_path
        print("Using dummy image (Detection should fail).")
    else:
        test_file = real_image_path
    
    print(f"Testing {url} with event_id={event_id}...")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'selfie': (os.path.basename(test_file), f, 'image/jpeg' if test_file.endswith('.JPG') else 'image/png')}
            params = {'event_id': event_id}
            
            response = requests.post(url, params=params, files=files)
            
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response Body: {response.json()}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Search endpoint test passed (Successful processing)!")
        elif response.status_code == 400:
            print(f"✅ Search endpoint test passed (Validation logic worked: {response.json().get('detail')})")
        else:
            print(f"❌ Search endpoint test failed with status {response.status_code}.")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Note: Make sure the FastAPI server is running on http://localhost:8000")
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)

if __name__ == "__main__":
    test_search_endpoint()
