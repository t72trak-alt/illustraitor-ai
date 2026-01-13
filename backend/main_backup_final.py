from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from typing import Optional
import openai
import os
from dotenv import load_dotenv
import json
load_dotenv()
app = FastAPI(
    title="Illustraitor AI API",
    description="API для генерации AI иллюстраций с демо-режимом",
    version="2.1.0",
    default_response_class=ORJSONResponse
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
# Стили с русскими названиями (правильная кодировка)
STYLES = {
    "business": {"name": "Бизнес", "prompt": "professional corporate style"},
    "creative": {"name": "Креативный", "prompt": "artistic, imaginative"},
    "minimalist": {"name": "Минимализм", "prompt": "minimalist design"},
    "infographic": {"name": "Инфографика", "prompt": "infographic style"},
    "playful": {"name": "Игривый", "prompt": "fun, cartoonish"},
    "3d_render": {"name": "3D Рендер", "prompt": "3D render"},
    "watercolor": {"name": "Акварель", "prompt": "watercolor painting"},
    "cyberpunk": {"name": "Киберпанк", "prompt": "cyberpunk aesthetic"},
    "flat_design": {"name": "Плоский дизайн", "prompt": "flat design"},
    "oil_painting": {"name": "Масляная живопись", "prompt": "oil painting"},
    "pixel_art": {"name": "Пиксель-арт", "prompt": "pixel art"},
    "anime": {"name": "Аниме", "prompt": "anime style"},
    "sketch": {"name": "Эскиз", "prompt": "sketch drawing"},
    "vintage": {"name": "Винтаж", "prompt": "vintage style"},
    "fantasy": {"name": "Фэнтези", "prompt": "fantasy art"}
}
DEMO_IMAGES = {
    "business": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1024&h=1024&fit=crop",
    "creative": "https://images.unsplash.com/photo-1542744095-fcf48d80b0fd?w=1024&h=1024&fit=crop",
    "minimalist": "https://images.unsplash.com/photo-1579546929662-711aa81148cf?w=1024&h=1024&fit=crop",
    "infographic": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1024&h=1024&fit=crop",
    "playful": "https://images.unsplash.com/photo-1518834103326-4dbb0d8400de?w=1024&h=1024&fit=crop",
    "3d_render": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1024&h=1024&fit=crop",
    "watercolor": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=1024&h=1024&fit=crop",
    "cyberpunk": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1024&h=1024&fit=crop",
    "flat_design": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=1024&h=1024&fit=crop",
    "oil_painting": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=1024&h=1024&fit=crop",
    "pixel_art": "https://images.unsplash.com/photo-1534423861386-85a16f5d13fd?w=1024&h=1024&fit=crop",
    "anime": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1024&h=1024&fit=crop",
    "sketch": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=1024&h=1024&fit=crop",
    "vintage": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=1024&h=1024&fit=crop",
    "fantasy": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1024&h=1024&fit=crop"
}
@app.get("/health")
def health():
    return {"status": "healthy"}
@app.get("/styles")
def get_styles():
    styles_list = []
    for key, value in STYLES.items():
        styles_list.append({
            "id": key,
            "name": value["name"],
            "description": value["prompt"]
        })
    return {"styles": styles_list, "total": len(styles_list)}
@app.post("/generate")
def generate_illustration(request: GenerateRequest):
    if request.style not in STYLES:
        raise HTTPException(status_code=400, detail=f"Неверный стиль. Доступные: {list(STYLES.keys())}")
    # Демо-режим
    if not request.api_key or request.api_key.lower() == "demo":
        return {
            "status": "success",
            "message": f"Демо: иллюстрация в стиле '{STYLES[request.style]['name']}'",
            "image_url": DEMO_IMAGES[request.style],
            "text": request.text,
            "style": request.style,
            "style_name": STYLES[request.style]["name"],
            "mode": "demo",
            "note": "Используется демо-изображение. Для AI генерации укажите OpenAI API ключ."
        }
    # OpenAI режим
    try:
        if not request.api_key.startswith("sk-"):
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
            "text": request.text,
            "style": request.style,
            "style_name": STYLES[request.style]["name"],
            "mode": "openai"
        }
    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Неверный OpenAI API ключ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
