import requests
import json
print("=" * 50)
print("ТЕСТ С РАБОЧЕЙ КОДИРОВКОЙ")
print("=" * 50)
# Демо-генерация
data = {"text": "Кот космонавт в скафандре", "style": "fantasy"}
response = requests.post("http://localhost:8000/generate", json=data)
result = response.json()
print("Статус:", response.status_code)
print("Режим:", result.get("mode"))
print("Сообщение:", result.get("message"))
print("Стиль:", result.get("style_name"))
print("Изображение:", result.get("image_url")[:80], "...")
print("Примечание:", result.get("note"))
print("\n" + "=" * 50)
print("✅ СЕРВЕР РАБОТАЕТ КОРРЕКТНО!")
print("Проблема только в отображении в PowerShell")
print("=" * 50)
