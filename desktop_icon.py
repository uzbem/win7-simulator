"""
desktop_icon.py
----------------
Ish stolidagi (Desktop) sensorli ikonkalar: "Ushbu Kompyuter", "Savat",
"Hujjatlar", "Sozlamalar" va h.k.

Ikkita sensor ishorasini qo'llab-quvvatlaydi:
 1) Drag - barmoq bilan ushlab, ikonkani ish stoli bo'ylab erkin ko'chirish.
 2) Double Tap - Kivy'ning o'rnatilgan `touch.is_double_tap` xususiyati
    yordamida ikki marta bosishni aniqlab, dasturni ochish.
"""

import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp

logger = logging.getLogger("Win7Sim.DesktopIcon")

ICON_SIZE = dp(72)


class DesktopIcon(BoxLayout):
    """
    app_id: ikonka bosilganda ochiladigan dastur identifikatori
    label_text: ikonka ostidagi matn
    glyph: ikonka ichida ko'rsatiladigan belgi/harf (rasm o'rniga soddalashtirilgan)
    on_open(app_id): ikki marta bosilganda chaqiriladigan callback
    """

    def __init__(self, app_id, label_text, glyph, on_open, pos=(dp(20), dp(400)), **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            size=(ICON_SIZE, ICON_SIZE + dp(28)),
            pos=pos,
            **kwargs,
        )
        self.app_id = app_id
        self._on_open = on_open
        self._dragging = False
        self._drag_offset = (0, 0)
        self._touch_start_pos = None

        icon_box = BoxLayout(size_hint=(1, None), height=ICON_SIZE)
        with icon_box.canvas.before:
            Color(0.9, 0.9, 0.95, 0.85)
            self._circle = Ellipse(pos=icon_box.pos, size=icon_box.size)
        icon_box.bind(pos=self._update_circle, size=self._update_circle)

        glyph_label = Label(text=glyph, font_size=dp(28), color=(0.1, 0.1, 0.3, 1))
        icon_box.add_widget(glyph_label)
        self.add_widget(icon_box)

        text_label = Label(text=label_text, font_size=dp(11), color=(1, 1, 1, 1),
                            size_hint=(1, None), height=dp(24))
        self.add_widget(text_label)

    def _update_circle(self, instance, *args):
        self._circle.pos = instance.pos
        self._circle.size = instance.size

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        # Ikki marta bosishni Kivy o'zi aniqlaydi (is_double_tap)
        if touch.is_double_tap:
            logger.info("Ikonka ikki marta bosildi: %s", self.app_id)
            self._on_open(self.app_id)
            return True

        self._dragging = True
        self._drag_offset = (touch.x - self.x, touch.y - self.y)
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._dragging:
            new_x = touch.x - self._drag_offset[0]
            new_y = touch.y - self._drag_offset[1]
            if self.parent:
                new_x = max(0, min(new_x, self.parent.width - self.width))
                new_y = max(0, min(new_y, self.parent.height - self.height))
            self.pos = (new_x, new_y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._dragging = False
            return True
        return super().on_touch_up(touch)
