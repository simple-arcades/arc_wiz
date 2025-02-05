# screens/final_screen.py

import shutil
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock

from arcade_wizard.screen_manager import BaseScreen
from arcade_wizard.utils import log
from arcade_wizard.constants import PHYSICAL_WIDTH, PHYSICAL_HEIGHT

class FinalScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super(FinalScreen, self).__init__(app, name="final", **kwargs)
        self.font_size = '24sp'
        self.placeholder_images = self.define_placeholder_images()
        self.final_message = "Setup Complete!\nYour system will reboot."
        self.start_time = None
        self.done_action = False

        self.layout = FloatLayout(size=(PHYSICAL_WIDTH, PHYSICAL_HEIGHT))
        self.add_widget(self.layout)

        self.message_label = Label(text=self.final_message, font_size=self.font_size,
                                   pos=(PHYSICAL_WIDTH/2, self.app.bubble_rect[1] + self.app.bubble_rect[3]/2),
                                   size_hint=(None, None))
        self.layout.add_widget(self.message_label)
        Clock.schedule_interval(self.update, 1/30.)

    def define_placeholder_images(self):
        configs = [
            {
                "path": "setup_complete.png",
                "size": (500,165),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 250,
                        self.app.bubble_rect[1] + 60),
            },
            {
                "path": "navigation_legend.png",
                "size": (896,56),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 448,
                        self.app.bubble_rect[1] + 740),
            },
            {
                "path": "page_indicator_final.png",
                "size": (212,18),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 106,
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

    def update(self, dt):
        if self.start_time is None:
            self.start_time = Clock.get_time()
        elapsed = Clock.get_time() - self.start_time
        if not self.done_action and elapsed > 5:
            self.done_action = True
            self.finalize()

    def finalize(self):
        try:
            splash_src = self.app.get_path("splashscreen", "simple_arcades_intro.mp4")
            splash_dst = "/home/pi/RetroPie/splashscreens/simple_arcades_intro.mp4"
            shutil.move(splash_src, splash_dst)
            log(f"Moved {splash_src} -> {splash_dst}")
        except Exception as e:
            log(f"Failed to move splash video: {e}")
        log("Final screen finalize: removing wizard from autostart and rebooting.")
        self.app.remove_wizard_from_autostart()
        self.app.create_setup_flag()
        self.app.reboot_system()
