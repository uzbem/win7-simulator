"""
media_player_app.py
--------------------
Windows Media Player uslubidagi sodda audio pleyer simulyatsiyasi.

Kivy'ning o'rnatilgan `SoundLoader` klassi yordamida qurilmadagi
(ilova papkasi va umumiy Music papkasi) audio fayllarni ro'yxatlaydi
va Play/Pause/Stop tugmalari bilan boshqarishga imkon beradi.
"""

import os
import glob
import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App

logger = logging.getLogger("Win7Sim.MediaPlayer")

AUDIO_EXTENSIONS = ("*.mp3", "*.wav", "*.ogg")


def _search_dirs():
    dirs = []
    try:
        dirs.append(App.get_running_app().user_data_dir)
    except Exception:
        pass
    # Android'dagi umumiy Music papkasi (agar mavjud va ruxsat berilgan bo'lsa)
    for common in ("/sdcard/Music", "/storage/emulated/0/Music"):
        if os.path.isdir(common):
            dirs.append(common)
    return dirs


def _find_audio_files():
    files = []
    for d in _search_dirs():
        for ext in AUDIO_EXTENSIONS:
            files.extend(glob.glob(os.path.join(d, ext)))
    return sorted(set(files))


class MediaPlayerWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)

        self.current_sound = None
        self.current_path = None

        self.now_playing_label = Label(text="Hech narsa tanlanmagan", size_hint=(1, None),
                                        height=dp(28), font_size=dp(12))
        self.add_widget(self.now_playing_label)

        # --- Audio fayllar ro'yxati ---
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        self.add_widget(scroll)

        self.progress_slider = Slider(min=0, max=1, value=0, size_hint=(1, None), height=dp(28))
        self.progress_slider.disabled = True
        self.add_widget(self.progress_slider)

        controls = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(48), spacing=dp(6))
        self.play_btn = Button(text="▶ Play")
        self.play_btn.bind(on_release=self._toggle_play)
        stop_btn = Button(text="⏹ Stop")
        stop_btn.bind(on_release=self._stop)
        refresh_btn = Button(text="⟳")
        refresh_btn.bind(on_release=lambda *_: self._refresh_list())
        controls.add_widget(self.play_btn)
        controls.add_widget(stop_btn)
        controls.add_widget(refresh_btn)
        self.add_widget(controls)

        Clock.schedule_interval(self._update_progress, 0.5)
        self._refresh_list()

    def _refresh_list(self):
        self.grid.clear_widgets()
        files = _find_audio_files()
        if not files:
            self.grid.add_widget(Label(text="Audio fayllar topilmadi", size_hint_y=None, height=dp(30)))
            return
        for path in files:
            btn = Button(text=os.path.basename(path), size_hint_y=None, height=dp(38),
                         background_normal="", background_color=(0.93, 0.93, 0.96, 1),
                         color=(0.1, 0.1, 0.1, 1))
            btn.bind(on_release=lambda inst, p=path: self._load_and_play(p))
            self.grid.add_widget(btn)

    def _load_and_play(self, path):
        self._stop()
        try:
            self.current_sound = SoundLoader.load(path)
            if self.current_sound:
                self.current_path = path
                self.current_sound.play()
                self.now_playing_label.text = f"Ijro etilmoqda: {os.path.basename(path)}"
                self.play_btn.text = "⏸ Pause"
                self.progress_slider.disabled = False
                logger.info("Audio ijro etilmoqda: %s", path)
            else:
                self.now_playing_label.text = "Faylni yuklab bo'lmadi"
        except Exception as exc:
            logger.error("Audio yuklashda xatolik: %s", exc)
            self.now_playing_label.text = f"Xatolik: {exc}"

    def _toggle_play(self, *args):
        if not self.current_sound:
            return
        if self.current_sound.state == "play":
            self.current_sound.stop()
            self.play_btn.text = "▶ Play"
        else:
            self.current_sound.play()
            self.play_btn.text = "⏸ Pause"

    def _stop(self, *args):
        if self.current_sound:
            try:
                self.current_sound.stop()
                self.current_sound.unload()
            except Exception as exc:
                logger.warning("To'xtatishda xatolik: %s", exc)
        self.current_sound = None
        self.play_btn.text = "▶ Play"
        self.progress_slider.value = 0
        self.progress_slider.disabled = True

    def _update_progress(self, dt):
        if self.current_sound and self.current_sound.length:
            self.progress_slider.max = self.current_sound.length
            self.progress_slider.value = self.current_sound.get_pos()


def build_media_player_content():
    return MediaPlayerWidget()
