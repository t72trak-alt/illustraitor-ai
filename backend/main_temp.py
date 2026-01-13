from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import openai
import os
from dotenv import load_dotenv
import random
load_dotenv()
app = FastAPI(
    default_response_class=ORJSONResponse,
    title="Illustraitor AI API",
    description="API для генерации AI иллюстраций с демо-режимом",
    version="2.1.0"
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
    api_key: Optional[str] = None  # OpenAI ключ пользователя
# Стили (15 вариантов)
STYLES = {
    "business": {"name": "Бизнес", "prompt": "professional corporate style, clean lines, modern"},
    "creative": {"name": "Креативный", "prompt": "artistic, imaginative, colorful, abstract"},
    "minimalist": {"name": "Минимализм", "prompt": "minimalist design, simple lines, monochrome"},
    "infographic": {"name": "Инфографика", "prompt": "infographic style, data visualization"},
    "playful": {"name": "Игривый", "prompt": "fun, cartoonish, bright colors, friendly"},
    "3d_render": {"name": "3D Рендер", "prompt": "3D render, Blender style, cinematic lighting"},
    "watercolor": {"name": "Акварель", "prompt": "watercolor painting, soft edges, artistic"},
    "cyberpunk": {"name": "Киберпанк", "prompt": "cyberpunk aesthetic, neon lights, futuristic"},
    "flat_design": {"name": "Плоский дизайн", "prompt": "flat design, vector illustration"},
    "oil_painting": {"name": "Масляная живопись", "prompt": "oil painting style, textured brush strokes"},
    "pixel_art": {"name": "Пиксель-арт", "prompt": "pixel art, retro gaming style, 8-bit"},
    "anime": {"name": "Аниме", "prompt": "anime style, Japanese animation, vibrant colors"},
    "sketch": {"name": "Эскиз", "prompt": "sketch drawing, pencil lines, artistic"},
    "vintage": {"name": "Винтаж", "prompt": "vintage style, retro aesthetic, nostalgic"},
    "fantasy": {"name": "Фэнтези", "prompt": "fantasy art, magical creatures, mystical"}
}
# Демо-изображения (Unsplash для каждого стиля)
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
@app.get("/")
def root():
    return {
        "service": "Illustraitor AI API",
        "version": "2.1.0",
        "status": "running",
        "modes": ["demo (без ключа)", "openai (с вашим ключом)"],
        "styles": list(STYLES.keys())
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
    """Генерация иллюстрации"""
    # Проверка стиля
    if request.style not in STYLES:
        raise HTTPException(status_code=400, detail=f"Неверный стиль. Доступные: {list(STYLES.keys())}")
    # ДЕМО-РЕЖИМ: если нет ключа или ключ 'demo'
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
    # OPENAI РЕЖИМ: есть ключ пользователя
    try:
        # Проверяем что ключ похож на OpenAI ключ (начинается с sk-)
        if not request.api_key.startswith("sk-"):
            raise HTTPException(status_code=400, detail="Неверный формат OpenAI ключа. Ключ должен начинаться с 'sk-'")
        # Генерация через OpenAI
        client = openai.OpenAI(api_key=request.api_key)
        prompt = f"{STYLES[request.style]['prompt']}: {request.text}"
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return {
            "status": "success",
            "message": f"AI иллюстрация в стиле '{STYLES[request.style]['name']}'",
            "image_url": image_url,
            "text": request.text,
            "style": request.style,
            "style_name": STYLES[request.style]["name"],
            "mode": "openai",
            "note": "Сгенерировано через OpenAI DALL-E 3"
        }
    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Неверный OpenAI API ключ. Проверьте ключ.")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="Превышен лимит OpenAI. Попробуйте позже.")
    except openai.APIConnectionError:
        raise HTTPException(status_code=503, detail="Ошибка соединения с OpenAI. Проверьте интернет.")
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback на демо в случае других ошибок
        return {
            "status": "success",
            "message": f"Демо (ошибка OpenAI): {str(e)[:100]}",
            "image_url": DEMO_IMAGES[request.style],
            "mode": "demo_fallback",
            "error": str(e)[:200]
        }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

