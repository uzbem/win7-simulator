"""
calculator_app.py
------------------
Sensorli tugmalarga ega ishchi matematik kalkulyator.

Xavfsizlik: foydalanuvchi kiritgan ifoda `eval()` orqali emas, balki
faqat ruxsat etilgan belgilar (raqamlar, + - * / . () %) tekshirilgach
hisoblanadi - bu ixtiyoriy kodni bajarishning oldini oladi.
"""

import logging
import re
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

logger = logging.getLogger("Win7Sim.Calculator")

# Faqat shu belgilarga ruxsat beramiz (xavfsiz eval uchun)
ALLOWED_CHARS = re.compile(r"^[0-9\.\+\-\*\/\(\)\%\s]*$")

BUTTONS = [
    "C", "(", ")", "/",
    "7", "8", "9", "*",
    "4", "5", "6", "-",
    "1", "2", "3", "+",
    "0", ".", "⌫", "=",
]


class CalculatorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)

        self.display = TextInput(
            text="",
            font_size=dp(24),
            size_hint=(1, None),
            height=dp(60),
            readonly=True,
            multiline=False,
            halign="right",
        )
        self.add_widget(self.display)

        grid = GridLayout(cols=4, spacing=dp(4), size_hint=(1, 1))
        for label in BUTTONS:
            btn = Button(text=label, font_size=dp(18))
            btn.bind(on_release=self._on_button_press)
            grid.add_widget(btn)
        self.add_widget(grid)

    def _on_button_press(self, instance):
        label = instance.text
        current = self.display.text

        if label == "C":
            self.display.text = ""
        elif label == "⌫":
            self.display.text = current[:-1]
        elif label == "=":
            self._calculate()
        else:
            self.display.text = current + label

    def _calculate(self):
        expr = self.display.text.strip()
        if not expr:
            return
        if not ALLOWED_CHARS.match(expr):
            self.display.text = "Xato"
            logger.warning("Ruxsat etilmagan belgi kiritildi: %s", expr)
            return
        try:
            # % ni Python foizga emas, oddiy "/100" ma'nosida ham ishlatish mumkin,
            # lekin standart Python semantikasi (qoldiq) bilan qoldiramiz.
            result = eval(expr, {"__builtins__": {}}, {})
            self.display.text = str(result)
        except ZeroDivisionError:
            self.display.text = "Nolga bo'lib bo'lmaydi"
        except Exception as exc:
            logger.error("Hisoblashda xatolik: %s", exc)
            self.display.text = "Xato"


def build_calculator_content():
    return CalculatorWidget()
