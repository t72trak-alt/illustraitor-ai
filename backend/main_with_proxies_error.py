from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import openai
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(
    title="Illustraitor AI API",
    description="API для генерации AI иллюстраций с демо-режимом",
    version="2.2.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class GenerateRequest(BaseModel):
    text: str
    style: str = "creative"
    api_key: Optional[str] = None
STYLES = {
    "fantasy": {"name": "Фэнтези", "prompt": "fantasy art"},
    "minimalist": {"name": "Минимализм", "prompt": "minimalist design"}
}
DEMO_IMAGES = {
    "fantasy": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1024&h=1024&fit=crop",
    "minimalist": "https://images.unsplash.com/photo-1579546929662-711aa81148cf?w=1024&h=1024&fit=crop"
}
@app.get("/health")
def health():
    return {"status": "healthy"}
@app.post("/generate")
def generate_illustration(request: GenerateRequest):
    if request.style not in STYLES:
        raise HTTPException(status_code=400, detail=f"Неверный стиль. Доступные: {list(STYLES.keys())}")
    # Демо-режим
    if not request.api_key:
        return {
            "status": "success",
            "message": f"Демо: иллюстрация в стиле '{STYLES[request.style]['name']}'",
            "image_url": DEMO_IMAGES[request.style],
            "mode": "demo"
        }
    # OpenAI режим - исправленная проверка ключа
    try:
        # Поддержка sk- и sk-proj- ключей
        if not (request.api_key.startswith("sk-") or request.api_key.startswith("sk-proj-")):
            raise HTTPException(status_code=400, detail="Неверный формат OpenAI ключа")
        client = openai.OpenAI(api_key=request.api_key)
        prompt = f"{STYLES[request.style]['prompt']}: {request.text}"
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return {
            "status": "success",
            "message": f"AI иллюстрация в стиле '{STYLES[request.style]['name']}'",
            "image_url": response.data[0].url,
            "mode": "openai"
        }
    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Неверный OpenAI API ключ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка OpenAI: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
