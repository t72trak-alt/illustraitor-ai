from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
import logging
from datetime import datetime
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Illustraitor AI API",
    description="API для генерации изображений через DALL-E 3",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    style: str = "fantasy"
    api_key: Optional[str] = None
    size: str = "1024x1024"
    quality: str = "standard"

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

DEMO_IMAGES = {
    "business": "https://images.unsplash.com/photo-1497366754035-f200968a6e72",
    "creative": "https://images.unsplash.com/photo-1542744095-fcf48d80b0fd",
    "fantasy": "https://images.unsplash.com/photo-1519681393784-d120267933ba",
    "default": "https://images.unsplash.com/photo-1519681393784-d120267933ba"
}

# ========== КРИТИЧЕСКИ ВАЖНЫЕ ЭНДПОИНТЫ ==========

@app.head("/")
async def head_root():
    """HEAD запрос для Render health checks"""
    return

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(f"""
    <html>
        <body>
            <h1>Illustraitor AI API v2.0</h1>
            <p>✅ Server is running</p>
            <p>{datetime.now()}</p>
            <p><a href="/docs">📖 Swagger</a></p>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "illustraitor-ai"
    })

@app.get("/styles")
async def get_styles():
    styles_list = []
    for key, value in STYLES.items():
        styles_list.append({
            "id": key,
            "name": value["name"],
            "description": value["prompt"]
        })
    return {"styles": styles_list, "total": len(styles_list)}

@app.post("/generate")
async def generate(request: GenerateRequest):
    if not request.api_key:
        return {
            "status": "success",
            "mode": "demo",
            "image_url": DEMO_IMAGES.get(request.style, DEMO_IMAGES["default"]),
            "message": f"Демо: стиль '{STYLES[request.style]['name']}'"
        }
    
    try:
        client = OpenAI(api_key=request.api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"{STYLES[request.style]['prompt']}: {request.text}",
            size=request.size,
            quality=request.quality,
            n=1
        )
        return {
            "status": "success",
            "mode": "openai",
            "image_url": response.data[0].url,
            "message": f"AI иллюстрация в стиле '{STYLES[request.style]['name']}'"
        }
    except Exception as e:
        return {
            "status": "success",
            "mode": "fallback",
            "image_url": DEMO_IMAGES.get(request.style, DEMO_IMAGES["default"]),
            "message": "Ошибка, используется демо-изображение",
            "error": str(e)[:200]
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
