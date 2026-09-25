"""
taskbar.py
----------
Windows 7 "Vazifalar paneli" (Taskbar) simulyatsiyasi.

Ekranning pastida doimiy joylashadi:
 - chapda shaffof orb-uslubidagi Start tugmasi
 - o'rtada ochiq turgan ilovalarning aktiv piktogramma-tugmalari
 - o'ngda soat/sana va batareya foizi

Taskbar tashqi dunyo bilan faqat callback orqali gaplashadi
(on_start_pressed, on_app_icon_pressed) - bu uni qayta ishlatishga qulay qiladi.
"""

import logging
import datetime
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

logger = logging.getLogger("Win7Sim.Taskbar")

try:
    # Android qurilmasida haqiqiy batareya foizini olishga urinish
    from plyer import battery
    HAS_BATTERY_API = True
except Exception:
    HAS_BATTERY_API = False


TASKBAR_HEIGHT = dp(48)


class Taskbar(BoxLayout):
    def __init__(self, on_start_pressed, on_app_icon_pressed, **kwargs):
        super().__init__(orientation="horizontal", size_hint=(1, None), height=TASKBAR_HEIGHT, **kwargs)
        self._on_start_pressed = on_start_pressed
        self._on_app_icon_pressed = on_app_icon_pressed
        self._running_buttons = {}  # app_id -> Button

        with self.canvas.before:
            Color(0.1, 0.18, 0.32, 0.92)  # Windows 7 taskbar ko'k-qorong'u rangi
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # --- Start orb tugmasi (chap) ---
        self.start_btn = Button(
            text="[b]⊙[/b]",
            markup=True,
            font_size=dp(20),
            size_hint=(None, 1),
            width=dp(56),
            background_normal="",
            background_color=(0.15, 0.55, 0.15, 1),
            color=(1, 1, 1, 1),
        )
        self.start_btn.bind(on_release=lambda *_: self._on_start_pressed())
        self.add_widget(self.start_btn)

        # --- Ochiq ilovalar joylashadigan gorizontal scroll maydon ---
        self.apps_scroll = ScrollView(size_hint=(1, 1), do_scroll_y=False)
        self.apps_box = BoxLayout(orientation="horizontal", size_hint=(None, 1), spacing=dp(4), padding=(dp(4), 0))
        self.apps_box.bind(minimum_width=self.apps_box.setter("width"))
        self.apps_scroll.add_widget(self.apps_box)
        self.add_widget(self.apps_scroll)

        # --- O'ng taraf: batareya + soat/sana ---
        right_box = BoxLayout(orientation="horizontal", size_hint=(None, 1), width=dp(140), padding=(dp(6), 0))
        self.battery_label = Label(text="100%", size_hint=(None, 1), width=dp(50), color=(1, 1, 1, 1), font_size=dp(12))
        self.clock_label = Label(text="00:00\n01/01", size_hint=(None, 1), width=dp(90), color=(1, 1, 1, 1), font_size=dp(12), halign="center")
        self.clock_label.bind(size=self.clock_label.setter("text_size"))
        right_box.add_widget(self.battery_label)
        right_box.add_widget(self.clock_label)
        self.add_widget(right_box)

        # Har sekundda soatni, har 60 sekundda batareyani yangilaymiz
        Clock.schedule_interval(self._update_clock, 1)
        Clock.schedule_interval(self._update_battery, 60)
        self._update_clock(0)
        self._update_battery(0)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _update_clock(self, dt):
        now = datetime.datetime.now()
        self.clock_label.text = now.strftime("%H:%M\n%d/%m/%Y")

    def _update_battery(self, dt):
        try:
            if HAS_BATTERY_API:
                status = battery.status
                level = status.get("percentage")
                if level is not None:
                    self.battery_label.text = f"{int(level)}%"
                    return
            self.battery_label.text = "N/A"
        except Exception as exc:
            logger.warning("Batareya holatini olishda xatolik: %s", exc)
            self.battery_label.text = "N/A"

    # ------------------------------------------------------------------
    # Ochiq ilovalar ro'yxatini boshqarish
    # ------------------------------------------------------------------
    def add_running_app(self, app_id, title):
        if app_id in self._running_buttons:
            return
        btn = Button(
            text=title,
            size_hint=(None, 1),
            width=dp(110),
            background_normal="",
            background_color=(0.25, 0.35, 0.55, 1),
            color=(1, 1, 1, 1),
            font_size=dp(12),
        )
        btn.bind(on_release=lambda *_: self._on_app_icon_pressed(app_id))
        self.apps_box.add_widget(btn)
        self._running_buttons[app_id] = btn

    def remove_running_app(self, app_id):
        btn = self._running_buttons.pop(app_id, None)
        if btn:
            self.apps_box.remove_widget(btn)

    def set_app_active_style(self, app_id, active: bool):
        btn = self._running_buttons.get(app_id)
        if btn:
            btn.background_color = (0.35, 0.55, 0.85, 1) if active else (0.25, 0.35, 0.55, 1)
