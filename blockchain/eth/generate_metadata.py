import json
import os

def create_metadata(name: str, description: str, image_url: str):
    metadata = {
        "name": name,
        "description": description,
        "image": image_url
    }
    
    os.makedirs("nft_metadata", exist_ok=True)
    filename = f"nft_metadata/nft_{name}.json"
    
    with open(filename, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Сохранено: {filename}")
    return filename
