from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import openai
from openai.api_resources.image import Image
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
class GenerateRequest(BaseModel):
    text: str
    style: str = "fantasy"
    api_key: Optional[str] = None
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/generate")
def generate(request: GenerateRequest):
    # Демо режим
    if not request.api_key:
        return {
            "status": "success",
            "mode": "demo",
            "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba"
        }
    # OpenAI режим - МАКСИМАЛЬНО ПРОСТОЙ
    try:
        # Только ключ, никаких других параметров
        openai.api_key = request.api_key
        response = Image.create(
            prompt=f"{request.text}",
            size="256x256",
            n=1
        )
        return {
            "status": "success",
            "mode": "openai",
            "image_url": response['data'][0]['url']
        }
    except Exception as e:
        return {
            "status": "error",
            "mode": "error",
            "error": str(e),
            "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba"
        }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



