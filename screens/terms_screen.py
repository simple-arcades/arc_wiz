# screens/terms_screen.py

import os
import datetime
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from arcade_wizard.constants import BLACK, BLUE, GRAY, RED, GREEN, YELLOW, TERMS_LOG_FILE
from arcade_wizard.utils import log, show_message
from arcade_wizard.screen_manager import BaseScreen

class TermsScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super(TermsScreen, self).__init__(app, name="terms", **kwargs)
        # Load terms text from file.
        self.terms_text = self.load_terms()
        self.agree_enabled = False

        # Define positions based on bubble.
        bx, by, bw, bh = self.app.bubble_rect
        self.text_box_rect = [bx + 40, by + 350, bw - 80, bh - 535]
        self.agree_button_rect = [self.text_box_rect[0] + (self.text_box_rect[2]//2) - 111,
                                  self.text_box_rect[1] - 20, 222, 55]

        # Load placeholder images and agree button images.
        self.placeholder_images = self.load_placeholders()
        self.agree_normal, self.agree_hover, self.agree_pressed = self.load_agree_images()

        # Build UI using a FloatLayout.
        from kivy.core.window import Window
        self.layout = FloatLayout(size=Window.size)

        self.add_widget(self.layout)

        # Create a ScrollView for the terms text.
        self.scroll_view = ScrollView(size_hint=(None, None),
                                      size=(self.text_box_rect[2], self.text_box_rect[3]),
                                      pos=(self.text_box_rect[0], self.text_box_rect[1]))
        self.terms_label = Label(text=self.terms_text, markup=True, size_hint=(None, None),
                                 halign='left', valign='top', font_size='20sp', color=BLACK)
        self.terms_label.bind(texture_size=self.terms_label.setter('size'))
        self.scroll_view.add_widget(self.terms_label)
        self.layout.add_widget(self.scroll_view)

        # Create an Image widget for the agree button.
        self.agree_button = Image(source=self.app.get_path("images", "agree_normal_lg.png"),
                                  size_hint=(None, None), size=(222, 55),
                                  pos=(self.agree_button_rect[0], self.agree_button_rect[1]))
        self.layout.add_widget(self.agree_button)

        # Check scroll position periodically to enable the agree button.
        Clock.schedule_interval(self.update, 1/30.)

    def load_terms(self):
        try:
            path = self.app.get_path("terms_and_conditions.txt")
            with open(path, "r") as f:
                lines = f.readlines()
            return "\n".join(line.rstrip("\n") for line in lines)
        except Exception as e:
            log("Error: terms_and_conditions.txt not found.")
            return "**Error: Terms and Conditions file not found.**"

    def load_placeholders(self):
        configs = [
            {
                "path": "user_agreement.png",
                "size": (803,205),
                "pos": (self.app.bubble_rect[0] + 1419//2 - 401,
                        self.app.bubble_rect[1] + 80),
            },
            {
                "path": "navigation_legend.png",
                "size": (896,56),
                "pos": (self.app.bubble_rect[0] + 1419//2 - 448,
                        self.app.bubble_rect[1] + 740),
            },
            {
                "path": "page_indicator_3.png",
                "size": (212,18),
                "pos": (self.app.bubble_rect[0] + 1419//2 - 106,
                        self.app.bubble_rect[1] + 880),
            },
        ]
        result = []
        from kivy.core.image import Image as CoreImage
        for cfg in configs:
            try:
                texture = CoreImage(self.app.get_path("images", cfg["path"])).texture
            except Exception as e:
                log(f"Failed to load image {cfg['path']}: {e}")
                texture = None
            result.append({"texture": texture, "pos": cfg["pos"], "size": cfg["size"]})
        return result

    def load_agree_images(self):
        from kivy.core.image import Image as CoreImage
        try:
            n = CoreImage(self.app.get_path("images", "agree_normal_lg.png")).texture
            h = CoreImage(self.app.get_path("images", "agree_hover_lg.png")).texture
            p = CoreImage(self.app.get_path("images", "agree_pressed_lg.png")).texture
            return n, h, p
        except Exception as e:
            log(f"Failed to load agree button images: {e}")
            return None, None, None

    def update(self, dt):
        # Enable agree button if the user has scrolled to the bottom.
        if self.scroll_view.scroll_y <= 0.05:
            self.agree_enabled = True
        else:
            self.agree_enabled = False

    def on_touch_down(self, touch):
        # If touch is on the agree button and it’s enabled, process agreement.
        if self.agree_enabled:
            x, y = touch.pos
            ax, ay, aw, ah = self.agree_button_rect
            if ax <= x <= ax+aw and ay <= y <= ay+ah:
                if self.agree_normal:
                    self.agree_button.texture = self.agree_pressed
                self.log_user_agreement()
                self.app.screen_manager.current = 'wifi'
                return True
        return super(TermsScreen, self).on_touch_down(touch)

    def log_user_agreement(self):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"User agreed on {t}\n"
        try:
            with open(TERMS_LOG_FILE, "a") as lf:
                lf.write(msg)
        except Exception as e:
            log(f"Failed to write to terms log: {e}")
