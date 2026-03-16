import sqlite3
from pathlib import Path

from telegram import Update, ReplyKeyboardMarkup
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

BOT_TOKEN = "8530069357:AAE4QpQvPC8FzGI1R4B0Eqzn2hYeq3RlnP0"
ADMIN_ID = 5017672713
BOT_USERNAME = "UniqLowbot"

MENU = [["Замовлення", "Підтримка"], ["Відгук", "Мій ID"]]

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
        source TEXT NOT NULL DEFAULT 'manual'
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


def stars_keyboard():
    return ReplyKeyboardMarkup([["1", "2", "3", "4", "5"], ["Скасувати"]], resize_keyboard=True)


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
        user.id,
        user.username,
        display_name,
        query_text.strip(),
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Вітаю в боті магазину JulyShop.\n\n"
        "Тут можна:\n"
        "• оформити замовлення\n"
        "• звернутися в підтримку\n"
        "• залишити відгук\n\n"
        "При оформленні замовлення через Telegram діє знижка 10%."
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ваш Telegram ID: {update.effective_user.id}", reply_markup=main_keyboard())


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Замовлення":
        await update.message.reply_text(
            "Надішліть назву товару або посилання на нього.",
            reply_markup=ReplyKeyboardMarkup([["Скасувати"]], resize_keyboard=True)
        )
        return ORDER_INPUT

    if text == "Підтримка":
        await update.message.reply_text(
            "Опишіть вашу проблему або запитання одним повідомленням.",
            reply_markup=ReplyKeyboardMarkup([["Скасувати"]], resize_keyboard=True)
        )
        return SUPPORT_INPUT

    if text == "Відгук":
        if has_review(update.effective_user.id):
            await update.message.reply_text(
                "Ви вже залишили відгук. Один користувач може залишити лише один відгук.",
                reply_markup=main_keyboard()
            )
            return ConversationHandler.END

        await update.message.reply_text("Оцініть магазин від 1 до 5 зірок.", reply_markup=stars_keyboard())
        return REVIEW_STARS

    if text == "Мій ID":
        await update.message.reply_text(f"Ваш Telegram ID: {update.effective_user.id}", reply_markup=main_keyboard())
        return ConversationHandler.END

    await update.message.reply_text("Оберіть дію з меню.", reply_markup=main_keyboard())
    return ConversationHandler.END


async def order_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    product = find_product(text)
    save_order(update.effective_user, text, product)

    user = update.effective_user
    username = f"@{user.username}" if user.username else "без username"
    display_name = user.full_name or "Покупець"

    if product:
        admin_text = (
            "Нове замовлення\n\n"
            f"Покупець: {display_name}\n"
            f"Username: {username}\n"
            f"User ID: {user.id}\n\n"
            f"Запит: {text}\n"
            f"Знайдений товар: {product['title']}\n"
            f"Ціна: {product['price']}\n"
            f"Посилання: {product['item_url']}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

        await update.message.reply_text(
            "Ваше замовлення прийнято.\n"
            "Менеджер отримає повідомлення та зв’яжеться з вами.",
            reply_markup=main_keyboard()
        )
    else:
        admin_text = (
            "Нове замовлення без точного збігу\n\n"
            f"Покупець: {display_name}\n"
            f"Username: {username}\n"
            f"User ID: {user.id}\n\n"
            f"Запит: {text}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

        await update.message.reply_text(
            "Запит отримано. Точний товар не знайдено в базі, але менеджер перегляне ваше повідомлення.",
            reply_markup=main_keyboard()
        )

    return ConversationHandler.END


async def support_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    save_support(update.effective_user, text)

    user = update.effective_user
    username = f"@{user.username}" if user.username else "без username"
    display_name = user.full_name or "Користувач"

    admin_text = (
        "Нове звернення в підтримку\n\n"
        f"Користувач: {display_name}\n"
        f"Username: {username}\n"
        f"User ID: {user.id}\n\n"
        f"Повідомлення:\n{text}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

    await update.message.reply_text(
        "Ваше звернення передано в підтримку.",
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END


async def review_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    if text not in {"1", "2", "3", "4", "5"}:
        await update.message.reply_text("Оберіть число від 1 до 5.", reply_markup=stars_keyboard())
        return REVIEW_STARS

    context.user_data["review_stars"] = int(text)

    await update.message.reply_text(
        "Напишіть текст відгуку або надішліть '-' щоб пропустити.",
        reply_markup=ReplyKeyboardMarkup([["-"], ["Скасувати"]], resize_keyboard=True)
    )
    return REVIEW_TEXT


async def review_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Скасувати":
        await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
        return ConversationHandler.END

    stars = context.user_data.get("review_stars")
    review_text_value = "" if text == "-" else text

    try:
        save_review(update.effective_user, stars, review_text_value)
    except sqlite3.IntegrityError:
        await update.message.reply_text("Ви вже залишили відгук раніше.", reply_markup=main_keyboard())
        return ConversationHandler.END

    user = update.effective_user
    username = f"@{user.username}" if user.username else "без username"
    display_name = user.full_name or "Користувач"

    admin_text = (
        "Новий відгук\n\n"
        f"Користувач: {display_name}\n"
        f"Username: {username}\n"
        f"User ID: {user.id}\n\n"
        f"Оцінка: {stars}/5\n"
        f"Текст: {review_text_value if review_text_value else 'Без тексту'}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

    await update.message.reply_text(
        "Дякуємо за відгук.",
        reply_markup=main_keyboard()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Дію скасовано.", reply_markup=main_keyboard())
    return ConversationHandler.END


def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("Спочатку вставте BOT_TOKEN у bot.py")
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
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(conversation)

    print("Бот запущено...")
    app.run_polling()


if __name__ == "__main__":
    main()