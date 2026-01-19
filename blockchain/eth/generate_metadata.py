import json
import os

def create_metadata(name: str, description: str, image_url: str, token_id: int):
    metadata = {
        "name": name,
        "description": description,
        "image": image_url
    }
    
    os.makedirs("metadata", exist_ok=True)
    filename = f"metadata/nft_{token_id}.json"
    
    with open(filename, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Сохранено: {filename}")
    return filename
