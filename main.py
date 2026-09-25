"""
main.py
-------
Windows 7 Mobile Simulator - ilovaning kirish nuqtasi.

Bu fayl:
 1. Logging (xatolarni yozib borish) tizimini sozlaydi.
 2. Android runtime ruxsatnomalarini (Storage) so'raydi.
 3. Asosiy DesktopScreen'ni ilova oynasiga yuklaydi.
 4. Ekran orientatsiyasi (portrait/landscape) o'zgarishini kuzatadi.

Ishga tushirish (kompyuterda, sinov uchun):
    pip install -r requirements.txt
    python main.py

Android uchun APK yig'ish bo'yicha ko'rsatma README.md faylida.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform

from screens.desktop_screen import DesktopScreen


def setup_logging():
    """
    Xatolar va istisnolarni faylga va konsolga yozib boruvchi logging
    tizimini sozlaydi (try-except bilan himoyalangan - log sozlamasi
    o'zi xato bersa ham ilova ishlashda davom etsin).
    """
    try:
        log_dir = os.path.join(os.path.expanduser("~"), ".win7sim_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")

        handler = RotatingFileHandler(log_file, maxBytes=512 * 1024, backupCount=2, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)

        root_logger = logging.getLogger("Win7Sim")
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    except Exception as exc:
        # Log sozlanmasa ham, oddiy consol chiqishi bilan davom etamiz
        print(f"Logging sozlashda xatolik: {exc}")


def request_android_permissions():
    """
    Android qurilmasida ishlaganda xotiraga (Storage) kirish uchun
    runtime ruxsatnomalarini so'raydi. Kompyuterda ishga tushirilganda
    (android moduli mavjud bo'lmaganda) xatosiz o'tkazib yuboriladi.
    """
    if platform != "android":
        return
    try:
        from android.permissions import request_permissions, Permission  # noqa
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
        logging.getLogger("Win7Sim").info("Android ruxsatnomalari so'raldi.")
    except Exception as exc:
        logging.getLogger("Win7Sim").warning("Android ruxsatnomalarini so'rashda xatolik: %s", exc)


class Win7SimulatorApp(App):
    """
    Ilovaning bosh klassi (Clean Architecture: bu qatlam faqat
    "composition root" vazifasini bajaradi - ya'ni barcha modullarni
    bog'lab, ilovani ishga tushiradi; biznes-mantiq bu yerda yozilmagan).
    """

    def build(self):
        self.title = "Windows 7 Mobile Simulator"
        Window.softinput_mode = "below_target"  # klaviatura ochilganda kontent surilsin

        logger = logging.getLogger("Win7Sim.App")
        try:
            desktop = DesktopScreen()
            logger.info("DesktopScreen muvaffaqiyatli yuklandi.")
            return desktop
        except Exception as exc:
            logger.critical("Ilovani ishga tushirishda kritik xatolik: %s", exc)
            # Ilova butunlay qulab tushmasligi uchun oddiy xato ekranini qaytaramiz
            from kivy.uix.label import Label
            return Label(text=f"Ilova yuklanmadi:\n{exc}")

    def on_pause(self):
        # Android'da ilova fonga o'tganda holatni saqlab, ishlashda davom etish
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    setup_logging()
    request_android_permissions()
    Win7SimulatorApp().run()
