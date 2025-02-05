# screens/welcome_screen.py

from kivy.uix.screenmanager import Screen
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.core.window import Window

from arcade_wizard.constants import GREEN, YELLOW, RED, BLUE
from arcade_wizard.utils import log
from arcade_wizard.screen_manager import BaseScreen

class WelcomeScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super(WelcomeScreen, self).__init__(app, name="welcome", **kwargs)
        # Define the "continue" button rectangle.
        bx = app.bubble_rect[0] + (app.bubble_rect[2] // 2) - 220
        by = app.bubble_rect[1] + 150
        self.next_button_rect = [bx, by, 441, 107]
        self.next_button_selected = False
        self.next_button_hovered = False

        self.load_buttons()
        self.load_sounds()
        self.placeholder_images = self.define_placeholder_images()
        Window.bind(on_touch_down=self.on_touch_down)

    def load_buttons(self):
        try:
            n_path = self.app.get_path("images", "continue_normal_lg.png")
            h_path = self.app.get_path("images", "continue_hover_lg.png")
            p_path = self.app.get_path("images", "continue_pressed_lg.png")
            self.next_normal = CoreImage(n_path).texture
            self.next_hover = CoreImage(h_path).texture
            self.next_pressed = CoreImage(p_path).texture
        except Exception as e:
            log(f"Failed to load WelcomeScreen buttons: {e}")
            self.next_normal = self.next_hover = self.next_pressed = None

    def load_sounds(self):
        try:
            click_path = self.app.get_path("sounds", "select.ogg")
            hover_path = self.app.get_path("sounds", "hover.ogg")
            from kivy.core.audio import SoundLoader
            self.button_click_sound = SoundLoader.load(click_path)
            if self.button_click_sound:
                self.button_click_sound.volume = 0.5
            self.button_hover_sound = SoundLoader.load(hover_path)
            if self.button_hover_sound:
                self.button_hover_sound.volume = 0.1
        except Exception as e:
            log(f"Failed to load WelcomeScreen sounds: {e}")
            self.button_click_sound = self.button_hover_sound = None

    def define_placeholder_images(self):
        configs = [
            {
                "path": "welcome_arcade.png",
                "size": (1058, 324),
                "pos": (self.app.bubble_rect[0] + 1419 // 2 - 529,
                        self.app.bubble_rect[1] + 100),
            },
            {
                "path": "get_started.png",
                "size": (324, 18),
                "pos": (self.app.bubble_rect[0] + 1419 // 2 - 162,
                        self.app.bubble_rect[1] + 500),
            },
            {
                "path": "navigation_legend.png",
                "size": (896, 56),
                "pos": (self.app.bubble_rect[0] + 1419 // 2 - 448,
                        self.app.bubble_rect[1] + 740),
            },
            {
                "path": "page_indicator_1.png",
                "size": (212, 18),
                "pos": (self.app.bubble_rect[0] + 1419 // 2 - 106,
                        self.app.bubble_rect[1] + 880),
            }
        ]
        result = []
        for cfg in configs:
            try:
                img_path = self.app.get_path("images", cfg["path"])
                texture = CoreImage(img_path).texture
            except Exception as e:
                log(f"Failed to load image {cfg['path']}: {e}")
                texture = None
            result.append({"texture": texture, "pos": cfg["pos"], "size": cfg["size"]})
        return result

    def on_touch_down(self, touch):
        x, y = touch.pos
        bx, by, bw, bh = self.next_button_rect
        if bx <= x <= bx + bw and by <= y <= by + bh:
            if self.button_click_sound:
                self.button_click_sound.play()
            self.app.screen_manager.current = 'timezone'
            return True
        return super(WelcomeScreen, self).on_touch_down(touch)

    def on_enter(self):
        self.canvas.clear()
        with self.canvas:
            self.render_background_and_bubble(self.canvas)
            bx, by, bw, bh = self.next_button_rect
            if self.next_normal:
                Rectangle(texture=self.next_normal, pos=(bx, by), size=(bw, bh))
            for ph in self.placeholder_images:
                if ph["texture"]:
                    Rectangle(texture=ph["texture"], pos=ph["pos"], size=ph["size"])
        super(WelcomeScreen, self).on_enter()
