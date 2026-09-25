"""
window_manager.py
------------------
Windows 7 uslubidagi "Aero Glass" oynasini simulyatsiya qiluvchi modul.

Bu modul har bir ochilgan dastur (Notepad, Calculator va h.k.) uchun
mustaqil, sudrab ko'chiriladigan (draggable), burchagidan ushlab
o'lchami o'zgartiriladigan (resizable), kichiklashtiriladigan
(minimize), to'liq ekranga yoyiladigan (maximize) va yopiladigan
(close) oyna obyektini yaratadi.

Arxitektura tamoyili: har bir AppWindow o'zining holatini (pos, size,
is_maximized) o'zi boshqaradi va tashqi WindowManager (Desktop) bilan
faqat callback orqali (on_close, on_minimize) aloqa qiladi -> bu
"loose coupling" (Clean Architecture) tamoyiliga mos keladi.
"""

import logging
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import StringProperty, BooleanProperty

logger = logging.getLogger("Win7Sim.WindowManager")

# Minimal oyna o'lchamlari - juda kichik qilib "buzib" qo'yishning oldini olish
MIN_WIN_WIDTH = dp(220)
MIN_WIN_HEIGHT = dp(180)

# Burchakdagi "resize" ushlagichining teginish radiusi (barmoq uchun)
RESIZE_HANDLE_SIZE = dp(36)


class TitleBar(BoxLayout):
    """
    Oynaning tepasidagi shaffof Aero-uslubidagi sarlavha paneli.
    Sudrash faqat shu panel ustida boshlanadi (butun oyna emas),
    bu esa ichidagi kontent (masalan TextInput) bilan to'qnashuvni oldini oladi.
    """

    def __init__(self, title_text, on_close, on_minimize, on_maximize, **kwargs):
        super().__init__(orientation="horizontal", size_hint=(1, None), height=dp(40), **kwargs)
        self._on_close = on_close
        self._on_minimize = on_minimize
        self._on_maximize = on_maximize

        with self.canvas.before:
            # Aero Glass effektini taqlid qiluvchi yarim shaffof gradient-simon fon
            Color(0.55, 0.75, 0.95, 0.55)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.title_label = Label(
            text=title_text,
            color=(0.05, 0.05, 0.05, 1),
            bold=True,
            halign="left",
            valign="middle",
            size_hint=(1, 1),
            padding=(dp(10), 0),
        )
        self.title_label.bind(size=self.title_label.setter("text_size"))
        self.add_widget(self.title_label)

        # Minimize, Maximize, Close tugmalari - Windows 7 tartibida
        self.add_widget(self._make_btn("—", self._minimize_pressed, (0.85, 0.85, 0.9, 1)))
        self.add_widget(self._make_btn("□", self._maximize_pressed, (0.85, 0.85, 0.9, 1)))
        self.add_widget(self._make_btn("X", self._close_pressed, (0.85, 0.25, 0.25, 1)))

    def _make_btn(self, text, callback, color):
        btn = Button(
            text=text,
            size_hint=(None, 1),
            width=dp(40),
            background_normal="",
            background_color=color,
            color=(0, 0, 0, 1),
            bold=True,
        )
        btn.bind(on_release=callback)
        return btn

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _close_pressed(self, *args):
        self._on_close()

    def _minimize_pressed(self, *args):
        self._on_minimize()

    def _maximize_pressed(self, *args):
        self._on_maximize()


class AppWindow(FloatLayout):
    """
    Har bir dastur uchun mustaqil, sudrab ko'chiriladigan oyna.

    Parametrlar:
        title (str): oyna sarlavhasi
        content (Widget): oyna ichida ko'rsatiladigan dastur interfeysi
        desktop_layer (Widget): oynalar joylashadigan asosiy FloatLayout (z-order uchun)
        on_close (callable): oyna yopilganda chaqiriladigan funksiya
        on_state_change (callable): oyna minimize/restore bo'lganda taskbar'ni yangilash uchun
    """

    is_maximized = BooleanProperty(False)
    app_id = StringProperty("")

    def __init__(self, title, content, desktop_layer, app_id="",
                 on_close=None, on_state_change=None,
                 win_pos=(dp(40), dp(120)), win_size=(dp(320), dp(420)), **kwargs):
        super().__init__(size_hint=(None, None), pos=win_pos, size=win_size, **kwargs)
        self.app_id = app_id
        self.desktop_layer = desktop_layer
        self._on_close_cb = on_close
        self._on_state_change_cb = on_state_change
        self._content_widget = content
        self._restore_pos = win_pos
        self._restore_size = win_size

        # --- Sudrash (drag) holati uchun o'zgaruvchilar ---
        self._dragging = False
        self._drag_offset = (0, 0)

        # --- Resize holati uchun o'zgaruvchilar ---
        self._resizing = False

        with self.canvas.before:
            Color(0.96, 0.96, 0.97, 0.97)
            self._body_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.2, 0.4, 0.7, 0.9)
            self._border_line = Line(rectangle=(*self.pos, *self.size), width=1.2)
        self.bind(pos=self._sync_graphics, size=self._sync_graphics)

        # --- Ichki joylashuv: TitleBar (yuqorida) + Content (pastda) ---
        self.title_bar = TitleBar(
            title_text=title,
            on_close=self._handle_close,
            on_minimize=self._handle_minimize,
            on_maximize=self._handle_maximize,
        )
        self.add_widget(self.title_bar)

        self._content_container = FloatLayout(size_hint=(1, 1))
        self._content_container.add_widget(content)
        self.add_widget(self._content_container)

        # Resize ushlagichi (o'ng-past burchak) - vizual belgi
        self.resize_handle = Label(
            text="◢",
            size_hint=(None, None),
            size=(RESIZE_HANDLE_SIZE, RESIZE_HANDLE_SIZE),
            color=(0.3, 0.3, 0.3, 0.8),
        )
        self.add_widget(self.resize_handle)

        self.bind(pos=self._layout_children, size=self._layout_children)
        self._layout_children()

    # ------------------------------------------------------------------
    # Grafikani va bolalar (children) joylashuvini pozitsiyaga moslash
    # ------------------------------------------------------------------
    def _sync_graphics(self, *args):
        self._body_rect.pos = self.pos
        self._body_rect.size = self.size
        self._border_line.rectangle = (*self.pos, *self.size)

    def _layout_children(self, *args):
        # TitleBar - oynaning eng yuqorisida, to'liq kenglikda
        self.title_bar.size = (self.width, dp(40))
        self.title_bar.pos = (self.x, self.top - dp(40))

        # Content - TitleBar ostidagi qolgan barcha maydon
        self._content_container.size = (self.width, self.height - dp(40))
        self._content_container.pos = (self.x, self.y)

        # Resize ushlagich - o'ng-past burchakda
        self.resize_handle.pos = (self.right - RESIZE_HANDLE_SIZE, self.y)

    # ------------------------------------------------------------------
    # Touch (sensorli) hodisalar: sudrash va o'lchamni o'zgartirish
    # ------------------------------------------------------------------
    def on_touch_down(self, touch):
        # Avval oynani "eng oldinga" chiqaramiz (fokus effekti)
        if self.collide_point(*touch.pos):
            self.bring_to_front()

        # Resize ushlagichi bosilganmi?
        if self.resize_handle.collide_point(*touch.pos) and not self.is_maximized:
            self._resizing = True
            touch.grab(self)
            return True

        # TitleBar bosilganmi (sudrash uchun)?
        if self.title_bar.collide_point(*touch.pos) and not self.is_maximized:
            # Tugmalar ustida bosilgan bo'lsa, sudrashni boshlamaymiz
            for child in self.title_bar.children:
                if isinstance(child, Button) and child.collide_point(*touch.pos):
                    return super().on_touch_down(touch)
            self._dragging = True
            self._drag_offset = (touch.x - self.x, touch.y - self.y)
            touch.grab(self)
            return True

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            if self._dragging:
                new_x = touch.x - self._drag_offset[0]
                new_y = touch.y - self._drag_offset[1]
                # Oynani ekran chegarasidan butunlay chiqib ketishini cheklaymiz
                if self.desktop_layer:
                    new_x = max(-self.width + dp(60), min(new_x, self.desktop_layer.width - dp(60)))
                    new_y = max(dp(0), min(new_y, self.desktop_layer.height - dp(40)))
                self.pos = (new_x, new_y)
                return True
            if self._resizing:
                new_w = max(MIN_WIN_WIDTH, touch.x - self.x)
                new_h = max(MIN_WIN_HEIGHT, self.top - touch.y)
                new_y = self.top - new_h
                self.size = (new_w, new_h)
                self.y = new_y
                return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._dragging = False
            self._resizing = False
            return True
        return super().on_touch_up(touch)

    # ------------------------------------------------------------------
    # Oyna holatini boshqarish: yopish / kichiklashtirish / yoyish
    # ------------------------------------------------------------------
    def bring_to_front(self):
        """Oynani z-order bo'yicha eng tepaga chiqaradi (bosilganda fokusga oladi)."""
        try:
            if self.parent:
                self.parent.remove_widget(self)
                self.parent.add_widget(self)
        except Exception as exc:
            logger.warning("bring_to_front xatosi: %s", exc)

    def _handle_close(self):
        try:
            if self.parent:
                self.parent.remove_widget(self)
            if self._on_close_cb:
                self._on_close_cb(self.app_id)
            logger.info("Oyna yopildi: %s", self.app_id)
        except Exception as exc:
            logger.error("Oynani yopishda xatolik: %s", exc)

    def _handle_minimize(self):
        try:
            self.opacity = 0
            self.disabled = True
            self.size_hint = self.size_hint  # o'zgarishsiz, faqat ko'rinmas qilinadi
            self.pos = (-dp(9999), -dp(9999))  # touch hodisalari tegmasligi uchun
            if self._on_state_change_cb:
                self._on_state_change_cb(self.app_id, "minimized")
        except Exception as exc:
            logger.error("Minimize xatosi: %s", exc)

    def restore(self):
        """Taskbar orqali minimallashtirilgan oynani qayta tiklash."""
        self.opacity = 1
        self.disabled = False
        self.pos = self._restore_pos
        self.bring_to_front()
        if self._on_state_change_cb:
            self._on_state_change_cb(self.app_id, "restored")

    def _handle_maximize(self):
        if not self.desktop_layer:
            return
        if not self.is_maximized:
            self._restore_pos = self.pos
            self._restore_size = self.size
            anim = Animation(
                pos=(0, dp(48)),
                size=(self.desktop_layer.width, self.desktop_layer.height - dp(48)),
                duration=0.18,
            )
            anim.start(self)
            self.is_maximized = True
        else:
            anim = Animation(pos=self._restore_pos, size=self._restore_size, duration=0.18)
            anim.start(self)
            self.is_maximized = False
