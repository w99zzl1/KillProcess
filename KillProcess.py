import psutil
import win32gui
import win32process
import keyboard
import threading
import ctypes
import sys
import os
import tkinter as tk
from tkinter import ttk
import json
import winreg
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Константы
APP_NAME = "KillProcess"
CONFIG_FILE = 'tray_config.json'
DEFAULT_CONFIG = {
    "autostart": False,
    "hotkey": "ctrl+shift+k"
}

# ------------------------ РЕСУРСЫ ------------------------

def resource_path(relative_path):
    """Для корректной работы с PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ICON_PATH = resource_path("icon.ico")

# ------------------------ КОНФИГ ------------------------

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r") as f:
        config_data = json.load(f)
        if "hotkey" not in config_data:
            config_data["hotkey"] = DEFAULT_CONFIG["hotkey"]
            save_config(config_data)
        return config_data

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

# ------------------------ ФУНКЦИИ ------------------------

def kill_active_window():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = psutil.Process(pid)
            proc.kill()
        except Exception:
            pass

def listen_hotkey():
    keyboard.add_hotkey(config["hotkey"], kill_active_window)
    keyboard.wait()

def run_hotkey_thread():
    thread = threading.Thread(target=listen_hotkey, daemon=True)
    thread.start()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_executable_path():
    return sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

def toggle_autostart(icon, item):
    config["autostart"] = not config["autostart"]
    set_autostart(config["autostart"])
    save_config(config)
    icon.update_menu()

def set_autostart(enable):
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    exe_path = get_executable_path()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_ALL_ACCESS) as reg:
            if enable:
                winreg.SetValueEx(reg, APP_NAME, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(reg, APP_NAME)
                except FileNotFoundError:
                    pass
    except Exception:
        pass

def on_quit(icon=None, item=None):
    icon.stop()
    sys.exit()

def create_icon_image():
    try:
        return Image.open(ICON_PATH)
    except Exception:
        img = Image.new("RGB", (64, 64), "black")
        draw = ImageDraw.Draw(img)
        draw.rectangle((16, 16, 48, 48), fill="red")
        return img

def set_window_icon(window):
    try:
        if os.path.exists(ICON_PATH):
            window.iconbitmap(ICON_PATH)
    except Exception as e:
        print(f"Не удалось установить иконку: {e}")

def on_change_hotkey(icon):
    hotkey_window = tk.Tk()
    hotkey_window.title("Изменить хоткей")
    set_window_icon(hotkey_window)
    hotkey_window.geometry("400x200+%d+%d" % (
        (hotkey_window.winfo_screenwidth() - 400) // 2,
        (hotkey_window.winfo_screenheight() - 200) // 2))

    label = tk.Label(hotkey_window, text="Нажмите новую комбинацию клавиш:")
    label.pack(pady=10)

    hotkey_display = tk.Label(hotkey_window, text="Ожидание ввода...", font=('Arial', 14))
    hotkey_display.pack(pady=10)

    cancel_button = tk.Button(hotkey_window, text="Отмена", command=hotkey_window.destroy)
    cancel_button.pack(pady=10)

    def capture_hotkey():
        hotkey = keyboard.read_hotkey(suppress=True)
        config["hotkey"] = hotkey
        save_config(config)
        hotkey_display.config(text=f"Новая комбинация: {hotkey}")
        hotkey_window.after(1500, hotkey_window.destroy)
        keyboard.clear_all_hotkeys()
        keyboard.add_hotkey(config["hotkey"], kill_active_window)
        icon.update_menu()

    threading.Thread(target=capture_hotkey, daemon=True).start()
    hotkey_window.mainloop()

def run_tray():
    icon = Icon("KillProcess", create_icon_image(), "KillProcess")
    menu = Menu(
        MenuItem(lambda icon: f"Хоткей: {config['hotkey']}", None, enabled=False),
        MenuItem(lambda icon: "Отключить автозапуск" if config["autostart"] else "Включить автозапуск", toggle_autostart),
        MenuItem("Изменить хоткей", lambda icon, item: on_change_hotkey(icon)),
        MenuItem("Выход", on_quit)
    )
    icon.menu = menu
    icon.run()

# ------------------------ ЗАПУСК ------------------------

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    if config["autostart"]:
        set_autostart(True)

    run_hotkey_thread()
    run_tray()
