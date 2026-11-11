import os
import requests
import glob
from crewai.tools import tool

def limpiar_directorio_temp():
    """Cleans all files from temp directory"""
    try:
        if os.path.exists("temp"):
            files = glob.glob(os.path.join("temp", "*"))
            for f in files:
                try:
                    os.remove(f)
                    print(f"File deleted: {f}")
                except Exception as e:
                    print(f"Error deleting {f}: {e}")
        else:
            os.makedirs("temp")
            print("Temp directory created")
    except Exception as e:
        print(f"Error cleaning temp directory: {e}")

def _buscar_imagen_base(topic: str) -> str:
    """Base function to search and download image"""
    try:
        limpiar_directorio_temp()
        SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
        
        if not SERPER_API_KEY:
            print("Error: SERPER_API_KEY not configured")
            return "Error: API key not configured"

        url = "https://google.serper.dev/images"
        payload = {
            "q": f"{topic} scientific research academic illustration high quality",
            "gl": "en",
            "hl": "en"
        }

        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        print(f"Searching image for: {topic}")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        image_results = response.json()
        
        if 'images' in image_results and image_results['images']:
            for img_data in image_results['images'][:5]:
                image_url = img_data.get('imageUrl')
                if not image_url:
                    continue
                
                try:
                    print(f"Downloading image from: {image_url}")
                    img_response = requests.get(image_url, timeout=10, stream=True)
                    img_response.raise_for_status()
                    
                    content_type = img_response.headers.get('Content-Type')
                    if content_type and 'image/jpeg' in content_type:
                        ext = '.jpg'
                    elif content_type and 'image/png' in content_type:
                        ext = '.png'
                    else:
                        ext = '.jpg'
                    
                    image_path = os.path.join("temp", f"cover_image{ext}")
                    
                    with open(image_path, 'wb') as f:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"Image downloaded: {image_path}")
                    return f"Image downloaded to {image_path}"
                    
                except Exception as e:
                    print(f"Error downloading image: {e}")
                    continue
            
            return "Could not download any valid image"
        else:
            return "No images found"
            
    except Exception as e:
        print(f"Error in image search: {e}")
        return f"Error: {e}"

@tool("ImageSearchTool")
def buscar_imagen_destino(scientific_topic: str) -> str:
    """Searches for an image related to the scientific topic to use as cover."""
    return _buscar_imagen_base(scientific_topic)
