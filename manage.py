import subprocess
import threading
import time
import sys
import os

bot_process = None
autoshop_running = True


def add_to_startup():
    """Додає цей файл в автозавантаження Windows"""
    bat_path = r'C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\UniqLow_Start.bat'
    bat_path = os.path.expandvars(bat_path)
    with open(bat_path, "w") as bat_file:
        bat_file.write(f'cd /d "{os.getcwd()}"\nstart cmd /k "python manager.py"')
    print("✅ Додано в автозавантаження Windows!")


def run_autoshop():
    print("▶️ [AutoShop] Запущено щогодинне оновлення.")
    while autoshop_running:
        print("⏳ [AutoShop] Оновлюю сайт та базу...")
        subprocess.run(["python", "auto_shop.py"])
        # Чекаємо 1 годину (3600 сек) невеликими кроками, щоб швидко реагувати на /stop
        for _ in range(3600):
            if not autoshop_running: break
            time.sleep(1)


def main():
    global bot_process, autoshop_running
    add_to_startup()

    print("▶️ [Бот] Запускається...")
    bot_process = subprocess.Popen(["python", "bot.py"])

    thread = threading.Thread(target=run_autoshop, daemon=True)
    thread.start()

    print(
        "\n🚀 UniqLow працює! Команди:\n/stop - Зупинити все\n/bot_stop - Зупинити бота\n/auto_shop_stop - Зупинити оновлення сайту\n")

    while True:
        cmd = input("").strip()
        if cmd == "/stop":
            autoshop_running = False
            if bot_process: bot_process.terminate()
            print("🛑 Все зупинено. Вихід.")
            sys.exit(0)
        elif cmd == "/bot_stop":
            if bot_process: bot_process.terminate(); print("🛑 Бот зупинений.")
        elif cmd == "/auto_shop_stop":
            autoshop_running = False;
            print("🛑 Оновлення сайту зупинено.")


if __name__ == "__main__":
    main()