"""
cmd_app.py
----------
Windows Buyruqlar satri (Command Prompt) ning Android muhitiga
moslashtirilgan matnli konsol simulyatori.

Qo'llab-quvvatlanadigan buyruqlar:
    dir     - joriy (ilova) papkadagi fayl/papkalarni ro'yxatlaydi
    echo    - matnni ekranga chiqaradi
    clear   - konsol ekranini tozalaydi
    ver     - simulyator versiyasini ko'rsatadi
    help    - mavjud buyruqlar ro'yxatini ko'rsatadi
"""

import os
import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App

logger = logging.getLogger("Win7Sim.CMD")

VERSION_TEXT = "Windows7-Simulator [Version 1.0.0] - Kivy asosida (Python)"


class CmdWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)

        self.output_scroll = ScrollView(size_hint=(1, 1))
        self.output_label = Label(
            text="Microsoft(R) Windows 7 [Simulyator]\nYordam uchun 'help' yozing.\n\n",
            size_hint_y=None,
            font_size=dp(12),
            font_name="RobotoMono-Regular" if self._mono_available() else None,
            color=(0.1, 1, 0.1, 1),
            halign="left",
            valign="top",
        )
        self.output_label.bind(texture_size=self._update_label_height)
        self.output_scroll.add_widget(self.output_label)
        self.add_widget(self.output_scroll)

        input_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(40))
        self.prompt_label = Label(text=">", size_hint=(None, 1), width=dp(18), color=(0.1, 1, 0.1, 1))
        self.cmd_input = TextInput(
            multiline=False,
            size_hint=(1, 1),
            background_color=(0, 0, 0, 1),
            foreground_color=(0.1, 1, 0.1, 1),
            cursor_color=(0.1, 1, 0.1, 1),
        )
        self.cmd_input.bind(on_text_validate=self._on_enter)
        input_row.add_widget(self.prompt_label)
        input_row.add_widget(self.cmd_input)
        self.add_widget(input_row)

        with self.canvas.before:
            pass  # fon rangini oddiy Label orqali qora qilib beryapmiz (pastda canvas orqali)

    def _mono_available(self):
        return False  # standart shrift bilan cheklanamiz, ixtiyoriy monospace kiritilishi mumkin

    def _update_label_height(self, instance, size):
        self.output_label.height = size[1]
        self.output_label.text_size = (self.output_label.width, None)
        self.output_scroll.scroll_y = 0

    def _print(self, text):
        self.output_label.text += text + "\n"

    def _on_enter(self, instance):
        command_line = instance.text.strip()
        instance.text = ""
        if not command_line:
            return
        self._print(f"> {command_line}")
        self._execute(command_line)

    def _execute(self, command_line):
        try:
            parts = command_line.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "help":
                self._print(
                    "Mavjud buyruqlar:\n"
                    "  dir    - fayllarni ro'yxatlash\n"
                    "  echo   - matn chiqarish (masalan: echo Salom)\n"
                    "  clear  - ekranni tozalash\n"
                    "  ver    - versiya haqida ma'lumot\n"
                    "  help   - shu ro'yxat"
                )
            elif cmd == "dir":
                self._cmd_dir()
            elif cmd == "echo":
                self._print(arg)
            elif cmd == "clear" or cmd == "cls":
                self.output_label.text = ""
            elif cmd == "ver":
                self._print(VERSION_TEXT)
            else:
                self._print(f"'{cmd}' buyrug'i tanilmadi. Yordam uchun 'help' yozing.")
        except Exception as exc:
            logger.error("Buyruqni bajarishda xatolik: %s", exc)
            self._print(f"Xatolik: {exc}")

    def _cmd_dir(self):
        try:
            base = App.get_running_app().user_data_dir
        except Exception:
            base = "."
        try:
            entries = os.listdir(base)
            self._print(f" {base} papkasi mundarijasi:\n")
            if not entries:
                self._print(" (bo'sh)")
            else:
                for e in entries:
                    full = os.path.join(base, e)
                    tag = "<DIR>" if os.path.isdir(full) else "     "
                    self._print(f" {tag}  {e}")
        except Exception as exc:
            self._print(f"Xatolik: {exc}")


def build_cmd_content():
    return CmdWidget()
