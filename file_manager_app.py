"""
file_manager_app.py
--------------------
Windows Explorer uslubidagi fayl menejeri simulyatsiyasi.

Android xotirasi bilan ishlash uchun ilovaning shaxsiy papkasidan
(`App.user_data_dir`) boshlanadi - bu qo'shimcha ruxsatnomalarsiz
(scoped storage cheklovlarisiz) ishonchli ishlaydi. Agar tashqi
xotiraga (`/sdcard/`) kirish kerak bo'lsa, runtime ruxsatnomalari
so'raladi (android_permissions.py orqali).
"""

import os
import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App

logger = logging.getLogger("Win7Sim.FileManager")


def _root_dir():
    try:
        base = App.get_running_app().user_data_dir
    except Exception:
        base = "."
    os.makedirs(base, exist_ok=True)
    return base


class FileManagerWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)
        self.current_path = _root_dir()

        # --- Manzil qatori ---
        path_bar = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(36), spacing=dp(4))
        self.path_label = Label(text=self.current_path, font_size=dp(11), halign="left", valign="middle")
        self.path_label.bind(size=self.path_label.setter("text_size"))
        up_btn = Button(text="⬆", size_hint=(None, 1), width=dp(40))
        up_btn.bind(on_release=lambda *_: self._go_up())
        path_bar.add_widget(up_btn)
        path_bar.add_widget(self.path_label)
        self.add_widget(path_bar)

        # --- Fayllar ro'yxati ---
        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)

        # --- Pastki asboblar paneli ---
        toolbar = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(6))
        new_folder_btn = Button(text="Yangi papka")
        new_folder_btn.bind(on_release=self._prompt_new_folder)
        refresh_btn = Button(text="Yangilash")
        refresh_btn.bind(on_release=lambda *_: self._refresh())
        toolbar.add_widget(new_folder_btn)
        toolbar.add_widget(refresh_btn)
        self.add_widget(toolbar)

        self._refresh()

    def _go_up(self):
        parent = os.path.dirname(self.current_path.rstrip(os.sep))
        root = _root_dir()
        # Ildiz papkadan yuqoriga chiqishga ruxsat bermaymiz (xavfsizlik)
        if parent and os.path.commonpath([os.path.abspath(parent), os.path.abspath(root)]) == os.path.abspath(root) or parent == root:
            self.current_path = parent if parent else root
            self._refresh()

    def _refresh(self):
        self.grid.clear_widgets()
        self.path_label.text = self.current_path
        try:
            entries = sorted(os.listdir(self.current_path))
        except Exception as exc:
            logger.error("Papkani o'qishda xatolik: %s", exc)
            self.grid.add_widget(Label(text=f"Xatolik: {exc}", size_hint_y=None, height=dp(30)))
            return

        if not entries:
            self.grid.add_widget(Label(text="(bo'sh papka)", size_hint_y=None, height=dp(30)))
            return

        for name in entries:
            full_path = os.path.join(self.current_path, name)
            is_dir = os.path.isdir(full_path)
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
            icon = "📁" if is_dir else "📄"
            item_btn = Button(text=f"{icon}  {name}", halign="left",
                               background_normal="", background_color=(0.93, 0.93, 0.96, 1),
                               color=(0.1, 0.1, 0.1, 1))
            item_btn.bind(on_release=lambda inst, p=full_path, d=is_dir: self._on_item_pressed(p, d))
            del_btn = Button(text="🗑", size_hint=(None, 1), width=dp(44))
            del_btn.bind(on_release=lambda inst, p=full_path: self._confirm_delete(p))
            row.add_widget(item_btn)
            row.add_widget(del_btn)
            self.grid.add_widget(row)

    def _on_item_pressed(self, path, is_dir):
        if is_dir:
            self.current_path = path
            self._refresh()
        else:
            logger.info("Fayl tanlandi: %s (ko'rish funksiyasi Bloknotda mavjud)", path)

    def _prompt_new_folder(self, *args):
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(8))
        name_input = TextInput(text="Yangi papka", multiline=False, size_hint=(1, None), height=dp(40))
        box.add_widget(Label(text="Papka nomi:", size_hint=(1, None), height=dp(24)))
        box.add_widget(name_input)

        popup = Popup(title="Yangi papka yaratish", content=box, size_hint=(0.85, 0.4))
        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(6))

        def do_create(*_):
            folder_name = name_input.text.strip()
            if folder_name:
                try:
                    os.makedirs(os.path.join(self.current_path, folder_name), exist_ok=True)
                    self._refresh()
                except Exception as exc:
                    logger.error("Papka yaratishda xatolik: %s", exc)
            popup.dismiss()

        create_btn = Button(text="Yaratish")
        create_btn.bind(on_release=do_create)
        cancel_btn = Button(text="Bekor qilish")
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(create_btn)
        btn_row.add_widget(cancel_btn)
        box.add_widget(btn_row)
        popup.open()

    def _confirm_delete(self, path):
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(8))
        box.add_widget(Label(text=f"O'chirilsinmi?\n{os.path.basename(path)}"))
        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(44), spacing=dp(6))
        popup = Popup(title="Tasdiqlash", content=box, size_hint=(0.85, 0.4))

        def do_delete(*_):
            try:
                if os.path.isdir(path):
                    os.rmdir(path)  # faqat bo'sh papkalarni o'chiramiz (xavfsizlik)
                else:
                    os.remove(path)
                self._refresh()
            except Exception as exc:
                logger.error("O'chirishda xatolik: %s", exc)
            popup.dismiss()

        yes_btn = Button(text="Ha")
        yes_btn.bind(on_release=do_delete)
        no_btn = Button(text="Yo'q")
        no_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(yes_btn)
        btn_row.add_widget(no_btn)
        box.add_widget(btn_row)
        popup.open()


def build_file_manager_content():
    return FileManagerWidget()
