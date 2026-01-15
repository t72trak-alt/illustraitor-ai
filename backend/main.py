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
    description="API для генерации изображений через DALL-E 3 с поддержкой Unsplash",
    version="2.1.0",
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

# ========== МОДЕЛИ ЗАПРОСОВ ==========

class GenerateRequest(BaseModel):
    text: str
    style: str = "fantasy"
    api_key: Optional[str] = None
    unsplash_key: Optional[str] = None  # ⬅️ НОВОЕ ПОЛЕ ДЛЯ UNSPLASH
    size: str = "1024x1024"
    quality: str = "standard"

# ========== СТИЛИ ГЕНЕРАЦИИ ==========

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

# ========== UNSPLASH PROVIDER ==========

class UnsplashProvider:
    """Поиск изображений через Unsplash API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.unsplash.com"
    
    def search_image(self, query: str, style_prompt: str) -> Optional[str]:
        """Ищет релевантное изображение в Unsplash"""
        if not self.api_key:
            return None
        
        try:
            # Комбинируем промпт стиля и запрос пользователя
            search_query = f"{style_prompt} {query}"
            
            headers = {
                "Authorization": f"Client-ID {self.api_key}",
                "Accept-Version": "v1"
            }
            
            params = {
                "query": search_query[:100],  # Ограничиваем длину
                "per_page": 1,
                "orientation": "squarish",
                "content_filter": "high"
            }
            
            response = requests.get(
                f"{self.base_url}/search/photos",
                headers=headers,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    logger.info(f"Unsplash found image for: {search_query}")
                    return data["results"][0]["urls"]["regular"]
            
        except Exception as e:
            logger.warning(f"Unsplash API error: {str(e)[:100]}")
        
        return None

# ========== ДЕМО ИЗОБРАЖЕНИЯ ==========

DEMO_IMAGES = {
    "business": "https://images.unsplash.com/photo-1497366754035-f200968a6e72",
    "creative": "https://images.unsplash.com/photo-1542744095-fcf48d80b0fd",
    "fantasy": "https://images.unsplash.com/photo-1519681393784-d120267933ba",
    "minimalist": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32",
    "cyberpunk": "https://images.unsplash.com/photo-1518709268805-4e9042af2176",
    "watercolor": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5",
    "default": "https://images.unsplash.com/photo-1519681393784-d120267933ba"
}

# ========== КРИТИЧЕСКИ ВАЖНЫЕ ЭНДПОИНТЫ ==========

@app.head("/")
async def head_root():
    """HEAD запрос для Render health checks"""
    return

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Illustraitor AI API v2.1.0</title>
        <style>
            body {{ font-family: Arial; margin: 50px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Illustraitor AI API</h1>
            <p>Версия: 2.1.0 | Статус: ✅ Работает</p>
            <p>Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Поддержка:</strong> OpenAI DALL-E 3 + Unsplash API</p>
            <p><a href="/docs">📖 Swagger документация</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "illustraitor-ai",
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ["openai", "unsplash", "15_styles"]
    })

# ========== ОСНОВНЫЕ ЭНДПОИНТЫ API ==========

@app.get("/styles")
async def get_styles():
    """Получить список всех доступных стилей генерации"""
    styles_list = []
    for key, value in STYLES.items():
        styles_list.append({
            "id": key,
            "name": value["name"],
            "description": value["prompt"],
            "demo_image": DEMO_IMAGES.get(key, DEMO_IMAGES["default"])
        })
    
    return {
        "status": "success",
        "styles": styles_list, 
        "total": len(styles_list),
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Для генерации используйте POST /generate"
    }

@app.post("/generate")
async def generate(request: GenerateRequest):
    """
    Основной эндпоинт генерации изображений
    Поддерживает три режима: 
    - OpenAI (с API ключом)
    - Unsplash демо (с Unsplash ключом)
    - Базовая демо (без ключей)
    """
    start_time = datetime.now()
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(2).hex()}"
    
    logger.info(f"[{request_id}] === НАЧАЛО GENERATE ===")
    logger.info(f"[{request_id}] Текст: {request.text[:50]}...")
    logger.info(f"[{request_id}] Стиль: {request.style}")
    logger.info(f"[{request_id}] OpenAI ключ: {'Да' if request.api_key else 'Нет'}")
    logger.info(f"[{request_id}] Unsplash ключ: {'Да' if request.unsplash_key else 'Нет'}")
    
    # Проверка стиля
    if request.style not in STYLES:
        available_styles = list(STYLES.keys())
        logger.error(f"[{request_id}] Неверный стиль: {request.style}. Доступные: {available_styles}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error": f"Неверный стиль. Доступные: {', '.join(available_styles)}",
                "available_styles": available_styles,
                "request_id": request_id
            }
        )
    
    # Очистка proxy переменных
    proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
    os.environ['NO_PROXY'] = '*'
    
    # ========== РЕЖИМ OPENAI ==========
    if request.api_key:
        logger.info(f"[{request_id}] Режим: OPENAI")
        try:
            client = OpenAI(api_key=request.api_key)
            logger.info(f"[{request_id}] Клиент OpenAI создан успешно")
            
            prompt = f"{STYLES[request.style]['prompt']}: {request.text}"
            logger.info(f"[{request_id}] Формированный промпт: {prompt[:100]}...")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt[:4000],
                size=request.size,
                quality=request.quality,
                n=1,
                style="vivid"
            )
            
            image_url = response.data[0].url
            logger.info(f"[{request_id}] OpenAI успешно: {image_url[:50]}...")
            
            return {
                "status": "success",
                "mode": "openai",
                "image_url": image_url,
                "message": f"AI иллюстрация в стиле '{STYLES[request.style]['name']}'",
                "style": request.style,
                "style_name": STYLES[request.style]["name"],
                "size": request.size,
                "quality": request.quality,
                "generation_time": round((datetime.now() - start_time).total_seconds(), 2),
                "model": "dall-e-3",
                "request_id": request_id,
                "prompt_used": prompt[:200]
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{request_id}] Ошибка OpenAI: {error_msg}")
            
            # При ошибке OpenAI переходим в демо-режим
            logger.info(f"[{request_id}] Переход в демо-режим после ошибки OpenAI")
    
    # ========== ДЕМО РЕЖИМ ==========
    logger.info(f"[{request_id}] Режим: ДЕМО")
    
    # Получаем изображение для демо-режима
    demo_image_url = DEMO_IMAGES.get(request.style, DEMO_IMAGES["default"])
    search_source = "default_fallback"
    
    # Пробуем найти через Unsplash если есть ключ
    if request.unsplash_key:
        unsplash = UnsplashProvider(request.unsplash_key)
        found_image = unsplash.search_image(
            request.text, 
            STYLES[request.style]['prompt']
        )
        
        if found_image:
            demo_image_url = found_image
            search_source = "unsplash"
            logger.info(f"[{request_id}] Используется Unsplash изображение")
        else:
            search_source = "unsplash_fallback"
            logger.info(f"[{request_id}] Unsplash не нашел изображение, используется fallback")
    
    width, height = request.size.split('x')
    
    return {
        "status": "success",
        "mode": "demo",
        "image_url": f"{demo_image_url}?w={width}&h={height}&fit=crop&auto=format",
        "message": f"Демо-режим: иллюстрация в стиле '{STYLES[request.style]['name']}'",
        "style": request.style,
        "style_name": STYLES[request.style]["name"],
        "size": request.size,
        "generation_time": round((datetime.now() - start_time).total_seconds(), 2),
        "request_id": request_id,
        "demo_source": search_source,
        "note": "Для AI генерации укажите ваш OpenAI API ключ"
    }

@app.get("/test-unsplash")
async def test_unsplash(api_key: str):
    """Тестирование Unsplash API ключа"""
    try:
        unsplash = UnsplashProvider(api_key)
        test_url = unsplash.search_image("test", "test")
        
        if test_url:
            return {
                "status": "success",
                "message": "Unsplash API ключ работает",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "warning",
                "message": "Unsplash API ключ принят, но поиск не вернул результатов",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Unsplash API ключ не работает",
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)