import random

def spin_slots():
    FRUITS = ["🍌", "🍑", "🍋", "🍐", "🍏", "🍍", "🥝", "🥭", "🍅", "🍺"]
    OTHER_EMOJIS = ["💎", "🔔", "⭐️", "🎯", "🎲", "🧿", "👑", "💍", "💰", "💣"]
    BASKET = "🛒"

    while True:
        # Генерируем слоты с заданными вероятностями
        slots = []
        # Первый слот - 50% на корзину
        slots.append(BASKET if random.random() < 0.5 else random.choice(OTHER_EMOJIS))
        # Второй слот - 25% на фрукт
        slots.append(random.choice(FRUITS) if random.random() < 0.25 else random.choice(OTHER_EMOJIS))
        # Третий слот - 25% на фрукт
        slots.append(random.choice(FRUITS) if random.random() < 0.25 else random.choice(OTHER_EMOJIS))
        # Проверяем условие выигрыша: ровно одна корзина и ровно один фрукт
        basket_count = slots.count(BASKET)
        fruit_count = sum(1 for s in slots if s in FRUITS)
        # Если условие выполняется - возвращаем результат
        if basket_count == 1 and fruit_count == 1:
            win_fruit = next((s for s in slots if s in FRUITS), None)
            return slots, win_fruit
        else:
            return slots, None