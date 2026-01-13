from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import openai
import os
app = FastAPI(title="Illustraitor AI", version="2.0")
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
DEMO_IMAGE = "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1024&h=1024"
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/generate")
def generate(request: GenerateRequest):
    # Всегда демо для простоты
    return {
        "status": "success",
        "mode": "demo",
        "image_url": DEMO_IMAGE,
        "message": "Demo image generated"
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
