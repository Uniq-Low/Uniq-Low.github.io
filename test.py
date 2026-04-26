# ============================================================
#  UniqLow — Редактор товарів + генератор GitHub Pages
#  pip install customtkinter selenium webdriver-manager pillow
# ============================================================

import sqlite3
import subprocess
import threading
import time
import tkinter.messagebox as mb
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ════════════════════════════════════════════════════════════
#  НАЛАШТУВАННЯ  —  міняй тут
# ════════════════════════════════════════════════════════════
SHOP_NAME  = "UniqLow"
ICON_NAME  = "icon.png"

# ✅ Номер телефону власника (з кодом країни, без +)
# Наприклад: "380991234567"  →  посилання буде https://t.me/+380991234567
CONTACT_PHONE = "380953862096"   # <-- ВСТАВ СВІЙ НОМЕР

BOT_URL = f"https://t.me/+{CONTACT_PHONE}"   # генерується автоматично

BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "shop.db"

SHAFA_PROFILE_URL = "https://shafa.ua/uk/member/uniqlo-shop?sort=4"
OLX_PROFILE_URL   = "https://www.olx.ua/uk/list/user/1735R/"
SHAFA_REVIEWS_URL = "https://shafa.ua/uk/member/uniqlo-shop/reviews?t=s"

# ════════════════════════════════════════════════════════════
#  МЕНЮ САЙТУ
# ════════════════════════════════════════════════════════════
MENU_GROUPS = {
    "Навігація": [
        ("⭐ Відгуки покупців", "/reviews/"),
        ("🌐 Shafa", "https://shafa.ua/uk/member/uniqlo-shop?sort=4"),
        ("🌐 OLX", "/olx/"),
    ],
    "Жіночий одяг": [
        ("Спідниці", "/spidnytsi/"), ("Плаття", "/plattya/"),
        ("Верхній одяг", "/verhniy-odyag/"), ("Майки й футболки", "/maiky-futbolky/"),
        ("Сорочки та блузи", "/sorochky-bluzy/"), ("Кофти", "/kofty/"),
        ("Спідня білизна", "/spidnya-bilyzna/"), ("Спортивний одяг", "/sportyvnyy-odyag/"),
        ("Костюми", "/kostyumy/"), ("Комбінезони", "/kombinezony/"),
        ("Одяг для дому та сну", "/odyag-dlya-domu/"),
        ("Взуття", "/vzuttya/"), ("Штани та шорти", "/shtany-shorty/"),
    ],
    "Дитячий одяг": [
        ("Для дівчаток", "/dlya-divchatok/"), ("Для хлопчиків", "/dlya-hlopchykiv/"),
        ("Для малюків", "/dlya-malyukiv/"),
    ],
    "Чоловічий одяг": [
        ("Верхній одяг", "/cholovichyy-verhniy-odyag/"), ("Кофти та светри", "/kofty-svetry/"),
        ("Сорочки та теніски", "/sorochky-tenisky/"), ("Футболки та майки", "/futbolky-mayky-men/"),
        ("Спідня білизна", "/spidnya-bilyzna-men/"), ("Взуття", "/vzuttya-men/"),
        ("Спортивний одяг", "/sportyvnyy-odyag-men/"),
        ("Одяг для дому та сну", "/odyag-dlya-domu-men/"),
        ("Штани та шорти", "/shtany-shorty-men/"),
    ],
    "Аксесуари": [
        ("Сумки та рюкзаки", "/sumky-ryukzaky/"), ("Головні убори", "/golovni-ubory/"),
        ("Ремені та пояси", "/remeni-poyasy/"),
    ],
}

SHAFA_CATEGORIES = [
    {"title": "Спідниці",           "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=yubki&sort=4",                    "slug": "spidnytsi"},
    {"title": "Плаття",             "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=platya&sort=4",                   "slug": "plattya"},
    {"title": "Верхній одяг (Ж)",   "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=verhnyaya-odezhda&sort=4",        "slug": "verhniy-odyag"},
    {"title": "Майки й футболки",   "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=mayki-i-futbolki&sort=4",         "slug": "maiky-futbolky"},
    {"title": "Сорочки та блузи",   "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=rubashki-i-bluzy&sort=4",         "slug": "sorochky-bluzy"},
    {"title": "Кофти",              "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=kofty&sort=4",                    "slug": "kofty"},
    {"title": "Спідня білизна",     "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=nizhnee-bele-i-kupalniki&sort=4", "slug": "spidnya-bilyzna"},
    {"title": "Спортивний одяг",    "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=sport-otdyh&sort=4",              "slug": "sportyvnyy-odyag"},
    {"title": "Костюми",            "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=zhenskie-kostyumy&sort=4",        "slug": "kostyumy"},
    {"title": "Комбінезони",        "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=zhenskie-kombinezony&sort=4",     "slug": "kombinezony"},
    {"title": "Одяг для дому (Ж)",  "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=odezhda-dlya-doma-i-sna&sort=4", "slug": "odyag-dlya-domu"},
    {"title": "Взуття (Ж)",         "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=zhenskaya-obuv&sort=4",           "slug": "vzuttya"},
    {"title": "Штани та шорти (Ж)", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=shtany&sort=4",                  "slug": "shtany-shorty"},
    {"title": "Для дівчаток",       "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=dlya-devochek&sort=4",            "slug": "dlya-divchatok"},
    {"title": "Для хлопчиків",      "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=dlya-malchikov&sort=4",           "slug": "dlya-hlopchykiv"},
    {"title": "Для малюків",        "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=dlya-malyshey&sort=4",            "slug": "dlya-malyukiv"},
    {"title": "Верхній одяг (Ч)",   "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=verkhniaia-odezhda&sort=4",      "slug": "cholovichyy-verhniy-odyag"},
    {"title": "Кофти та светри (Ч)","url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=kofti&sort=4",                   "slug": "kofty-svetry"},
    {"title": "Сорочки та теніски", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=rubashki&sort=4",                 "slug": "sorochky-tenisky"},
    {"title": "Футболки та майки",  "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=futbolki-i-maiki&sort=4",        "slug": "futbolky-mayky-men"},
    {"title": "Спідня білизна (Ч)", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=nizhnee-bele&sort=4",             "slug": "spidnya-bilyzna-men"},
    {"title": "Взуття (Ч)",         "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=obuv&sort=4",                    "slug": "vzuttya-men"},
    {"title": "Спортивний одяг (Ч)","url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=sport-i-otdyh&sort=4",           "slug": "sportyvnyy-odyag-men"},
    {"title": "Одяг для дому (Ч)",  "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=odezhda-dlia-doma-i-sna&sort=4", "slug": "odyag-dlya-domu-men"},
    {"title": "Штани та шорти (Ч)", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=shtany-i-shorty&sort=4",         "slug": "shtany-shorty-men"},
    {"title": "Сумки та рюкзаки",   "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=vsi-sumky&sort=4",               "slug": "sumky-ryukzaky"},
    {"title": "Головні убори",      "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=holovni-ubory&sort=4",           "slug": "golovni-ubory"},
    {"title": "Ремені та пояси",    "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=remeni-poyasy&sort=4",           "slug": "remeni-poyasy"},
]

SLUG_OPTIONS = ["scraped"] + [c["slug"] for c in SHAFA_CATEGORIES] + ["olx"]

# ════════════════════════════════════════════════════════════
#  SELENIUM
# ════════════════════════════════════════════════════════════

def make_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)


def normalize_url(url: str, base: str = "") -> str:
    if not url: return ""
    if url.startswith("http://") or url.startswith("https://"): return url
    if url.startswith("/"): return base.rstrip("/") + url
    return url


def collect_shafa_products(driver, url: str, limit: int = 150) -> list[dict]:
    driver.get(url)
    time.sleep(4)
    last_count = attempts = 0
    while attempts < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        cur = len(driver.find_elements(By.CSS_SELECTOR, "div.z0N6W7"))
        if cur >= limit: break
        if cur == last_count: attempts += 1
        else: last_count = cur; attempts = 0

    result = []
    for card in driver.find_elements(By.CSS_SELECTOR, "div.z0N6W7"):
        try:
            link_el  = card.find_element(By.CSS_SELECTOR, "a.p1SYwW")
            img_el   = card.find_element(By.CSS_SELECTOR, "img")
            price_el = card.find_element(By.CSS_SELECTOR, "p.D8o9s7")
            product_url = normalize_url(link_el.get_attribute("href"), "https://shafa.ua")
            image = img_el.get_attribute("src")
            title = (img_el.get_attribute("alt") or "Товар").strip()
            price = price_el.text.strip()
            brand = size = ""
            try: brand = card.find_element(By.CSS_SELECTOR, "p.i7zcRu").text.strip()
            except: pass
            try: size  = card.find_element(By.CSS_SELECTOR, "p.NyHfpp").text.strip()
            except: pass
            if product_url and image and price:
                result.append({"name": title, "image": image, "price": price,
                                "url": product_url, "brand": brand, "size": size})
            if len(result) >= limit: break
        except: continue
    return result


def collect_olx_products(driver, url: str, limit: int = 150) -> list[dict]:
    driver.get(url)
    time.sleep(5)
    last_count = attempts = 0
    while attempts < 5:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        cur = len(driver.find_elements(By.CSS_SELECTOR, "a.css-1tqlkj0"))
        if cur >= limit: break
        if cur == last_count: attempts += 1
        else: last_count = cur; attempts = 0

    result, used = [], set()
    for tl in driver.find_elements(By.CSS_SELECTOR, "a.css-1tqlkj0"):
        try:
            href  = normalize_url(tl.get_attribute("href"), "https://www.olx.ua")
            title = (tl.text or "").strip()
            if not href or not title or href in used: continue
            wrapper, depth, img_el = tl, 0, None
            while wrapper is not None and depth < 8:
                try:
                    img_el = wrapper.find_element(By.XPATH, ".//preceding::img[1]")
                    if img_el: break
                except: pass
                wrapper = wrapper.find_element(By.XPATH, "./..")
                depth += 1
            if not img_el: continue
            image = img_el.get_attribute("src")
            if not image: continue
            price = "Переглянути оголошення"
            try:
                text = tl.find_element(By.XPATH, "./ancestor::div[contains(@class,'css-13aawz3')][1]").text.strip()
                for line in text.splitlines():
                    if "грн" in line or "$" in line or "€" in line:
                        price = line.strip(); break
            except: pass
            result.append({"name": title, "image": image, "price": price,
                            "url": href, "brand": "OLX", "size": ""})
            used.add(href)
            if len(result) >= limit: break
        except: continue
    return result


def collect_shafa_reviews(driver, url: str, limit: int = 100) -> list[dict]:
    driver.get(url)
    time.sleep(4)
    last_count = attempts = 0
    while attempts < 4:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        cur = len(driver.find_elements(By.CSS_SELECTOR, "div.uiZ9LP"))
        if cur >= limit: break
        if cur == last_count: attempts += 1
        else: last_count = cur; attempts = 0

    result = []
    for card in driver.find_elements(By.CSS_SELECTOR, "div.uiZ9LP"):
        try:
            name = card.find_element(By.CSS_SELECTOR, "a.BWnpYH").text.strip()
            try: text = card.find_element(By.CSS_SELECTOR, "div.emowg6").text.strip()
            except: text = ""
            stars = len(card.find_elements(By.CSS_SELECTOR, "li.fDRQWG")) or 5
            if name:
                result.append({"name": name, "text": text, "stars": stars, "source": "Shafa"})
            if len(result) >= limit: break
        except: continue
    return result

# ════════════════════════════════════════════════════════════
#  БАЗА ДАНИХ
# ════════════════════════════════════════════════════════════

def db_ensure():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            category_slug TEXT NOT NULL DEFAULT 'scraped',
            price         TEXT NOT NULL DEFAULT '',
            image_url     TEXT NOT NULL DEFAULT '',
            item_url      TEXT NOT NULL UNIQUE,
            source        TEXT NOT NULL DEFAULT 'manual',
            brand         TEXT DEFAULT '',
            size          TEXT DEFAULT ''
        )""")
    conn.commit(); conn.close()


def db_load_all() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id,title,category_slug,price,image_url,item_url,source,brand,size "
        "FROM products ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_upsert(p: dict):
    conn = sqlite3.connect(DB_PATH)
    if p.get("id"):
        conn.execute("""
            UPDATE products SET title=?,category_slug=?,price=?,image_url=?,
            item_url=?,brand=?,size=?,source=? WHERE id=?""",
            (p["title"], p["category_slug"], p["price"], p["image_url"],
             p["item_url"], p.get("brand",""), p.get("size",""),
             p.get("source","manual"), p["id"]))
    else:
        conn.execute("""
            INSERT OR IGNORE INTO products
            (title,category_slug,price,image_url,item_url,source,brand,size)
            VALUES (?,?,?,?,?,?,?,?)""",
            (p["title"], p["category_slug"], p["price"], p["image_url"],
             p["item_url"], p.get("source","manual"),
             p.get("brand",""), p.get("size","")))
    conn.commit(); conn.close()


def db_delete(pid: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit(); conn.close()


def db_bulk_insert(products: list[dict]):
    conn = sqlite3.connect(DB_PATH)
    conn.executemany("""
        INSERT OR IGNORE INTO products
        (title,category_slug,price,image_url,item_url,source,brand,size)
        VALUES (:name,:slug,:price,:image,:url,'scraped',:brand,:size)""",
        [{"name": p["name"], "slug": p.get("category_slug","scraped"),
          "price": p["price"], "image": p["image"], "url": p["url"],
          "brand": p.get("brand",""), "size": p.get("size","")} for p in products])
    conn.commit(); conn.close()


def get_db_reviews() -> list[dict]:
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT display_name,stars,text FROM reviews ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return [{"name": r[0], "stars": r[1], "text": r[2] or "", "source": "Telegram"} for r in rows]
    except: return []

# ════════════════════════════════════════════════════════════
#  HTML ГЕНЕРАТОР
# ════════════════════════════════════════════════════════════

def save_root_index(html: str):
    (BASE_DIR / "index.html").write_text(html, encoding="utf-8")

def save_folder_page(slug: str, html: str):
    folder = BASE_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(html, encoding="utf-8")


def build_menu(current_path: str) -> str:
    html = []
    for group, items in MENU_GROUPS.items():
        html.append(f"<div class='menu-block'><div class='menu-title'>{group}</div><ul>")
        for text, href in items:
            active = "active-link" if href == current_path else ""
            target = " target='_blank' rel='noopener'" if href.startswith("http") else ""
            html.append(f"<li><a class='{active}' href='{href}'{target}>{text}</a></li>")
        html.append("</ul></div>")
    return "\n".join(html)


def product_card(item: dict, hidden=False) -> str:
    meta_parts = []
    if item.get("brand"): meta_parts.append(item["brand"])
    if item.get("size"):  meta_parts.append(item["size"])
    meta_html    = f"<div class='product-meta'>{' • '.join(meta_parts)}</div>" if meta_parts else ""
    hidden_class = " hidden-card" if hidden else ""
    return f"""
    <div class="product-card{hidden_class}">
        <a class="card-main-link" href="{item['url']}" target="_blank" rel="noopener">
            <div class="product-image-wrap">
                <img class="product-image" src="{item['image']}" alt="{item['name']}">
            </div>
            <div class="product-info">
                <div class="product-price">{item['price']}</div>
                <div class="product-title">{item['name']}</div>
                {meta_html}
            </div>
        </a>
        <a class="card-tg-btn" href="{BOT_URL}" target="_blank" rel="noopener">
            Замовити в Telegram (-10%)
        </a>
    </div>"""


def render_page(title: str, current_path: str, data: list, page_type: str = "category") -> str:
    menu_html = build_menu(current_path)
    prefix    = "." if current_path == "/" else ".."
    logo_src  = f"{prefix}/{ICON_NAME}"

    products_html = show_more_btn = reviews_html = ""

    if page_type in ("category", "home", "olx"):
        if data:
            products_html  = "".join(product_card(p) for p in data[:12])
            products_html += "".join(product_card(p, hidden=True) for p in data[12:])
        else:
            products_html = "<div class='empty-box'>У цьому розділі поки немає товарів.</div>"
        if len(data) > 12:
            show_more_btn = """<div class="show-more-wrap">
                <button class="show-more-btn" onclick="showMoreProducts(this)">Показати всі товари</button>
            </div>"""

    elif page_type == "reviews":
        if data:
            for r in data:
                stars_str = "★" * r["stars"] + "☆" * (5 - r["stars"])
                badge = f"<span class='src-badge src-{r['source'].lower()}'>{r['source']}</span>"
                reviews_html += f"""
                <div class="review-card">
                    <div class="review-header">
                        <div class="review-name">{r['name']} {badge}</div>
                        <div class="review-stars">{stars_str}</div>
                    </div>
                    <div class="review-text">{r['text']}</div>
                </div>"""
        else:
            reviews_html = "<div class='empty-box'>Відгуків поки немає.</div>"

    quick_tiles = promo_section = ""
    if page_type == "home":
        quick_tiles = """
        <section class="quick-section">
            <div class="section-top"><h2>Популярні розділи</h2></div>
            <div class="quick-grid">
                <a class="quick-tile" href="/spidnytsi/">Спідниці</a>
                <a class="quick-tile" href="/plattya/">Плаття</a>
                <a class="quick-tile" href="/verhniy-odyag/">Верхній одяг</a>
                <a class="quick-tile" href="/maiky-futbolky/">Майки й футболки</a>
                <a class="quick-tile" href="/kofty/">Кофти</a>
                <a class="quick-tile" href="/vzuttya/">Взуття</a>
                <a class="quick-tile" href="/cholovichyy-verhniy-odyag/">Чоловічий одяг</a>
                <a class="quick-tile" href="/olx/">OLX</a>
            </div>
        </section>"""
        promo_section = f"""
        <section class="promo-section">
            <div class="promo-card">
                <div class="promo-badge">-10%</div>
                <div class="promo-content">
                    <h2>Оформлюйте через Telegram зі знижкою 10%</h2>
                    <p>При оформленні замовлення ви гарантовано отримуєте знижку 10%.</p>
                    <a class="telegram-btn" href="{BOT_URL}" target="_blank" rel="noopener">Написати в Telegram</a>
                </div>
            </div>
        </section>"""

    if page_type == "reviews":
        content_area = f"""
        <div class="section-top">
            <h2>{title}</h2>
            <p>Тут зібрані відгуки з нашого Telegram та платформи Shafa.</p>
        </div>
        <div class="reviews-page-grid">{reviews_html}</div>"""
    else:
        content_area = f"""
        <div class="section-top">
            <h2>{"Популярні пропозиції" if page_type == "home" else "Товари розділу"}</h2>
        </div>
        <div class="products-grid">{products_html}</div>
        {show_more_btn}"""

    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{SHOP_NAME} — {title}</title>
<style>
:root{{--bg:#f6f8fc;--bg-soft:#eef2ff;--panel:rgba(255,255,255,0.92);--panel-solid:#fff;
--text:#101828;--muted:#667085;--accent:#e11d48;--accent-soft:rgba(225,29,72,.12);
--border:rgba(16,24,40,.08);--shadow:0 18px 45px rgba(16,24,40,.08);
--green:#16a34a;--orange:#f59e0b;}}
body.dark{{--bg:#0b1220;--bg-soft:#111827;--panel:rgba(17,24,39,.88);--panel-solid:#111827;
--text:#f8fafc;--muted:#98a2b3;--accent:#ff4d6d;--accent-soft:rgba(255,77,109,.12);
--border:rgba(255,255,255,.08);--shadow:0 18px 45px rgba(0,0,0,.35);}}
*{{box-sizing:border-box;}}
body{{margin:0;font-family:Arial,sans-serif;color:var(--text);background:var(--bg);}}
.layout{{display:grid;grid-template-columns:300px 1fr;min-height:100vh;}}
.sidebar{{position:sticky;top:0;height:100vh;overflow-y:auto;padding:20px;
border-right:1px solid var(--border);background:var(--panel);backdrop-filter:blur(18px);}}
.brand{{display:flex;align-items:center;gap:14px;text-decoration:none;margin-bottom:18px;
padding:12px;border-radius:20px;background:rgba(255,255,255,.04);}}
.brand-avatar{{width:66px;height:66px;border-radius:50%;object-fit:cover;
border:2px solid rgba(225,29,72,.18);flex-shrink:0;background:white;}}
.brand-name{{font-size:26px;font-weight:800;color:var(--accent);line-height:1;}}
.brand-sub{{margin-top:6px;font-size:13px;color:var(--muted);}}
.theme-toggle{{width:100%;border:1px solid var(--border);background:var(--panel-solid);
color:var(--text);border-radius:14px;padding:11px 12px;cursor:pointer;font-size:18px;margin-bottom:18px;}}
.menu-block{{margin-bottom:18px;}}
.menu-title{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;font-weight:800;
color:var(--muted);margin-bottom:8px;padding:0 6px;}}
.menu-block ul{{list-style:none;margin:0;padding:0;}}
.menu-block a{{display:block;text-decoration:none;color:var(--text);padding:10px 12px;
border-radius:12px;font-size:14px;margin-bottom:4px;transition:.18s ease;}}
.menu-block a:hover{{background:var(--accent-soft);color:var(--accent);transform:translateX(2px);}}
.active-link{{background:var(--accent-soft);color:var(--accent)!important;font-weight:700;}}
.content{{padding:28px;}}
.section-top{{margin-bottom:14px;}}
.section-top h2{{margin:0 0 6px;font-size:24px;}}
.section-top p{{margin:0;color:var(--muted);line-height:1.6;}}
.quick-section,.promo-section{{margin-bottom:28px;}}
.quick-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;}}
.quick-tile{{min-height:102px;display:flex;align-items:flex-end;padding:18px;text-decoration:none;
color:var(--text);font-size:18px;font-weight:800;border-radius:22px;border:1px solid var(--border);
background:var(--panel-solid);box-shadow:var(--shadow);transition:transform .18s ease;}}
.quick-tile:hover{{transform:translateY(-3px);border-color:var(--accent);}}
.promo-card{{display:flex;gap:18px;align-items:center;
background:linear-gradient(135deg,rgba(34,197,94,.12),rgba(34,197,94,.04));
border:1px solid rgba(34,197,94,.18);border-radius:28px;padding:24px;box-shadow:var(--shadow);}}
.promo-badge{{width:100px;height:100px;border-radius:50%;background:var(--green);color:white;
display:flex;align-items:center;justify-content:center;font-weight:900;font-size:24px;flex-shrink:0;}}
.telegram-btn{{display:inline-block;text-decoration:none;color:white;background:#229ED9;
padding:12px 18px;border-radius:14px;font-weight:700;margin-top:10px;}}
.products-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;}}
.product-card{{display:flex;flex-direction:column;background:var(--panel-solid);
border:1px solid var(--border);border-radius:22px;overflow:hidden;
box-shadow:var(--shadow);transition:.2s ease;}}
.product-card:hover{{transform:translateY(-5px);border-color:rgba(225,29,72,.18);
box-shadow:0 25px 48px rgba(16,24,40,.14);}}
.card-main-link{{text-decoration:none;color:inherit;flex-grow:1;display:flex;flex-direction:column;}}
.product-image-wrap{{background:var(--bg-soft);overflow:hidden;}}
.product-image{{width:100%;height:330px;object-fit:cover;display:block;transition:transform .35s ease;}}
.product-card:hover .product-image{{transform:scale(1.04);}}
.product-info{{padding:16px;flex-grow:1;}}
.product-price{{font-size:24px;font-weight:800;margin-bottom:8px;}}
.product-title{{font-size:15px;line-height:1.5;min-height:46px;margin-bottom:8px;}}
.product-meta{{font-size:13px;color:var(--muted);}}
.card-tg-btn{{display:block;margin:0 16px 16px;
background:linear-gradient(135deg,#2AABEE,#229ED9);color:white;text-align:center;
padding:12px;border-radius:14px;text-decoration:none;font-weight:bold;font-size:14px;transition:transform .2s;}}
.card-tg-btn:hover{{transform:translateY(-2px);box-shadow:0 5px 15px rgba(34,158,217,.3);}}
.hidden-card{{display:none;}}
.show-more-wrap{{margin-top:30px;text-align:center;}}
.show-more-btn{{border:none;background:linear-gradient(135deg,var(--accent),#fb7185);
color:white;padding:14px 28px;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;}}
.reviews-page-grid{{display:grid;grid-template-columns:1fr;gap:15px;max-width:800px;}}
.review-card{{background:var(--panel-solid);border:1px solid var(--border);
border-radius:16px;padding:20px;box-shadow:var(--shadow);}}
.review-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}}
.review-name{{font-weight:800;font-size:16px;display:flex;align-items:center;gap:10px;}}
.review-stars{{color:var(--orange);font-size:18px;}}
.review-text{{color:var(--text);line-height:1.6;font-size:15px;}}
.src-badge{{font-size:11px;padding:3px 8px;border-radius:8px;font-weight:bold;color:white;text-transform:uppercase;}}
.src-shafa{{background:#f59e0b;}}.src-telegram{{background:#2AABEE;}}
.empty-box{{padding:30px;border-radius:22px;border:1px dashed var(--border);
background:var(--panel-solid);color:var(--muted);}}
.footer-note{{margin-top:26px;text-align:center;color:var(--muted);font-size:13px;}}
@media(max-width:1080px){{
.layout{{grid-template-columns:1fr;}}
.sidebar{{position:static;height:auto;border-right:none;border-bottom:1px solid var(--border);}}
.promo-card{{flex-direction:column;text-align:center;}}}}
</style>
</head>
<body>
<div class="layout">
<aside class="sidebar">
    <a class="brand" href="{prefix}/">
        <img class="brand-avatar" src="{logo_src}" alt="{SHOP_NAME}">
        <div>
            <div class="brand-name">{SHOP_NAME}</div>
            <div class="brand-sub">Одяг та аксесуари</div>
        </div>
    </a>
    <button class="theme-toggle" onclick="toggleTheme()">🌗</button>
    {menu_html}
</aside>
<main class="content">
    {promo_section}
    {quick_tiles}
    {content_area}
    <div class="footer-note">{SHOP_NAME} • Створено для зручного перегляду товарів</div>
</main>
</div>
<script>
function toggleTheme(){{document.body.classList.toggle('dark');
localStorage.setItem('theme',document.body.classList.contains('dark')?'dark':'light');}}
if(localStorage.getItem('theme')==='dark')document.body.classList.add('dark');
function showMoreProducts(btn){{document.querySelectorAll('.hidden-card').forEach(el=>el.style.display='flex');btn.style.display='none';}}
</script>
</body>
</html>"""


def run_git():
    subprocess.run(["git", "add", "."],              cwd=BASE_DIR)
    subprocess.run(["git", "commit", "-m", "Auto update"], cwd=BASE_DIR)
    subprocess.run(["git", "push", "-f", "origin", "main"], cwd=BASE_DIR)


def rows_to_items(rows: list[dict]) -> list[dict]:
    return [{"name": r["title"], "price": r["price"], "image": r["image_url"],
             "url": r["item_url"], "brand": r.get("brand",""), "size": r.get("size","")}
            for r in rows]

# ════════════════════════════════════════════════════════════
#  GUI — ДІАЛОГ РЕДАГУВАННЯ
# ════════════════════════════════════════════════════════════

class ProductDialog(ctk.CTkToplevel):
    def __init__(self, master, product: dict | None = None):
        super().__init__(master)
        self.title("✏️ Редагувати" if product else "➕ Новий товар")
        self.geometry("600x580")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.result: dict | None = None
        p = product or {}

        def field(label, default=""):
            ctk.CTkLabel(self, text=label, anchor="w").pack(fill="x", padx=20, pady=(10, 2))
            e = ctk.CTkEntry(self, width=555)
            e.pack(padx=20)
            e.insert(0, default)
            return e

        self.e_title = field("Назва товару *",          p.get("title", ""))
        self.e_price = field("Ціна *  (напр. 450 грн)", p.get("price", ""))
        self.e_url   = field("URL товару *",             p.get("item_url", ""))
        self.e_img   = field("URL зображення *",         p.get("image_url", ""))
        self.e_brand = field("Бренд",                    p.get("brand", ""))
        self.e_size  = field("Розмір",                   p.get("size", ""))

        ctk.CTkLabel(self, text="Категорія (slug)", anchor="w").pack(fill="x", padx=20, pady=(10,2))
        self.slug_var = ctk.StringVar(value=p.get("category_slug", "scraped"))
        ctk.CTkComboBox(self, values=SLUG_OPTIONS, variable=self.slug_var, width=555).pack(padx=20)

        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(fill="x", padx=20, pady=18)
        ctk.CTkButton(bf, text="💾 Зберегти", fg_color="#16a34a",
                      hover_color="#15803d", command=self._save).pack(side="left", padx=(0,10))
        ctk.CTkButton(bf, text="Скасувати",  fg_color="gray40",
                      hover_color="gray30",  command=self.destroy).pack(side="left")
        self._p = p

    def _save(self):
        t = self.e_title.get().strip()
        pr = self.e_price.get().strip()
        u = self.e_url.get().strip()
        im = self.e_img.get().strip()
        if not all([t, pr, u, im]):
            mb.showerror("Помилка", "Заповніть усі обов'язкові поля (*)", parent=self)
            return
        self.result = {
            "id": self._p.get("id"),
            "title": t, "price": pr, "item_url": u, "image_url": im,
            "category_slug": self.slug_var.get(),
            "brand": self.e_brand.get().strip(),
            "size":  self.e_size.get().strip(),
            "source": self._p.get("source", "manual"),
        }
        self.destroy()

# ════════════════════════════════════════════════════════════
#  GUI — ГОЛОВНЕ ВІКНО
# ════════════════════════════════════════════════════════════

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"🛍  {SHOP_NAME} — Редактор товарів")
        self.geometry("1400x830")
        self.minsize(1100, 680)
        db_ensure()
        self._products: list[dict] = []
        self._sort_rev: dict = {}
        self._build_ui()
        self._load_table()

    # ── UI ──────────────────────────────────────────────────
    def _build_ui(self):
        # Toolbar
        tb = ctk.CTkFrame(self, height=58, corner_radius=0)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        ctk.CTkLabel(tb, text=f"🛍  {SHOP_NAME}",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=18)

        btn = {"height": 36, "corner_radius": 10}
        ctk.CTkButton(tb, text="🚀 Опублікувати на GitHub",
                      fg_color="#e11d48", hover_color="#be123c",
                      command=self._publish, **btn).pack(side="right", padx=(0,14), pady=11)
        ctk.CTkButton(tb, text="📥 Підтягнути з Шафа",
                      fg_color="#7c3aed", hover_color="#6d28d9",
                      command=self._pull_shafa, **btn).pack(side="right", padx=(0,8), pady=11)
        ctk.CTkButton(tb, text="🔄 Оновити",
                      fg_color="#0284c7", hover_color="#0369a1",
                      command=self._load_table, **btn).pack(side="right", padx=(0,8), pady=11)

        # Filter bar
        fb = ctk.CTkFrame(self, height=48, corner_radius=0, fg_color=("gray90","gray15"))
        fb.pack(fill="x")
        fb.pack_propagate(False)
        ctk.CTkLabel(fb, text="🔍 Пошук:").pack(side="left", padx=(14,4))
        self._sv = ctk.StringVar()
        self._sv.trace_add("write", lambda *_: self._apply_filter())
        ctk.CTkEntry(fb, textvariable=self._sv, width=260,
                     placeholder_text="Назва / бренд / розмір…").pack(side="left", padx=(0,16))
        ctk.CTkLabel(fb, text="Категорія:").pack(side="left", padx=(0,4))
        self._slug_v = ctk.StringVar(value="Всі")
        ctk.CTkComboBox(fb, values=["Всі"]+SLUG_OPTIONS, variable=self._slug_v,
                        width=200, command=lambda _: self._apply_filter()).pack(side="left")
        self._cnt = ctk.CTkLabel(fb, text="")
        self._cnt.pack(side="right", padx=14)

        # Table
        tf = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        tf.pack(fill="both", expand=True, padx=12, pady=(8,0))

        cols    = ("id","title","price","brand","size","category_slug","source","item_url")
        headers = ("ID","Назва","Ціна","Бренд","Розмір","Категорія","Джерело","URL")
        widths  = (48, 320, 90, 110, 80, 160, 80, 280)

        dark = ctk.get_appearance_mode() == "Dark"
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("S.Treeview",
            background   ="#1e1e2e" if dark else "#ffffff",
            foreground   ="#cdd6f4" if dark else "#101828",
            fieldbackground="#1e1e2e" if dark else "#ffffff",
            rowheight=30, font=("Arial",12))
        st.configure("S.Treeview.Heading",
            background="#313244" if dark else "#f1f5f9",
            foreground="#cdd6f4" if dark else "#101828",
            font=("Arial",12,"bold"))
        st.map("S.Treeview",
            background=[("selected","#585b70" if dark else "#dbeafe")])

        self._tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  style="S.Treeview", selectmode="extended")
        for c,h,w in zip(cols,headers,widths):
            self._tree.heading(c, text=h, command=lambda x=c: self._sort_by(x))
            self._tree.column(c, width=w, minwidth=40)

        ys = ttk.Scrollbar(tf, orient="vertical",   command=self._tree.yview)
        xs = ttk.Scrollbar(tf, orient="horizontal",  command=self._tree.xview)
        self._tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)
        self._tree.bind("<Double-1>", lambda _: self._edit_selected())

        # Bottom bar
        bb = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color=("gray90","gray15"))
        bb.pack(fill="x", side="bottom")
        bb.pack_propagate(False)
        ctk.CTkButton(bb, text="➕ Додати",        fg_color="#16a34a", hover_color="#15803d",
                      command=self._add,            **btn).pack(side="left", padx=14, pady=8)
        ctk.CTkButton(bb, text="✏️ Редагувати",    fg_color="#0284c7", hover_color="#0369a1",
                      command=self._edit_selected,  **btn).pack(side="left", padx=(0,8), pady=8)
        ctk.CTkButton(bb, text="🗑 Видалити",      fg_color="#dc2626", hover_color="#b91c1c",
                      command=self._delete_selected,**btn).pack(side="left", padx=(0,8), pady=8)

        # Log
        self._log = ctk.CTkTextbox(self, height=110, corner_radius=0,
                                   font=ctk.CTkFont(family="Courier", size=12))
        self._log.pack(fill="x", side="bottom")
        self._log.configure(state="disabled")

    # ── helpers ─────────────────────────────────────────────
    def _log_msg(self, msg: str):
        self._log.configure(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _sort_by(self, col: str):
        rev = self._sort_rev.get(col, False)
        self._sort_rev[col] = not rev
        data = [(self._tree.set(k, col), k) for k in self._tree.get_children()]
        data.sort(reverse=rev, key=lambda x: x[0].lower())
        for i, (_, k) in enumerate(data):
            self._tree.move(k, "", i)

    # ── таблиця ─────────────────────────────────────────────
    def _load_table(self):
        self._products = db_load_all()
        self._apply_filter()

    def _apply_filter(self):
        q    = self._sv.get().strip().lower()
        slug = self._slug_v.get()
        filtered = [
            p for p in self._products
            if (not q or q in p["title"].lower()
                      or q in p.get("brand","").lower()
                      or q in p.get("size","").lower())
            and (slug == "Всі" or p["category_slug"] == slug)
        ]
        self._tree.delete(*self._tree.get_children())
        for p in filtered:
            self._tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["title"], p["price"],
                p.get("brand",""), p.get("size",""),
                p["category_slug"], p["source"], p["item_url"]))
        self._cnt.configure(text=f"Показано: {len(filtered)} / Всього: {len(self._products)}")

    # ── CRUD ────────────────────────────────────────────────
    def _add(self):
        dlg = ProductDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            db_upsert(dlg.result)
            self._log_msg(f"➕ Додано: {dlg.result['title']}")
            self._load_table()

    def _edit_selected(self):
        sel = self._tree.selection()
        if not sel:
            mb.showinfo("Підказка", "Виберіть рядок для редагування")
            return
        pid = int(sel[0])
        prod = next((p for p in self._products if p["id"] == pid), None)
        if not prod: return
        dlg = ProductDialog(self, prod)
        self.wait_window(dlg)
        if dlg.result:
            db_upsert(dlg.result)
            self._log_msg(f"✏️  Оновлено: {dlg.result['title']}")
            self._load_table()

    def _delete_selected(self):
        sel = self._tree.selection()
        if not sel:
            mb.showinfo("Підказка", "Виберіть рядки для видалення")
            return
        if not mb.askyesno("Підтвердження", f"Видалити {len(sel)} товар(ів)?"):
            return
        for iid in sel:
            db_delete(int(iid))
            self._log_msg(f"🗑  Видалено ID={iid}")
        self._load_table()

    # ── ПІДТЯГНУТИ З ШАФА ───────────────────────────────────
    def _pull_shafa(self):
        if not mb.askyesno("Підтягнути з Shafa",
                           "Запустити збір товарів?\n(займе 5–15 хвилин)"):
            return
        self._log_msg("🔄 Починаю збір з Shafa…")
        threading.Thread(target=self._pull_worker, daemon=True).start()

    def _pull_worker(self):
        try:
            driver = make_driver()
            total  = 0
            try:
                self._log_msg("  → Головна Shafa…")
                prods = collect_shafa_products(driver, SHAFA_PROFILE_URL, limit=12)
                for p in prods: p["category_slug"] = "scraped"
                db_bulk_insert(prods)
                total += len(prods)
                self._log_msg(f"     ✅ {len(prods)} товарів")

                for cat in SHAFA_CATEGORIES:
                    self._log_msg(f"  → {cat['title']}…")
                    prods = collect_shafa_products(driver, cat["url"], limit=150)
                    for p in prods: p["category_slug"] = cat["slug"]
                    db_bulk_insert(prods)
                    total += len(prods)
                    self._log_msg(f"     ✅ {len(prods)} товарів")
            finally:
                driver.quit()
            self._log_msg(f"✅ Всього підтягнуто: {total} товарів")
            self.after(0, self._load_table)
        except Exception as e:
            self._log_msg(f"❌ Помилка: {e}")

    # ── ОПУБЛІКУВАТИ ────────────────────────────────────────
    def _publish(self):
        if not mb.askyesno("Публікація",
                           "Згенерувати HTML зі змін у БД і відправити на GitHub?"):
            return
        self._log_msg("🚀 Починаю публікацію…")
        threading.Thread(target=self._publish_worker, daemon=True).start()

    def _publish_worker(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row

            # Головна — останні 12 товарів
            rows = conn.execute(
                "SELECT * FROM products ORDER BY id DESC LIMIT 12"
            ).fetchall()
            save_root_index(render_page("Головна", "/",
                                        rows_to_items([dict(r) for r in rows]),
                                        page_type="home"))
            self._log_msg("  ✅ Головна")

            # Категорії
            for cat in SHAFA_CATEGORIES:
                rows = conn.execute(
                    "SELECT * FROM products WHERE category_slug=? ORDER BY id DESC",
                    (cat["slug"],)
                ).fetchall()
                items = rows_to_items([dict(r) for r in rows])
                save_folder_page(cat["slug"],
                                 render_page(cat["title"], f"/{cat['slug']}/",
                                             items, page_type="category"))
                self._log_msg(f"  ✅ {cat['title']} ({len(items)})")

            # OLX
            rows = conn.execute(
                "SELECT * FROM products WHERE source='olx' OR brand='OLX' ORDER BY id DESC"
            ).fetchall()
            olx = rows_to_items([dict(r) for r in rows])
            save_folder_page("olx", render_page("OLX", "/olx/", olx, page_type="olx"))
            self._log_msg(f"  ✅ OLX ({len(olx)})")
            conn.close()

            # Відгуки — збираємо з Shafa через selenium
            self._log_msg("  → Збираю відгуки з Shafa (selenium)…")
            try:
                driver = make_driver()
                shafa_reviews = collect_shafa_reviews(driver, SHAFA_REVIEWS_URL, limit=100)
                driver.quit()
                self._log_msg(f"  ✅ Shafa відгуки: {len(shafa_reviews)}")
            except Exception as e:
                shafa_reviews = []
                self._log_msg(f"  ⚠️ Shafa відгуки не зібрано: {e}")

            # Telegram відгуки з БД (якщо є)
            telegram_reviews = get_db_reviews()
            self._log_msg(f"  ✅ Telegram відгуки: {len(telegram_reviews)}")

            all_reviews = telegram_reviews + shafa_reviews
            save_folder_page("reviews",
                             render_page("Відгуки покупців", "/reviews/",
                                         all_reviews, page_type="reviews"))
            self._log_msg(f"  ✅ Відгуки всього: {len(all_reviews)}")

            # Git
            self._log_msg("🔧 Git push…")
            run_git()
            self._log_msg("🎉 Опубліковано успішно!")
        except Exception as e:
            self._log_msg(f"❌ Помилка публікації: {e}")


# ════════════════════════════════════════════════════════════
#  ЗАПУСК
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Якщо запускати напряму — відкриває GUI
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    App().mainloop()