# screens/update_screen.py

import threading
import queue
import subprocess
import time

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock

from arcade_wizard.constants import WHITE, YELLOW, GREEN, RED, AUTO_UPDATE_SCRIPT, PHYSICAL_WIDTH
from arcade_wizard.utils import log
from arcade_wizard.screen_manager import BaseScreen

class UpdateScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super(UpdateScreen, self).__init__(app, name="update", **kwargs)
        self.font_size = '24sp'
        self.placeholder_images = self.define_placeholder_images()
        self.status_message = "Checking for updates..."
        self.message_queue = queue.Queue()
        self.update_complete = False

        from kivy.core.window import Window
        self.layout = FloatLayout(size=Window.size)

        self.add_widget(self.layout)

        self.status_label = Label(text=self.status_message, font_size=self.font_size,
                                  pos=(PHYSICAL_WIDTH/2, self.app.bubble_rect[1] + self.app.bubble_rect[3]/2),
                                  size_hint=(None, None))
        self.layout.add_widget(self.status_label)
        self.scan_updates()
        Clock.schedule_interval(self.update, 1/30.)

    def define_placeholder_images(self):
        configs = [
            {
                "path": "update_screen.png",
                "size": (683,165),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 342,
                        self.app.bubble_rect[1] + 60),
            },
            {
                "path": "navigation_legend.png",
                "size": (896,56),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 448,
                        self.app.bubble_rect[1] + 740),
            },
            {
                "path": "page_indicator_5.png",
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

    def scan_updates(self):
        def worker():
            self.message_queue.put(("info", "Looking for updates..."))
            try:
                proc = subprocess.Popen(["sudo", AUTO_UPDATE_SCRIPT],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        text=True)
                for line in proc.stdout:
                    self.message_queue.put(("line", line.rstrip("\n")))
                proc.wait()
                rc = proc.returncode
                self.message_queue.put(("done", rc))
            except Exception as e:
                self.message_queue.put(("error", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def update(self, dt):
        while not self.message_queue.empty():
            msg = self.message_queue.get()
            if msg[0] == "info":
                self.status_message = msg[1]
            elif msg[0] == "line":
                self.status_message = msg[1]
                log(f"UpdateScript: {msg[1]}")
            elif msg[0] == "done":
                rc = msg[1]
                if rc == 0:
                    self.status_message = "Updates applied successfully. Press designated SELECT button to continue."
                else:
                    self.status_message = f"Update script failed (RC={rc})."
                self.update_complete = True
            elif msg[0] == "error":
                self.status_message = f"Error: {msg[1]}"
                self.update_complete = True
        self.status_label.text = self.status_message

    def on_touch_down(self, touch):
        if self.update_complete:
            self.finish_update_flow()
            return True
        return super(UpdateScreen, self).on_touch_down(touch)

    def finish_update_flow(self):
        self.app.screen_manager.current = 'final'
