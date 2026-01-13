import requests
import json
# Демо-тест
print("=== ДЕМО ТЕСТ ===")
response = requests.post("http://localhost:8000/generate", 
    json={"text": "Тестовый кот", "style": "fantasy"})
data = response.json()
print(f"Статус: {response.status_code}")
print(f"Режим: {data.get('mode')}")
print(f"Сообщение: {data.get('message')}")
print(f"URL: {data.get('image_url')}")
# Стили
print("\n=== СТИЛИ ===")
styles = requests.get("http://localhost:8000/styles").json()
for style in styles['styles'][:3]:
    print(f"{style['id']}: {style['name']}")
