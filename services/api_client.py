import requests
import random
import json
import os
from datetime import datetime, timedelta
from urllib.parse import quote

CACHE_FILE = "storage/fruit_cache.json"
CACHE_EXPIRE_HOURS = 24

def get_fruit_fact(fruit=None):
    try:
        fruits = get_cached_fruits()
        if not fruits:
            fruits = fetch_all_fruits()
        
        if not fruit:
            fruit = random.choice(fruits)["name"]
        
        fruit_data = next((f for f in fruits if f["name"].lower() == fruit.lower()), None)
        if fruit_data:
            return format_fruit_info(fruit_data)
        return "Информация о фрукте не найдена."
    except Exception as e:
        return f"Ошибка при получении данных: {str(e)}"

def get_fruit_info(fruit_name):
    try:
        # Кэшированный запрос
        fruits = get_cached_fruits()
        if fruits:
            fruit = next((f for f in fruits if f["name"].lower() == fruit_name.lower()), None)
            if fruit:
                return fruit
        
        # Прямой запрос к API если нет в кэше
        response = requests.get(f"https://www.fruityvice.com/api/fruit/{quote(fruit_name)}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {"name": fruit_name, "nutritions": {"calories": "N/A", "sugar": "N/A"}}

def fetch_all_fruits():
    try:
        response = requests.get("https://www.fruityvice.com/api/fruit/all", timeout=5)
        response.raise_for_status()
        fruits = response.json()
        save_fruits_cache(fruits)
        return fruits
    except Exception:
        return []

def get_cached_fruits():
    if not os.path.exists(CACHE_FILE):
        return None
        
    cache_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
    if datetime.now() - cache_time > timedelta(hours=CACHE_EXPIRE_HOURS):
        return None
        
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_fruits_cache(fruits):
    os.makedirs("storage", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(fruits, f)

def format_fruit_info(fruit):
    name = fruit.get("name", "Неизвестный фрукт")
    nutrition = fruit.get("nutritions", {})

    calories = nutrition.get("calories", "N/A")
    sugar = nutrition.get("sugar", "N/A")
    fat = nutrition.get("fat", "N/A")
    carbohydrates = nutrition.get("carbohydrates", "N/A")
    protein = nutrition.get("protein", "N/A")

    fact_parts = [
        f"🍎 {name} — информация о фрукте:",
        "",
        "📊 Пищевая ценность на 100 г:",
        f"• Калории: {calories} ккал",
        f"• Сахар: {sugar} г",
        f"• Жиры: {fat} г",
        f"• Углеводы: {carbohydrates} г",
        f"• Белки: {protein} г",
    ]

    # Анализ калорийности
    if isinstance(calories, (int, float)):
        if calories < 40:
            fact_parts.append("🔹 Низкокалорийный фрукт")
        elif calories > 80:
            fact_parts.append("🔹 Высококалорийный фрукт")
        else:
            fact_parts.append("🔹 Средняя калорийность")

    # Анализ содержания сахара
    if isinstance(sugar, (int, float)):
        if sugar > 15:
            fact_parts.append("⚠️ Содержит много сахара")
        elif sugar < 5:
            fact_parts.append("✅ Низкое содержание сахара")

    # Комментарии по белку
    if isinstance(protein, (int, float)) and protein > 1:
        fact_parts.append("💪 Содержит заметное количество белка для фрукта")

    # Завершающая строка
    fact_parts.append("🍽️ Наслаждайтесь здоровым питанием!")

    return "\n".join(fact_parts)