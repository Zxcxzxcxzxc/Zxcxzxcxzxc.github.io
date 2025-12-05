import json
import requests
import re
from openai import OpenAI
from urllib.parse import quote_plus

client = OpenAI(api_key='sk-9c4f6721a8a2421bb6e6f5168e4daf5e', base_url="https://api.deepseek.com")
MODEL_NAME = 'deepseek-chat'

SYSTEM_PROMPT = """
Ти — експерт з підбору ноутбуків для комп’ютерних ігор.

Твоє завдання:
1. За назвою гри та параметрами визначити мінімальні та рекомендовані системні вимоги.
2. Запропонувати 3–5 ноутбуків, які підійдуть для гри.
3. Всі ціни — у гривнях.
4. НЕ використовуй коментарі, описи, пояснення. Тільки факти.
5. Відповідь — СТРОГО у форматі JSON без жодного тексту поза JSON.
6. НЕ використовуй <think>, ```json, або інший службовий текст.

Формат відповіді:
{
  "game": "назва гри",
  "requirements": {
    "min": {
      "cpu": "",
      "gpu": "",
      "ram_gb": 0,
      "storage_gb": 0
    },
    "recommended": {
      "cpu": "",
      "gpu": "",
      "ram_gb": 0,
      "storage_gb": 0
    }
  },
  "laptops": [
    {
      "name": "",
      "cpu": "",
      "gpu": "",
      "ram_gb": 0,
      "storage_gb": 0,
      "approx_price_uah": 0
    }
  ]
}

Відповідай ТІЛЬКИ JSON.
"""


def _extract_json(text: str) -> dict:
    
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError("JSON not found", text, 0)

    json_text = text[start:end + 1]

    return json.loads(json_text)


def get_game_and_laptops(
    game_name: str,
    settings: str = "Medium",
    resolution: str = "1920x1080",
    budget: int | None = None
) -> dict:

    user_prompt = f"""
Гра: {game_name}
Налаштування: {settings}
Роздільна здатність: {resolution}
Бюджет (грн): {budget if budget is not None else "не вказаний"}

Сформуй JSON у форматі вище.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
        )

        deepseek_raw_response = response.choices[0].message.content
    except Exception as e:
        print("❌ Помилка Deepseek API:", e)
        return {
            "error": "Не вдалося отримати відповідь від ШІ. Спробуйте ще раз."
        }

    try:
        result = _extract_json(deepseek_raw_response)
    except Exception as e:
        print("❌ JSON помилка:", e)
        print("Текст від моделі був такий:")
        print(deepseek_raw_response)
        return {
            "error": "ШІ повернула некоректні дані. Повторіть запит."
        }

    for lap in result.get("laptops", []):
        name = lap.get("name", "").strip()
        if name:
            q = quote_plus(name)
            lap["google_url"] = f"https://www.google.com/search?q={q}+купити+Україна"


    return result