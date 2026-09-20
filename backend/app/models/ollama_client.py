import aiohttp
import os
import json

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

async def generate(model: str, prompt: str, image_base64: str = None) -> str:
    """
    Async wrapper for Ollama generate API.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    
    if image_base64:
        payload["images"] = [image_base64]
        
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("response", "")
            else:
                error_text = await response.text()
                raise Exception(f"Ollama API Error: {response.status} - {error_text}")
