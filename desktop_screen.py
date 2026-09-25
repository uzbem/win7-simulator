"""
desktop_screen.py
------------------
Butun "Windows 7" tajribasining bosh ekrani.

Bu klass quyidagilarni birlashtiradi:
 - Klassik Windows 7 ko'k fon (gradient taqlidi)
 - Ish stoli ikonkalari (DesktopIcon)
 - Taskbar (pastki panel)
 - Start Menyu (talab bo'yicha ochiladi)
 - Oynalar qatlami (AppWindow obyektlari shu yerda "suzadi")

Ekran o'lchami o'zgarganda (portrait/landscape) barcha elementlar
avtomatik moslashadi, chunki ular size_hint va nisbiy pozitsiyalar
asosida qurilgan.
"""

import logging
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.app import App

from core.taskbar import Taskbar, TASKBAR_HEIGHT
from core.start_menu import StartMenu
from core.window_manager import AppWindow
from core.desktop_icon import DesktopIcon

from apps.notepad_app import build_notepad_content
from apps.calculator_app import build_calculator_content
from apps.file_manager_app import build_file_manager_content
from apps.media_player_app import build_media_player_content
from apps.cmd_app import build_cmd_content

logger = logging.getLogger("Win7Sim.Desktop")


# Har bir app_id uchun: (sarlavha, content_builder_funksiyasi, boshlang'ich o'lcham)
APP_REGISTRY = {
    "notepad": ("Bloknot - Notepad", build_notepad_content, (dp(320), dp(400))),
    "calculator": ("Kalkulyator", build_calculator_content, (dp(260), dp(380))),
    "file_manager": ("Fayl Menejeri", build_file_manager_content, (dp(340), dp(440))),
    "media_player": ("Windows Media Player", build_media_player_content, (dp(320), dp(400))),
    "cmd": ("Buyruqlar satri", build_cmd_content, (dp(340), dp(360))),
}


class DesktopScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint=(1, 1), **kwargs)

        # --- Windows 7 klassik ko'k fon (gradient taqlidi bir nechta qatlam bilan) ---
        with self.canvas.before:
            Color(0.10, 0.32, 0.62, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # --- Oynalar suzadigan qatlam (taskbardan yuqorida) ---
        self.windows_layer = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.windows_layer)

        # --- Ish stoli ikonkalari ---
        self._create_desktop_icons()

        # --- Taskbar (pastda, doim tepada ko'rinadi) ---
        self.taskbar = Taskbar(
            on_start_pressed=self._toggle_start_menu,
            on_app_icon_pressed=self._on_taskbar_app_pressed,
            pos=(0, 0),
        )
        self.add_widget(self.taskbar)

        self.start_menu = None
        self._open_windows = {}  # app_id -> AppWindow

        Window.bind(size=self._on_window_resize)

    # ------------------------------------------------------------------
    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self.taskbar.pos = (0, 0)
        self.taskbar.size = (self.width, TASKBAR_HEIGHT)

    def _on_window_resize(self, *args):
        """Portrait/Landscape almashganda taskbar va oynalar chegaralarini moslashtirish."""
        self.taskbar.width = self.width
        for win in list(self._open_windows.values()):
            # Ekrandan tashqariga chiqib qolgan oynalarni ichkariga qaytaramiz
            new_x = min(win.x, max(0, Window.width - win.width))
            new_y = min(win.y, max(TASKBAR_HEIGHT, Window.height - win.height))
            win.pos = (max(0, new_x), max(TASKBAR_HEIGHT, new_y))

    # ------------------------------------------------------------------
    # Ish stoli ikonkalari
    # ------------------------------------------------------------------
    def _create_desktop_icons(self):
        icons = [
            ("file_manager", "Ushbu Kompyuter", "🖥", (dp(20), dp(500))),
            ("file_manager", "Savat", "🗑", (dp(20), dp(400))),
            ("file_manager", "Hujjatlar", "📁", (dp(20), dp(300))),
            ("settings", "Sozlamalar", "⚙", (dp(20), dp(200))),
        ]
        for app_id, title, glyph, pos in icons:
            icon = DesktopIcon(app_id=app_id, label_text=title, glyph=glyph,
                                on_open=self._open_app, pos=pos)
            self.add_widget(icon)

    # ------------------------------------------------------------------
    # Start menyu
    # ------------------------------------------------------------------
    def _toggle_start_menu(self):
        if self.start_menu and self.start_menu.is_open:
            self.start_menu.close()
            self.start_menu = None
            return
        self.start_menu = StartMenu(
            on_app_selected=self._open_app,
            on_shutdown=self._handle_shutdown,
            on_quick_link=self._handle_quick_link,
        )
        self.add_widget(self.start_menu)
        self.start_menu.open_at(dp(4), TASKBAR_HEIGHT)

    def _handle_quick_link(self, link_name):
        logger.info("Tezkor havola bosildi: %s", link_name)
        if link_name in ("Mening hujjatlarim", "Rasmlar", "Xotira"):
            self._open_app("file_manager")
        elif link_name == "Sozlamalar":
            self._open_app("settings")

    def _handle_shutdown(self):
        logger.info("Tizimdan chiqish so'raldi -> ilova yopilmoqda")
        App.get_running_app().stop()

    # ------------------------------------------------------------------
    # Dastur (App) ochish / boshqarish
    # ------------------------------------------------------------------
    def _open_app(self, app_id):
        if app_id == "settings":
            self._show_settings_placeholder()
            return

        if app_id not in APP_REGISTRY:
            logger.warning("Noma'lum ilova: %s", app_id)
            return

        # Agar allaqachon ochiq bo'lsa - shunchaki tiklaymiz/fokusga olamiz
        if app_id in self._open_windows:
            self._open_windows[app_id].restore()
            return

        title, builder, size = APP_REGISTRY[app_id]
        try:
            content = builder()
        except Exception as exc:
            logger.error("'%s' ilovasi yaratilishida xatolik: %s", app_id, exc)
            content = Label(text=f"Xatolik: {exc}")

        win = AppWindow(
            title=title,
            content=content,
            desktop_layer=self.windows_layer,
            app_id=app_id,
            on_close=self._on_window_closed,
            on_state_change=self._on_window_state_change,
            win_pos=(dp(30) + dp(15) * len(self._open_windows), TASKBAR_HEIGHT + dp(40)),
            win_size=size,
        )
        self.windows_layer.add_widget(win)
        self._open_windows[app_id] = win
        self.taskbar.add_running_app(app_id, title.split(" - ")[0][:14])
        self.taskbar.set_app_active_style(app_id, True)

    def _show_settings_placeholder(self):
        from kivy.uix.label import Label as _Label
        if "settings" in self._open_windows:
            self._open_windows["settings"].restore()
            return
        content = _Label(text="Sozlamalar bo'limi\n(demo)", halign="center")
        win = AppWindow(
            title="Sozlamalar",
            content=content,
            desktop_layer=self.windows_layer,
            app_id="settings",
            on_close=self._on_window_closed,
            on_state_change=self._on_window_state_change,
            win_pos=(dp(50), TASKBAR_HEIGHT + dp(60)),
            win_size=(dp(280), dp(220)),
        )
        self.windows_layer.add_widget(win)
        self._open_windows["settings"] = win
        self.taskbar.add_running_app("settings", "Sozlamalar")

    def _on_window_closed(self, app_id):
        self._open_windows.pop(app_id, None)
        self.taskbar.remove_running_app(app_id)

    def _on_window_state_change(self, app_id, state):
        self.taskbar.set_app_active_style(app_id, state == "restored")

    def _on_taskbar_app_pressed(self, app_id):
        win = self._open_windows.get(app_id)
        if not win:
            return
        if win.opacity == 0:
            win.restore()
        else:
            win.bring_to_front()
