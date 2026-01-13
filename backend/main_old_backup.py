from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import sqlite3
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random

load_dotenv()

app = FastAPI(
    title="Illustraitor AI API",
    description="API для генерации AI иллюстраций с системой кредитов",
    version="2.0.0"
)

# Настройка CORS для продакшена
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели
class GenerateRequest(BaseModel):
    text: str
    style: str = "creative"
    api_key: Optional[str] = None

class BatchGenerateRequest(BaseModel):
    texts: List[str]
    style: str = "creative"
    api_key: Optional[str] = None

class UserRegister(BaseModel):
    email: str
    name: str

# База данных SQLite
def init_db():
    conn = sqlite3.connect('illustraitor.db')
    c = conn.cursor()
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE,
                  name TEXT,
                  api_key TEXT UNIQUE,
                  credits INTEGER DEFAULT 10,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # Таблица генераций
    c.execute('''CREATE TABLE IF NOT EXISTS generations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  text TEXT,
                  style TEXT,
                  image_url TEXT,
                  credits_used INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

init_db()

# Расширенные стили (15 стилей)
STYLES = {
    "business": {
        "name": "Бизнес",
        "prompt": "professional corporate style, clean lines, modern office, professional",
        "credits": 1
    },
    "creative": {
        "name": "Креативный",
        "prompt": "artistic, imaginative, colorful, abstract, creative artwork",
        "credits": 1
    },
    "minimalist": {
        "name": "Минимализм", 
        "prompt": "minimalist design, simple lines, monochrome, clean aesthetics",
        "credits": 1
    },
    "infographic": {
        "name": "Инфографика",
        "prompt": "infographic style, data visualization, charts, icons, informative",
        "credits": 1
    },
    "playful": {
        "name": "Игривый",
        "prompt": "fun, cartoonish, bright colors, playful characters, friendly",
        "credits": 1
    },
    "3d_render": {
        "name": "3D Рендер",
        "prompt": "3D render, Blender style, cinematic lighting, realistic materials",
        "credits": 2
    },
    "watercolor": {
        "name": "Акварель",
        "prompt": "watercolor painting, soft edges, transparent colors, artistic",
        "credits": 2
    },
    "cyberpunk": {
        "name": "Киберпанк",
        "prompt": "cyberpunk aesthetic, neon lights, futuristic, dystopian, night city",
        "credits": 2
    },
    "flat_design": {
        "name": "Плоский дизайн",
        "prompt": "flat design, vector illustration, simple shapes, modern UI",
        "credits": 1
    },
    "oil_painting": {
        "name": "Масляная живопись",
        "prompt": "oil painting style, textured brush strokes, classical art, rich colors",
        "credits": 2
    },
    "pixel_art": {
        "name": "Пиксель-арт",
        "prompt": "pixel art, retro gaming style, 8-bit, nostalgic video game",
        "credits": 1
    },
    "anime": {
        "name": "Аниме",
        "prompt": "anime style, Japanese animation, vibrant colors, expressive characters",
        "credits": 2
    },
    "sketch": {
        "name": "Эскиз",
        "prompt": "sketch drawing, pencil lines, rough draft, artistic sketchbook style",
        "credits": 1
    },
    "vintage": {
        "name": "Винтаж",
        "prompt": "vintage style, retro aesthetic, old photography, nostalgic",
        "credits": 1
    },
    "fantasy": {
        "name": "Фэнтези",
        "prompt": "fantasy art, magical creatures, epic landscapes, mystical",
        "credits": 2
    }
}

# Mock изображения для каждого стиля
MOCK_IMAGES = {
    "business": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop",
    "creative": "https://images.unsplash.com/photo-1542744095-fcf48d80b0fd?w=400&h=300&fit=crop",
    "minimalist": "https://images.unsplash.com/photo-1579546929662-711aa81148cf?w=400&h=300&fit=crop",
    "infographic": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
    "playful": "https://images.unsplash.com/photo-1518834103326-4dbb0d8400de?w=400&h=300&fit=crop",
    "3d_render": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=300&fit=crop",
    "watercolor": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=400&h=300&fit=crop",
    "cyberpunk": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=300&fit=crop",
    "flat_design": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400&h=300&fit=crop",
    "oil_painting": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400&h=300&fit=crop",
    "pixel_art": "https://images.unsplash.com/photo-1534423861386-85a16f5d13fd?w=400&h=300&fit=crop",
    "anime": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop",
    "sketch": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=300&fit=crop",
    "vintage": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=400&h=300&fit=crop",
    "fantasy": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&h=300&fit=crop"
}

# Вспомогательные функции
def get_user_by_api_key(api_key: str):
    """Получить пользователя по API ключу"""
    conn = sqlite3.connect('illustraitor.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
    user = c.fetchone()
    conn.close()
    return user

def use_credits(user_id: int, credits: int):
    """Использовать кредиты пользователя"""
    conn = sqlite3.connect('illustraitor.db')
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits - ? WHERE id = ? AND credits >= ?", 
              (credits, user_id, credits))
    conn.commit()
    success = c.rowcount > 0
    conn.close()
    return success

def log_generation(user_id: int, text: str, style: str, image_url: str, credits_used: int):
    """Записать генерацию в историю"""
    conn = sqlite3.connect('illustraitor.db')
    c = conn.cursor()
    c.execute("INSERT INTO generations (user_id, text, style, image_url, credits_used) VALUES (?, ?, ?, ?, ?)",
              (user_id, text, style, image_url, credits_used))
    conn.commit()
    conn.close()

# Эндпоинты
@app.get("/")
def root():
    return {
        "service": "Illustraitor AI API",
        "version": "2.0.0",
        "status": "running",
        "features": ["15 стилей", "система кредитов", "пакетная генерация", "интеграция с Notion"],
        "endpoints": ["/", "/health", "/styles", "/generate", "/batch-generate", "/register", "/credits"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/styles")
def get_styles():
    """Получить список всех стилей"""
    styles_list = []
    for key, value in STYLES.items():
        styles_list.append({
            "id": key,
            "name": value["name"],
            "credits_cost": value["credits"],
            "description": value["prompt"]
        })
    return {"styles": styles_list, "total": len(styles_list)}

@app.post("/register")
def register(user: UserRegister):
    """Регистрация нового пользователя"""
    api_key = f"ilust_{random.randint(10000, 99999)}_{datetime.now().strftime('%Y%m%d')}"
    conn = sqlite3.connect('illustraitor.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, name, api_key) VALUES (?, ?, ?)",
                  (user.email, user.name, api_key))
        conn.commit()
        user_id = c.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    conn.close()
    return {
        "status": "success",
        "message": "Регистрация успешна",
        "api_key": api_key,
        "credits": 10,
        "user_id": user_id
    }

@app.get("/credits/{api_key}")
def get_credits(api_key: str):
    """Получить количество кредитов"""
    user = get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {
        "credits": user[4],
        "email": user[1],
        "name": user[2]
    }

@app.post("/generate")
def generate_illustration(request: GenerateRequest):
    """Генерация одной иллюстрации"""
    # Проверка стиля
    if request.style not in STYLES:
        raise HTTPException(status_code=400, detail=f"Неверный стиль. Доступные: {list(STYLES.keys())}")
    
    credits_needed = STYLES[request.style]["credits"]
    
    # Проверка API ключа и кредитов
    if request.api_key:
        user = get_user_by_api_key(request.api_key)
        if not user:
            raise HTTPException(status_code=401, detail="Неверный API ключ")
        if user[4] < credits_needed:
            raise HTTPException(status_code=402, detail="Недостаточно кредитов")
        # Используем кредиты
        if not use_credits(user[0], credits_needed):
            raise HTTPException(status_code=402, detail="Ошибка списания кредитов")
    
    # Генерация изображения
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openai-api-key-here" and request.api_key:
        # Режим с OpenAI
        try:
            client = openai.OpenAI(api_key=api_key)
            prompt = f"{STYLES[request.style]['prompt']}: {request.text}"
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fallback на mock
            image_url = MOCK_IMAGES[request.style]
    else:
        # Mock режим
        image_url = MOCK_IMAGES[request.style]
    
    # Логирование если есть API ключ пользователя
    if request.api_key:
        user = get_user_by_api_key(request.api_key)
        log_generation(user[0], request.text, request.style, image_url, credits_needed)
    
    return {
        "status": "success",
        "message": f"Иллюстрация в стиле '{STYLES[request.style]['name']}' сгенерирована",
        "image_url": image_url,
        "text": request.text,
        "style": request.style,
        "style_name": STYLES[request.style]["name"],
        "credits_used": credits_needed if request.api_key else 0,
        "mode": "openai" if api_key and api_key != "your-openai-api-key-here" and request.api_key else "demo"
    }

@app.post("/batch-generate")
def batch_generate_illustrations(request: BatchGenerateRequest):
    """Пакетная генерация иллюстраций"""
    if len(request.texts) > 5:
        raise HTTPException(status_code=400, detail="Максимум 5 изображений за раз")
    
    if request.style not in STYLES:
        raise HTTPException(status_code=400, detail=f"Неверный стиль. Доступные: {list(STYLES.keys())}")
    
    credits_needed = STYLES[request.style]["credits"] * len(request.texts)
    
    # Проверка API ключа и кредитов
    if request.api_key:
        user = get_user_by_api_key(request.api_key)
        if not user:
            raise HTTPException(status_code=401, detail="Неверный API ключ")
        if user[4] < credits_needed:
            raise HTTPException(status_code=402, detail="Недостаточно кредитов")
        # Используем кредиты
        if not use_credits(user[0], credits_needed):
            raise HTTPException(status_code=402, detail="Ошибка списания кредитов")
    
    results = []
    for text in request.texts:
        # Mock генерация (для примера)
        image_url = MOCK_IMAGES[request.style]
        results.append({
            "text": text,
            "image_url": image_url,
            "style": request.style,
            "style_name": STYLES[request.style]["name"]
        })
        # Логирование если есть API ключ пользователя
        if request.api_key:
            user = get_user_by_api_key(request.api_key)
            log_generation(user[0], text, request.style, image_url, STYLES[request.style]["credits"])
    
    return {
        "status": "success",
        "message": f"Сгенерировано {len(results)} изображений",
        "results": results,
        "total_credits_used": credits_needed if request.api_key else 0
    }

# Интеграция с Notion (заглушка для демонстрации)
@app.post("/notion/save")
def save_to_notion(api_key: str, image_url: str, title: str = "AI Illustration"):
    """Сохранение в Notion (демо)"""
    # Здесь будет реальная интеграция с Notion API
    return {
        "status": "success",
        "message": "Интеграция с Notion включена в следующей версии",
        "notion_url": f"https://notion.so/demo-page-{random.randint(1000, 9999)}",
        "title": title,
        "image_url": image_url
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)