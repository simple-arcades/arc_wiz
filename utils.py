# utils.py
import os
import sys
import datetime
from arcade_wizard.constants import APP_LOG_FILE, PHYSICAL_WIDTH, PHYSICAL_HEIGHT, WHITE
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window

def log(message: str):
    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(APP_LOG_FILE, "a") as f:
            f.write(f"[{t}] {message}\n")
    except Exception as e:
        print(f"Logging failed: {e}")

def show_message(message: str, color=WHITE, timeout=2):
    """
    Displays an overlay message by adding a Label to the Window, then removing it after a timeout.
    """
    msg_label = Label(text=message, font_size='56sp', color=color,
                      size_hint=(None, None),
                      size=(PHYSICAL_WIDTH, PHYSICAL_HEIGHT),
                      pos=(0, 0))
    # Add a semi-transparent dark background behind the text.
    msg_label.canvas.before.clear()
    with msg_label.canvas.before:
        from kivy.graphics import Color, Rectangle
        Color(0, 0, 0, 0.7)
        Rectangle(pos=(0, 0), size=(PHYSICAL_WIDTH, PHYSICAL_HEIGHT))
    Window.add_widget(msg_label)
    Clock.schedule_once(lambda dt: Window.remove_widget(msg_label), timeout)
