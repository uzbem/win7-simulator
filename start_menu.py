"""
start_menu.py
-------------
Windows 7 Start Menyusining simulyatsiyasi.

Sensor Start tugmasiga bosilganda pastdan yuqoriga silliq (slide-up)
animatsiya bilan ochiladi. Chap ustunda dasturlar ro'yxati, o'ng ustunda
tezkor havolalar ("Mening hujjatlarim", "Rasmlar", "Xotira", "Sozlamalar")
va pastda "Tizimdan chiqish" tugmasi joylashadi.
"""

import logging
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import BooleanProperty

logger = logging.getLogger("Win7Sim.StartMenu")

MENU_HEIGHT = dp(360)
MENU_WIDTH = dp(300)


class StartMenu(FloatLayout):
    """
    on_app_selected(app_id): foydalanuvchi chap ustundan dastur tanlaganda
    on_shutdown(): "Tizimdan chiqish" bosilganda
    on_quick_link(link_name): o'ng ustundagi tezkor havolalar bosilganda
    """

    is_open = BooleanProperty(False)

    APP_LIST = [
        ("notepad", "Bloknot"),
        ("calculator", "Kalkulyator"),
        ("file_manager", "Fayl Menejeri"),
        ("media_player", "Media Player"),
        ("cmd", "Buyruqlar satri"),
    ]

    QUICK_LINKS = ["Mening hujjatlarim", "Rasmlar", "Xotira", "Sozlamalar"]

    def __init__(self, on_app_selected, on_shutdown, on_quick_link=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(MENU_WIDTH, MENU_HEIGHT), **kwargs)
        self._on_app_selected = on_app_selected
        self._on_shutdown = on_shutdown
        self._on_quick_link = on_quick_link or (lambda name: None)

        with self.canvas.before:
            Color(0.08, 0.12, 0.22, 0.97)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        root_box = BoxLayout(orientation="vertical", size_hint=(1, 1))

        # --- Yuqori qism: ikki ustunli (Apps | Quick Links) ---
        columns = BoxLayout(orientation="horizontal", size_hint=(1, 1))

        left_col = BoxLayout(orientation="vertical", size_hint=(0.62, 1), padding=dp(6), spacing=dp(4))
        left_col.add_widget(Label(text="Dasturlar", size_hint=(1, None), height=dp(24),
                                   color=(1, 1, 1, 0.7), font_size=dp(12)))
        for app_id, title in self.APP_LIST:
            btn = Button(text=title, size_hint=(1, None), height=dp(42),
                         background_normal="", background_color=(0.15, 0.2, 0.35, 1),
                         color=(1, 1, 1, 1))
            btn.bind(on_release=lambda inst, aid=app_id: self._select_app(aid))
            left_col.add_widget(btn)
        columns.add_widget(left_col)

        right_col = BoxLayout(orientation="vertical", size_hint=(0.38, 1), padding=dp(6), spacing=dp(4))
        right_col.add_widget(Label(text="Tezkor", size_hint=(1, None), height=dp(24),
                                    color=(1, 1, 1, 0.7), font_size=dp(12)))
        for link in self.QUICK_LINKS:
            btn = Button(text=link, size_hint=(1, None), height=dp(42), font_size=dp(11),
                         background_normal="", background_color=(0.12, 0.16, 0.28, 1),
                         color=(1, 1, 1, 1))
            btn.bind(on_release=lambda inst, name=link: self._on_quick_link(name))
            right_col.add_widget(btn)
        columns.add_widget(right_col)

        root_box.add_widget(columns)

        # --- Pastki qism: Tizimdan chiqish ---
        shutdown_btn = Button(text="Tizimdan chiqish", size_hint=(1, None), height=dp(44),
                               background_normal="", background_color=(0.55, 0.15, 0.15, 1),
                               color=(1, 1, 1, 1), bold=True)
        shutdown_btn.bind(on_release=lambda *_: self._on_shutdown())
        root_box.add_widget(shutdown_btn)

        self.add_widget(root_box)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _select_app(self, app_id):
        self.close()
        self._on_app_selected(app_id)

    # ------------------------------------------------------------------
    # Ochilish / yopilish animatsiyasi
    # ------------------------------------------------------------------
    def open_at(self, x, taskbar_top):
        """Menyuni berilgan X koordinatada, taskbar tepasidan animatsiya bilan ochadi."""
        self.pos = (x, taskbar_top)
        self.opacity = 0
        self.is_open = True
        target_y = taskbar_top
        self.y = taskbar_top - dp(30)
        anim = Animation(y=target_y, opacity=1, duration=0.16, t="out_quad")
        anim.start(self)

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        anim = Animation(opacity=0, duration=0.12)

        def _remove(*_):
            if self.parent:
                self.parent.remove_widget(self)

        anim.bind(on_complete=_remove)
        anim.start(self)
