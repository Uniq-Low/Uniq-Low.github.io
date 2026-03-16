import time
import json
import re
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- НАЛАШТУВАННЯ ---
SHAFA_URL = "https://shafa.ua/uk/member/uniqlo-shop?sort=4"
HTML_FILE = "index.html"


def get_category(title):
    t = title.lower()
    if 'пуховик' in t or 'куртка' in t or 'пальто' in t: return 'Верхній одяг'
    if 'спідниця' in t or 'юбка' in t: return 'Спідниці'
    if 'плаття' in t or 'сукня' in t: return 'Плаття'
    if 'футболка' in t or 'майка' in t: return 'Майки'
    if 'взуття' in t or 'кросівки' in t or 'черевики' in t: return 'Взуття'
    return 'Інше'


def main():
    print("🚀 Відкриваю браузер...")

    options = Options()
    # МИ ПРИБРАЛИ HEADLESS, ЩОБ САЙТ НЕ БЛОКУВАВ
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    data = []

    try:
        driver.get(SHAFA_URL)
        time.sleep(5)

        # Прокрутка вниз для завантаження картинок
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(3)

        # Шукаємо товари (картки)
        items = driver.find_elements(By.XPATH, "//li[.//a and .//img]")

        print(f"🔎 Знайдено елементів на сторінці: {len(items)}")

        for item in items[:30]:  # Беремо 30 штук
            try:
                # Шукаємо посилання
                link_el = item.find_element(By.TAG_NAME, "a")
                url = link_el.get_attribute("href")

                # Шукаємо картинку (src або data-src для лінивого завантаження)
                img_el = item.find_element(By.TAG_NAME, "img")
                img = img_el.get_attribute("src")
                if not img or "data:image" in img:
                    img = img_el.get_attribute("data-src")

                # Шукаємо ціну
                text = item.text
                price_match = re.search(r'(\d[\d\s]*грн)', text)
                price = price_match.group(0) if price_match else "Договірна"

                title = img_el.get_attribute("alt") or "Товар"

                if url and img:
                    data.append({
                        "name": title.strip(),
                        "image": img,
                        "price": price,
                        "url": url,
                        "category": get_category(title)
                    })
                    print(f"➕ {title[:20]}... - {price}")
            except:
                continue

    except Exception as e:
        print(f"❌ Помилка: {e}")
    finally:
        driver.quit()

    if not data:
        print("⚠️ Товарів не знайдено! Спробуй ще раз.")
        return

    # Оновлення HTML
    print("📝 Записую в файл...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    new_block = f"const products = {json_str};"

    # Заміна тексту між мітками
    pattern = r"(// --- PYTHON UPDATE AREA START ---\s*).*?(\s*// --- PYTHON UPDATE AREA END ---)"

    if re.search(pattern, html, re.DOTALL):
        new_html = re.sub(pattern, f"\\1\n    {new_block}\n    \\2", html, flags=re.DOTALL)
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("🎉 index.html оновлено!")

        # Git відправка
        print("🐙 Відправляю на GitHub...")
        subprocess.run(["git", "add", "."], shell=True)
        subprocess.run(["git", "commit", "-m", "Auto update"], shell=True)
        subprocess.run(["git", "push", "origin", "main"], shell=True)

        # Вимкнення ПК (розкоментуй, коли все буде працювати ідеально)
        # os.system("shutdown /s /t 60")

    else:
        print("❌ Не знайдено мітки в HTML!")


if __name__ == "__main__":
    main()