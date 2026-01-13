import requests
import json
KEY = "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"
print("=" * 50)
print("ТЕСТ СУПЕР-ЧИСТОЙ ВЕРСИИ СЕРВЕРА")
print("=" * 50)
# Тест 1: Демо (без ключа)
print("\n1. Демо тест (без ключа):")
try:
    r1 = requests.post('http://localhost:8000/generate', json={'text':'test'})
    print(f"   Status: {r1.status_code}")
    data1 = r1.json()
    print(f"   Mode: {data1.get('mode')}")
except Exception as e:
    print(f"   Ошибка: {e}")
# Тест 2: OpenAI (с ключом)
print("\n2. OpenAI тест (с ключом):")
try:
    r2 = requests.post('http://localhost:8000/generate', 
        json={'text':'A simple red apple', 'api_key':KEY},
        timeout=60)
    print(f"   Status: {r2.status_code}")
    if r2.status_code == 200:
        data2 = r2.json()
        print(f"   Mode: {data2.get('mode')}")
        url = data2.get('image_url', '')
        if url:
            print(f"   URL: {url[:80]}...")
            if 'oaidalleapi' in url:
                print("   🎉 УСПЕХ! Реальное OpenAI изображение!")
            elif 'unsplash' in url:
                print("   ⚠️ Всё ещё демо (Unsplash)")
        else:
            print("   Нет URL в ответе")
    else:
        print(f"   Error response: {r2.text[:200]}")
except Exception as e:
    print(f"   Исключение: {e}")
print("\n" + "=" * 50)
