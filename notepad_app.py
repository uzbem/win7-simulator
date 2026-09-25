"""
notepad_app.py
--------------
Windows 7 Bloknot (Notepad) dasturining simulyatsiyasi.

Funksiyalar:
 - Matn yozish (TextInput)
 - Joriy matnni .txt fayl sifatida saqlash (nom kiritish orqali)
 - Saqlangan fayllar ro'yxatidan birini tanlab qayta ochish

Fayllar ilovaning shaxsiy xotira papkasida (`App.user_data_dir/notes`)
saqlanadi - bu Android'da qo'shimcha ruxsatnomasiz ishlaydigan xavfsiz yo'l.
"""

import os
import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.app import App

logger = logging.getLogger("Win7Sim.Notepad")


def _notes_dir():
    """Bloknot fayllari saqlanadigan papkani qaytaradi, kerak bo'lsa yaratadi."""
    try:
        base = App.get_running_app().user_data_dir
    except Exception:
        base = "."
    path = os.path.join(base, "notes")
    os.makedirs(path, exist_ok=True)
    return path


class NotepadWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)

        self.text_input = TextInput(
            text="",
            font_size=dp(14),
            size_hint=(1, 1),
            hint_text="Matn kiriting...",
        )
        self.add_widget(self.text_input)

        toolbar = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(6))
        save_btn = Button(text="Saqlash")
        save_btn.bind(on_release=self._open_save_dialog)
        open_btn = Button(text="Ochish")
        open_btn.bind(on_release=self._open_load_dialog)
        new_btn = Button(text="Yangi")
        new_btn.bind(on_release=lambda *_: self._new_file())
        toolbar.add_widget(new_btn)
        toolbar.add_widget(save_btn)
        toolbar.add_widget(open_btn)
        self.add_widget(toolbar)

        self.status_label = Label(text="", size_hint=(1, None), height=dp(18), font_size=dp(11), color=(0.3, 0.3, 0.3, 1))
        self.add_widget(self.status_label)

        self._current_filename = None

    def _new_file(self):
        self.text_input.text = ""
        self._current_filename = None
        self.status_label.text = "Yangi hujjat"

    def _open_save_dialog(self, *args):
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(8))
        name_input = TextInput(
            text=self._current_filename or "yangi_fayl.txt",
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
        )
        box.add_widget(Label(text="Fayl nomini kiriting:", size_hint=(1, None), height=dp(24)))
        box.add_widget(name_input)

        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(6))
        popup = Popup(title="Saqlash", content=box, size_hint=(0.85, 0.4))

        def do_save(*_):
            filename = name_input.text.strip()
            if not filename:
                return
            if not filename.endswith(".txt"):
                filename += ".txt"
            self._save_to_file(filename)
            popup.dismiss()

        confirm_btn = Button(text="Saqlash")
        confirm_btn.bind(on_release=do_save)
        cancel_btn = Button(text="Bekor qilish")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(confirm_btn)
        btn_row.add_widget(cancel_btn)
        box.add_widget(btn_row)

        popup.open()

    def _save_to_file(self, filename):
        try:
            path = os.path.join(_notes_dir(), filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_input.text)
            self._current_filename = filename
            self.status_label.text = f"Saqlandi: {filename}"
            logger.info("Fayl saqlandi: %s", path)
        except Exception as exc:
            logger.error("Faylni saqlashda xatolik: %s", exc)
            self.status_label.text = f"Xatolik: {exc}"

    def _open_load_dialog(self, *args):
        try:
            files = [f for f in os.listdir(_notes_dir()) if f.endswith(".txt")]
        except Exception as exc:
            logger.error("Fayllar ro'yxatini olishda xatolik: %s", exc)
            files = []

        box = BoxLayout(orientation="vertical", spacing=dp(4), padding=dp(8))
        if not files:
            box.add_widget(Label(text="Saqlangan fayllar yo'q"))
        else:
            scroll = ScrollView(size_hint=(1, 1))
            grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(4))
            grid.bind(minimum_height=grid.setter("height"))
            popup = Popup(title="Faylni ochish", content=box, size_hint=(0.85, 0.6))

            for fname in files:
                btn = Button(text=fname, size_hint_y=None, height=dp(40))

                def make_cb(name=fname, p=popup):
                    def cb(*_):
                        self._load_from_file(name)
                        p.dismiss()
                    return cb

                btn.bind(on_release=make_cb())
                grid.add_widget(btn)
            scroll.add_widget(grid)
            box.add_widget(scroll)
            popup.open()
            return

        popup = Popup(title="Faylni ochish", content=box, size_hint=(0.85, 0.4))
        popup.open()

    def _load_from_file(self, filename):
        try:
            path = os.path.join(_notes_dir(), filename)
            with open(path, "r", encoding="utf-8") as f:
                self.text_input.text = f.read()
            self._current_filename = filename
            self.status_label.text = f"Ochildi: {filename}"
            logger.info("Fayl ochildi: %s", path)
        except Exception as exc:
            logger.error("Faylni ochishda xatolik: %s", exc)
            self.status_label.text = f"Xatolik: {exc}"


def build_notepad_content():
    """DesktopScreen tomonidan chaqiriladigan factory funksiya."""
    return NotepadWidget()
