import sqlite3
import subprocess
from pathlib import Path

from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "shop.db"

# ==========================================
# НАЛАШТУВАННЯ (ОБОВ'ЯЗКОВО ЗАПОВНИ)
# ==========================================
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"  # Встав токен від @BotFather
ADMIN_ID = 123456789  # Встав свій ID
BOT_USERNAME = "UniqLow_bot"  # Встав юзернейм бота без @

# ==========================================
# МЕНЮ ТА КНОПКИ
# ==========================================
MENU = [
    ["🛍 Замовлення", "💬 Підтримка"],
    ["⭐ Залишити відгук"]
]
CANCEL_BTN = [["❌ Скасувати"]]

ORDER_INPUT = 1
SUPPORT_INPUT = 2
REVIEW_STARS = 3
REVIEW_TEXT = 4


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category_slug TEXT NOT NULL,
        price TEXT NOT NULL,
        image_url TEXT NOT NULL,
        item_url TEXT NOT NULL UNIQUE,
        source TEXT NOT NULL DEFAULT 'manual',
        brand TEXT DEFAULT '',
        size TEXT DEFAULT ''
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_user_id INTEGER NOT NULL UNIQUE,
        tg_username TEXT,
        display_name TEXT NOT NULL,
        stars INTEGER NOT NULL,
        text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_user_id INTEGER NOT NULL,
        tg_username TEXT,
        display_name TEXT NOT NULL,
        query_text TEXT NOT NULL,
        found_title TEXT,
        found_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_user_id INTEGER NOT NULL,
        tg_username TEXT,
        display_name TEXT NOT NULL,
        message_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def main_keyboard():
    return ReplyKeyboardMarkup(MENU, resize_keyboard=True)


def cancel_keyboard():
    return ReplyKeyboardMarkup(CANCEL_BTN, resize_keyboard=True)


def stars_keyboard():
    return ReplyKeyboardMarkup([
        ["5 ⭐⭐⭐⭐⭐", "4 ⭐⭐⭐⭐"],
        ["3 ⭐⭐⭐", "2 ⭐⭐", "1 ⭐"],
        ["❌ Скасувати"]
    ], resize_keyboard=True)


def find_product(query: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT title, price, item_url
    FROM products
    WHERE lower(title) LIKE lower(?) OR item_url = ?
    LIMIT 1
    """, (f"%{query.strip()}%", query.strip()))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"title": row[0], "price": row[1], "item_url": row[2]}
    return None


def has_review(user_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM reviews WHERE tg_user_id = ?", (user_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def save_review(user, stars: int, text: str):
    conn = get_conn()
    cur = conn.cursor()
    display_name = (user.full_name or user.username or "Покупець").strip()
    cur.execute("""
    INSERT INTO reviews (tg_user_id, tg_username, display_name, stars, text)
    VALUES (?, ?, ?, ?, ?)
    """, (user.id, user.username, display_name, stars, text.strip() if text else ""))
    conn.commit()
    conn.close()


def save_order(user, query_text: str, found_product):
    conn = get_conn()
    cur = conn.cursor()
    display_name = (user.full_name or user.username or "Покупець").strip()
    cur.execute("""
    INSERT INTO orders (tg_user_id, tg_username, display_name, query_text, found_title, found_url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user.id, user.username, display_name, query_text.strip(),
        found_product["title"] if found_product else None,
        found_product["item_url"] if found_product else None
    ))
    conn.commit()
    conn.close()


def save_support(user, message_text: str):
    conn = get_conn()
    cur = conn.cursor()
    display_name = (user.full_name or user.username or "Покупець").strip()
    cur.execute("""
    INSERT INTO support_messages (tg_user_id, tg_username, display_name, message_text)
    VALUES (?, ?, ?, ?)
    """, (user.id, user.username, display_name, message_text.strip()))
    conn.commit()
    conn.close()


# Функція, яка дає команду оновити сайт після нового відгуку
def trigger_site_rebuild():
    try:
        subprocess.Popen(["python", "auto_shop.py"], cwd=BASE_DIR)
        print("Сайт відправлено на оновлення у фоні.")
    except Exception as e:
        print(f"Не вдалося оновити сайт автоматично: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Вітаємо в магазині UniqLow!</b>\n\n"
        "Тут ви можете:\n"
        "🛍 <b>Оформити замовлення</b> та гарантовано отримати знижку -10%\n"
        "💬 <b>Звернутися в підтримку</b>\n"
        "⭐ <b>Залишити відгук</b> про нашу роботу\n\n"
        "<i>Оберіть потрібний пункт у меню нижче 👇</i>"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "🛍 Замовлення":
        await update.message.reply_text(
            "Надішліть назву товару або посилання на нього.\n\n"
            "<i>(Менеджер отримає ваш запит та зв'яжеться з вами для уточнення деталей)</i>",
            reply_markup=cancel_keyboard(), parse_mode=ParseMode.HTML
        )
        return ORDER_INPUT

    if text == "💬 Підтримка":
        await update.message.reply_text(
            "Опишіть вашу проблему або запитання одним повідомленням.",
            reply_markup=cancel_keyboard()
        )
        return SUPPORT_INPUT

    if text == "⭐ Залишити відгук":
        if has_review(update.effective_user.id):
            await update.message.reply_text(
                "Дякуємо! Ви вже залишили відгук. Один користувач може залишити лише один відгук.",
                reply_markup=main_keyboard()
            )
            return ConversationHandler.END

        await update.message.reply_text(
            "Оцініть наш магазин від 1 до 5 зірок:",
            reply_markup=stars_keyboard()
        )
        return REVIEW_STARS

    await update.message.reply_text("Будь ласка, оберіть дію з меню нижче 👇", reply_markup=main_keyboard())
    return ConversationHandler.END


async def order_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "❌ Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    product = find_product(text)
    save_order(update.effective_user, text, product)

    user = update.effective_user
    username = f"@{user.username}" if user.username else "прихований username"
    display_name = user.full_name or "Покупець"

    if product:
        admin_text = (
            "🚨 <b>НОВЕ ЗАМОВЛЕННЯ</b> 🚨\n\n"
            f"👤 <b>Покупець:</b> {display_name} ({username})\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
            f"📝 <b>Запит:</b> {text}\n"
            f"📦 <b>Знайдений товар:</b> {product['title']}\n"
            f"💰 <b>Ціна (без знижки):</b> {product['price']}\n"
            f"🔗 <b>Посилання:</b> {product['item_url']}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode=ParseMode.HTML)

        await update.message.reply_text(
            "✅ <b>Ваше замовлення прийнято!</b>\n\n"
            "Менеджер вже отримав повідомлення та незабаром зв’яжеться з вами.",
            reply_markup=main_keyboard(), parse_mode=ParseMode.HTML
        )
    else:
        admin_text = (
            "🚨 <b>НОВИЙ ЗАПИТ (без точного збігу)</b> 🚨\n\n"
            f"👤 <b>Покупець:</b> {display_name} ({username})\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
            f"📝 <b>Запит:</b> {text}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode=ParseMode.HTML)

        await update.message.reply_text(
            "✅ <b>Запит отримано!</b>\n\n"
            "Ми не знайшли точного збігу в базі, але менеджер перегляне ваше повідомлення та напише вам.",
            reply_markup=main_keyboard(), parse_mode=ParseMode.HTML
        )

    return ConversationHandler.END


async def support_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "❌ Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    save_support(update.effective_user, text)

    user = update.effective_user
    username = f"@{user.username}" if user.username else "прихований username"
    display_name = user.full_name or "Користувач"

    admin_text = (
        "💬 <b>ПІДТРИМКА</b> 💬\n\n"
        f"👤 <b>Від:</b> {display_name} ({username})\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
        f"<b>Повідомлення:</b>\n{text}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode=ParseMode.HTML)

    await update.message.reply_text(
        "✅ <b>Звернення надіслано.</b> Ми відповімо вам якнайшвидше.",
        reply_markup=main_keyboard(), parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END


async def review_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "❌ Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    stars = 0
    if "5" in text:
        stars = 5
    elif "4" in text:
        stars = 4
    elif "3" in text:
        stars = 3
    elif "2" in text:
        stars = 2
    elif "1" in text:
        stars = 1

    if stars == 0:
        await update.message.reply_text("Будь ласка, натисніть на одну з кнопок нижче 👇", reply_markup=stars_keyboard())
        return REVIEW_STARS

    context.user_data["review_stars"] = stars

    await update.message.reply_text(
        "Напишіть короткий коментар до відгуку (або надішліть «-», щоб залишити тільки зірки).",
        reply_markup=ReplyKeyboardMarkup([["-"], ["❌ Скасувати"]], resize_keyboard=True)
    )
    return REVIEW_TEXT


async def review_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "❌ Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    stars = context.user_data.get("review_stars", 5)
    review_text_value = "" if text == "-" else text

    try:
        save_review(update.effective_user, stars, review_text_value)
    except sqlite3.IntegrityError:
        await update.message.reply_text("Ви вже залишили відгук раніше.", reply_markup=main_keyboard())
        return ConversationHandler.END

    user = update.effective_user
    username = f"@{user.username}" if user.username else "прихований username"
    display_name = user.full_name or "Користувач"

    admin_text = (
        "⭐ <b>НОВИЙ ВІДГУК</b> ⭐\n\n"
        f"👤 <b>Від:</b> {display_name} ({username})\n"
        f"Оцінка: {stars}/5\n"
        f"Текст: {review_text_value if review_text_value else 'Без тексту'}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode=ParseMode.HTML)

    await update.message.reply_text(
        "❤️ <b>Дякуємо за ваш відгук!</b> Він з'явиться на сайті за кілька хвилин.",
        reply_markup=main_keyboard(), parse_mode=ParseMode.HTML
    )

    # Викликаємо оновлення сайту у фоні
    trigger_site_rebuild()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
    return ConversationHandler.END


def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE" or ADMIN_ID == 123456789:
        print("ПОМИЛКА: Спочатку встав свій BOT_TOKEN та ADMIN_ID у файл bot.py!")
        return

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
        states={
            ORDER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_input)],
            SUPPORT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_input)],
            REVIEW_STARS: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_stars)],
            REVIEW_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)

    print("✅ Бот успішно запущено. Натисни /start у Телеграмі.")
    app.run_polling()


if __name__ == "__main__":
    main()