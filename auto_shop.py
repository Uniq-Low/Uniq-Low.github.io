import subprocess
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = Path(__file__).parent

SHOP_NAME = "UniqloShop"
AVATAR_URL = "https://avatars.shafastatic.net/691711_new_avatar_type1648494975"

SHAFA_PROFILE_URL = "https://shafa.ua/uk/member/uniqlo-shop?sort=4"
OLX_PROFILE_URL = "https://www.olx.ua/uk/list/user/1735R/"

SHAFA_CATEGORIES = [
    {"title": "Спідниці", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=yubki&sort=4", "slug": "spidnytsi", "group": "Жіночий одяг"},
    {"title": "Плаття", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=platya&sort=4", "slug": "plattya", "group": "Жіночий одяг"},
    {"title": "Верхній одяг", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=verhnyaya-odezhda&sort=4", "slug": "verhniy-odyag", "group": "Жіночий одяг"},
    {"title": "Майки й футболки", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=mayki-i-futbolki&sort=4", "slug": "maiky-futbolky", "group": "Жіночий одяг"},
    {"title": "Сорочки та блузи", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=rubashki-i-bluzy&sort=4", "slug": "sorochky-bluzy", "group": "Жіночий одяг"},
    {"title": "Кофти", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=kofty&sort=4", "slug": "kofty", "group": "Жіночий одяг"},
    {"title": "Спідня білизна", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=nizhnee-bele-i-kupalniki&sort=4", "slug": "spidnya-bilyzna", "group": "Жіночий одяг"},
    {"title": "Спортивний одяг", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=sport-otdyh&sort=4", "slug": "sportyvnyy-odyag", "group": "Жіночий одяг"},
    {"title": "Костюми", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=zhenskie-kostyumy&sort=4", "slug": "kostyumy", "group": "Жіночий одяг"},
    {"title": "Комбінезони", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=zhenskie-kombinezony&sort=4", "slug": "kombinezony", "group": "Жіночий одяг"},
    {"title": "Одяг для дому та сну", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=odezhda-dlya-doma-i-sna&sort=4", "slug": "odyag-dlya-domu", "group": "Жіночий одяг"},
    {"title": "Взуття", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=zhenskaya-obuv&sort=4", "slug": "vzuttya", "group": "Жіночий одяг"},
    {"title": "Штани та шорти", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=shtany&sort=4", "slug": "shtany-shorty", "group": "Жіночий одяг"},

    {"title": "Для дівчаток", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=dlya-devochek&sort=4", "slug": "dlya-divchatok", "group": "Дитячий одяг"},
    {"title": "Для хлопчиків", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=dlya-malchikov&sort=4", "slug": "dlya-hlopchykiv", "group": "Дитячий одяг"},
    {"title": "Для малюків", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=dlya-malyshey&sort=4", "slug": "dlya-malyukiv", "group": "Дитячий одяг"},

    {"title": "Верхній одяг", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=verkhniaia-odezhda&sort=4", "slug": "cholovichyy-verhniy-odyag", "group": "Чоловічий одяг"},
    {"title": "Кофти та светри", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=kofti&sort=4", "slug": "kofty-svetry", "group": "Чоловічий одяг"},
    {"title": "Сорочки та теніски", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=rubashki&sort=4", "slug": "sorochky-tenisky", "group": "Чоловічий одяг"},
    {"title": "Футболки та майки", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=futbolki-i-maiki&sort=4", "slug": "futbolky-mayky-men", "group": "Чоловічий одяг"},
    {"title": "Спідня білизна", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=nizhnee-bele&sort=4", "slug": "spidnya-bilyzna-men", "group": "Чоловічий одяг"},
    {"title": "Взуття", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=obuv&sort=4", "slug": "vzuttya-men", "group": "Чоловічий одяг"},
    {"title": "Спортивний одяг", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=sport-i-otdyh&sort=4", "slug": "sportyvnyy-odyag-men", "group": "Чоловічий одяг"},
    {"title": "Одяг для дому та сну", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=odezhda-dlia-doma-i-sna&sort=4", "slug": "odyag-dlya-domu-men", "group": "Чоловічий одяг"},
    {"title": "Штани та шорти", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=shtany-i-shorty&sort=4", "slug": "shtany-shorty-men", "group": "Чоловічий одяг"},

    {"title": "Сумки та рюкзаки", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=vsi-sumky&sort=4", "slug": "sumky-ryukzaky", "group": "Аксесуари"},
    {"title": "Головні убори", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=holovni-ubory&sort=4", "slug": "golovni-ubory", "group": "Аксесуари"},
    {"title": "Ремені та пояси", "url": "https://shafa.ua/uk/member/uniqlo-shop?catalog=remeni-poyasy&sort=4", "slug": "remeni-poyasy", "group": "Аксесуари"},
]

MENU_GROUPS = {
    "Жіночий одяг": [
        ("Спідниці", "/spidnytsi/"),
        ("Плаття", "/plattya/"),
        ("Верхній одяг", "/verhniy-odyag/"),
        ("Майки й футболки", "/maiky-futbolky/"),
        ("Сорочки та блузи", "/sorochky-bluzy/"),
        ("Кофти", "/kofty/"),
        ("Спідня білизна", "/spidnya-bilyzna/"),
        ("Спортивний одяг", "/sportyvnyy-odyag/"),
        ("Костюми", "/kostyumy/"),
        ("Комбінезони", "/kombinezony/"),
        ("Одяг для дому та сну", "/odyag-dlya-domu/"),
        ("Взуття", "/vzuttya/"),
        ("Штани та шорти", "/shtany-shorty/"),
    ],
    "Дитячий одяг": [
        ("Для дівчаток", "/dlya-divchatok/"),
        ("Для хлопчиків", "/dlya-hlopchykiv/"),
        ("Для малюків", "/dlya-malyukiv/"),
    ],
    "Чоловічий одяг": [
        ("Верхній одяг", "/cholovichyy-verhniy-odyag/"),
        ("Кофти та светри", "/kofty-svetry/"),
        ("Сорочки та теніски", "/sorochky-tenisky/"),
        ("Футболки та майки", "/futbolky-mayky-men/"),
        ("Спідня білизна", "/spidnya-bilyzna-men/"),
        ("Взуття", "/vzuttya-men/"),
        ("Спортивний одяг", "/sportyvnyy-odyag-men/"),
        ("Одяг для дому та сну", "/odyag-dlya-domu-men/"),
        ("Штани та шорти", "/shtany-shorty-men/"),
    ],
    "Аксесуари": [
        ("Сумки та рюкзаки", "/sumky-ryukzaky/"),
        ("Головні убори", "/golovni-ubory/"),
        ("Ремені та пояси", "/remeni-poyasy/"),
    ],
    "Майданчики": [
        ("Shafa", "https://shafa.ua/uk/member/uniqlo-shop?sort=4"),
        ("OLX", "/olx/"),
    ]
}


def normalize_url(url: str, base: str = "") -> str:
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return base.rstrip("/") + url
    return url


def make_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


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


def product_card(item: dict) -> str:
    meta_parts = []
    if item.get("brand"):
        meta_parts.append(item["brand"])
    if item.get("size"):
        meta_parts.append(item["size"])

    meta_html = f"<div class='product-meta'>{' • '.join(meta_parts)}</div>" if meta_parts else ""

    return f"""
    <a class="product-card" href="{item['url']}" target="_blank" rel="noopener">
        <div class="product-image-wrap">
            <img class="product-image" src="{item['image']}" alt="{item['name']}">
        </div>
        <div class="product-info">
            <div class="product-price">{item['price']}</div>
            <div class="product-title">{item['name']}</div>
            {meta_html}
        </div>
    </a>
    """


def render_page(title: str, current_path: str, products: list, page_type: str = "category") -> str:
    menu_html = build_menu(current_path)
    products_html = "".join(product_card(p) for p in products) if products else "<div class='empty-box'>У цьому розділі поки немає товарів.</div>"

    hero_text = {
        "home": "Стильний та зручний каталог товарів магазину UniqloShop. Обирайте потрібний розділ, переглядайте популярні пропозиції та переходьте до оголошення в один клік.",
        "olx": "Окремий каталог товарів з OLX у єдиному стилі сайту. Переглядайте пропозиції та відкривайте потрібне оголошення миттєво.",
    }.get(page_type, "Добірка товарів розділу з переходом до оригінального оголошення.")

    quick_tiles = ""
    if page_type == "home":
        quick_tiles = """
        <section class="quick-section">
            <div class="section-top">
                <h2>Популярні розділи</h2>
                <p>Швидкий перехід до найпопулярніших категорій.</p>
            </div>
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
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SHOP_NAME} — {title}</title>
    <meta name="description" content="Каталог товарів магазину {SHOP_NAME}. Українська мова, зручна навігація, товари Shafa та OLX.">
    <style>
        :root {{
            --bg: #f6f8fc;
            --bg-soft: #eef2ff;
            --panel: rgba(255,255,255,0.92);
            --panel-solid: #ffffff;
            --text: #101828;
            --muted: #667085;
            --accent: #e11d48;
            --accent-soft: rgba(225, 29, 72, 0.12);
            --border: rgba(16,24,40,0.08);
            --shadow: 0 18px 45px rgba(16,24,40,0.08);
            --hero: linear-gradient(135deg, #fff1f2 0%, #ffffff 38%, #eef4ff 100%);
        }}

        body.dark {{
            --bg: #0b1220;
            --bg-soft: #111827;
            --panel: rgba(17,24,39,0.88);
            --panel-solid: #111827;
            --text: #f8fafc;
            --muted: #98a2b3;
            --accent: #ff4d6d;
            --accent-soft: rgba(255,77,109,0.12);
            --border: rgba(255,255,255,0.08);
            --shadow: 0 18px 45px rgba(0,0,0,0.35);
            --hero: linear-gradient(135deg, #1f2937 0%, #111827 38%, #0b1220 100%);
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at left top, rgba(225,29,72,0.09), transparent 24%),
                radial-gradient(circle at right top, rgba(59,130,246,0.08), transparent 22%),
                var(--bg);
        }}

        .layout {{
            display: grid;
            grid-template-columns: 300px 1fr;
            min-height: 100vh;
        }}

        .sidebar {{
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            padding: 20px;
            border-right: 1px solid var(--border);
            background: var(--panel);
            backdrop-filter: blur(18px);
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
            margin-bottom: 18px;
            padding: 12px;
            border-radius: 20px;
            background: rgba(255,255,255,0.04);
        }}

        .brand-avatar {{
            width: 66px;
            height: 66px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid rgba(225,29,72,0.18);
            flex-shrink: 0;
        }}

        .brand-name {{
            font-size: 26px;
            font-weight: 800;
            color: var(--accent);
            line-height: 1;
        }}

        .brand-sub {{
            margin-top: 6px;
            font-size: 13px;
            color: var(--muted);
        }}

        .top-links {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }}

        .top-btn {{
            text-decoration: none;
            color: white;
            font-size: 14px;
            font-weight: 700;
            text-align: center;
            padding: 11px 12px;
            border-radius: 14px;
            transition: transform .18s ease, box-shadow .18s ease;
        }}

        .top-btn:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }}

        .btn-shafa {{
            background: linear-gradient(135deg, #f59e0b, #ea580c);
        }}

        .btn-olx {{
            background: linear-gradient(135deg, #16a34a, #15803d);
        }}

        .theme-toggle {{
            width: 100%;
            border: 1px solid var(--border);
            background: var(--panel-solid);
            color: var(--text);
            border-radius: 14px;
            padding: 11px 12px;
            cursor: pointer;
            font-size: 18px;
            margin-bottom: 18px;
        }}

        .theme-toggle:hover {{
            border-color: rgba(225,29,72,0.18);
        }}

        .menu-block {{
            margin-bottom: 18px;
        }}

        .menu-title {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-weight: 800;
            color: var(--muted);
            margin-bottom: 8px;
            padding: 0 6px;
        }}

        .menu-block ul {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        .menu-block li {{
            margin-bottom: 4px;
        }}

        .menu-block a {{
            display: block;
            text-decoration: none;
            color: var(--text);
            padding: 10px 12px;
            border-radius: 12px;
            font-size: 14px;
            transition: .18s ease;
        }}

        .menu-block a:hover {{
            background: var(--accent-soft);
            color: var(--accent);
            transform: translateX(2px);
        }}

        .active-link {{
            background: var(--accent-soft);
            color: var(--accent) !important;
            font-weight: 700;
        }}

        .content {{
            padding: 28px;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            border-radius: 30px;
            border: 1px solid var(--border);
            background: var(--hero);
            box-shadow: var(--shadow);
            padding: 28px;
            margin-bottom: 28px;
        }}

        .hero::after {{
            content: "";
            position: absolute;
            right: -80px;
            top: -80px;
            width: 260px;
            height: 260px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(225,29,72,0.18), transparent 68%);
        }}

        .hero-inner {{
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            gap: 20px;
            align-items: flex-start;
            flex-wrap: wrap;
        }}

        .hero h1 {{
            margin: 0 0 10px;
            font-size: 38px;
            line-height: 1.05;
        }}

        .hero p {{
            margin: 0;
            max-width: 800px;
            color: var(--muted);
            font-size: 16px;
            line-height: 1.7;
        }}

        .hero-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
        }}

        .hero-badge {{
            padding: 10px 14px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.45);
            font-size: 13px;
        }}

        .section-top {{
            margin-bottom: 14px;
        }}

        .section-top h2 {{
            margin: 0 0 6px;
            font-size: 24px;
        }}

        .section-top p {{
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
        }}

        .quick-section {{
            margin-bottom: 28px;
        }}

        .quick-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
        }}

        .quick-tile {{
            min-height: 102px;
            display: flex;
            align-items: flex-end;
            padding: 18px;
            text-decoration: none;
            color: var(--text);
            font-size: 18px;
            font-weight: 800;
            border-radius: 22px;
            border: 1px solid var(--border);
            background: linear-gradient(135deg, rgba(225,29,72,0.08), rgba(255,255,255,0.35));
            box-shadow: var(--shadow);
            transition: transform .18s ease, border-color .18s ease;
        }}

        .quick-tile:hover {{
            transform: translateY(-3px);
            border-color: rgba(225,29,72,0.22);
        }}

        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 20px;
        }}

        .product-card {{
            display: block;
            text-decoration: none;
            color: inherit;
            border-radius: 22px;
            overflow: hidden;
            background: var(--panel-solid);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            transition: .2s ease;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 25px 48px rgba(16,24,40,0.14);
            border-color: rgba(225,29,72,0.18);
        }}

        .product-image-wrap {{
            background: var(--bg-soft);
            overflow: hidden;
        }}

        .product-image {{
            width: 100%;
            height: 330px;
            object-fit: cover;
            display: block;
            transition: transform .35s ease;
        }}

        .product-card:hover .product-image {{
            transform: scale(1.04);
        }}

        .product-info {{
            padding: 16px;
        }}

        .product-price {{
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 8px;
        }}

        .product-title {{
            font-size: 15px;
            line-height: 1.5;
            min-height: 46px;
            margin-bottom: 8px;
        }}

        .product-meta {{
            font-size: 13px;
            color: var(--muted);
        }}

        .empty-box {{
            padding: 30px;
            border-radius: 22px;
            border: 1px dashed var(--border);
            background: var(--panel-solid);
            color: var(--muted);
        }}

        .footer-note {{
            margin-top: 26px;
            text-align: center;
            color: var(--muted);
            font-size: 13px;
        }}

        @media (max-width: 1080px) {{
            .layout {{
                grid-template-columns: 1fr;
            }}

            .sidebar {{
                position: static;
                height: auto;
                border-right: none;
                border-bottom: 1px solid var(--border);
            }}

            .content {{
                padding: 18px;
            }}

            .hero {{
                padding: 22px;
            }}

            .hero h1 {{
                font-size: 30px;
            }}
        }}
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <a class="brand" href="/">
                <img class="brand-avatar" src="{AVATAR_URL}" alt="uniqlo-shop">
                <div>
                    <div class="brand-name">{SHOP_NAME}</div>
                    <div class="brand-sub">Одяг та аксесуари</div>
                </div>
            </a>

            <div class="top-links">
                <a class="top-btn btn-shafa" href="{SHAFA_PROFILE_URL}" target="_blank" rel="noopener">Shafa</a>
                <a class="top-btn btn-olx" href="/olx/">OLX</a>
            </div>

            <button class="theme-toggle" onclick="toggleTheme()" aria-label="Змінити тему">🌗</button>

            {menu_html}
        </aside>

        <main class="content">
            <section class="hero">
                <div class="hero-inner">
                    <div>
                        <h1>{title}</h1>
                        <p>{hero_text}</p>
                        <div class="hero-badges">
                            <div class="hero-badge">Українська мова</div>
                            <div class="hero-badge">Зручна навігація</div>
                            <div class="hero-badge">Швидкий перехід у товар</div>
                        </div>
                    </div>
                </div>
            </section>

            {quick_tiles}

            <section>
                <div class="section-top">
                    <h2>{"Популярні пропозиції" if page_type == "home" else "Товари розділу"}</h2>
                    <p>{"Оберіть розділ або відкрийте конкретний товар для детального перегляду." if page_type != "olx" else "Переглядайте товари OLX у тому самому стилі сайту."}</p>
                </div>

                <div class="products-grid">
                    {products_html}
                </div>
            </section>

            <div class="footer-note">
                {SHOP_NAME} • Створено для зручного перегляду товарів
            </div>
        </main>
    </div>

    <script>
        function toggleTheme() {{
            document.body.classList.toggle('dark');
            localStorage.setItem('uniqlo_theme', document.body.classList.contains('dark') ? 'dark' : 'light');
        }}

        if (localStorage.getItem('uniqlo_theme') === 'dark') {{
            document.body.classList.add('dark');
        }}
    </script>
</body>
</html>"""


def collect_shafa_products(driver, url: str, limit: int = 24):
    driver.get(url)
    time.sleep(5)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.z0N6W7")
    result = []

    for card in cards:
        try:
            link_el = card.find_element(By.CSS_SELECTOR, "a.p1SYwW")
            img_el = card.find_element(By.CSS_SELECTOR, "img")
            price_el = card.find_element(By.CSS_SELECTOR, "p.D8o9s7")

            product_url = normalize_url(link_el.get_attribute("href"), "https://shafa.ua")
            image = img_el.get_attribute("src")
            title = (img_el.get_attribute("alt") or "Товар").strip()
            price = price_el.text.strip()

            brand = ""
            size = ""

            try:
                brand = card.find_element(By.CSS_SELECTOR, "p.i7zcRu").text.strip()
            except:
                pass

            try:
                size = card.find_element(By.CSS_SELECTOR, "p.NyHfpp").text.strip()
            except:
                pass

            if product_url and image and price:
                result.append({
                    "name": title,
                    "image": image,
                    "price": price,
                    "url": product_url,
                    "brand": brand,
                    "size": size
                })

            if len(result) >= limit:
                break
        except Exception:
            continue

    return result


def collect_olx_products(driver, url: str, limit: int = 24):
    driver.get(url)
    time.sleep(6)

    result = []
    used = set()

    title_links = driver.find_elements(By.CSS_SELECTOR, "a.css-1tqlkj0")

    for title_link in title_links:
        try:
            href = normalize_url(title_link.get_attribute("href"), "https://www.olx.ua")
            title = (title_link.text or "").strip()

            if not href or not title or href in used:
                continue

            wrapper = title_link
            depth = 0
            while wrapper is not None and depth < 8:
                try:
                    img_el = wrapper.find_element(By.XPATH, ".//preceding::img[1]")
                    if img_el:
                        break
                except:
                    pass
                wrapper = wrapper.find_element(By.XPATH, "./..")
                depth += 1

            image = ""
            try:
                image = img_el.get_attribute("src")
            except:
                image = ""

            if not image:
                continue

            price = "Переглянути оголошення"

            try:
                container = title_link.find_element(By.XPATH, "./ancestor::div[contains(@class,'css-13aawz3')][1]")
                text = container.text.strip()
                for line in text.splitlines():
                    line = line.strip()
                    if "грн" in line or "$" in line or "€" in line:
                        price = line
                        break
            except:
                pass

            result.append({
                "name": title,
                "image": image,
                "price": price,
                "url": href,
                "brand": "OLX",
                "size": ""
            })
            used.add(href)

            if len(result) >= limit:
                break

        except Exception:
            continue

    if not result:
        result.append({
            "name": "Переглянути всі товари на OLX",
            "image": AVATAR_URL,
            "price": "Відкрити OLX",
            "url": OLX_PROFILE_URL,
            "brand": "OLX",
            "size": ""
        })

    return result


def run_git():
    subprocess.run(["git", "add", "."], cwd=BASE_DIR)
    subprocess.run(["git", "commit", "-m", "Auto update full site"], cwd=BASE_DIR)
    subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR)


def main():
    print("Запуск оновлення сайту...")

    driver = make_driver()

    try:
        print("Збір головної сторінки Shafa...")
        home_products = collect_shafa_products(driver, SHAFA_PROFILE_URL, limit=12)
        save_root_index(render_page("Головна", "/", home_products, page_type="home"))
        print(f"Головна: {len(home_products)} товарів")

        print("Збір категорій Shafa...")
        for category in SHAFA_CATEGORIES:
            print(f"  {category['title']} -> /{category['slug']}/")
            products = collect_shafa_products(driver, category["url"], limit=24)
            save_folder_page(category["slug"], render_page(category["title"], f"/{category['slug']}/", products, page_type="category"))
            print(f"    готово: {len(products)} товарів")

        print("Збір OLX...")
        olx_products = collect_olx_products(driver, OLX_PROFILE_URL, limit=24)
        save_folder_page("olx", render_page("OLX", "/olx/", olx_products, page_type="olx"))
        print(f"OLX: {len(olx_products)} товарів")

    finally:
        driver.quit()

    print("Відправка на GitHub...")
    run_git()
    print("Готово. Сайт оновлено.")


if __name__ == "__main__":
    main()