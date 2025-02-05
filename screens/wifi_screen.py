# screens/wifi_screen.py

import os
import sys
import time
import threading
import queue
import subprocess

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.clock import Clock

from arcade_wizard.constants import BLACK, WHITE, YELLOW, GREEN, RED, PHYSICAL_WIDTH, PHYSICAL_HEIGHT
from arcade_wizard.utils import log
from arcade_wizard.screen_manager import BaseScreen
from arcade_wizard.widgets.onscreen_keyboard import OnScreenKeyboardPopup

GRAY = (200/255., 200/255., 200/255., 1)
LIGHT_GRAY = (220/255., 220/255., 220/255., 1)
SOUND_ENABLED = True

class WiFiScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super(WiFiScreen, self).__init__(app, name="wifi", **kwargs)
        self.networks = []
        self.connected_ssid = None
        self.selected_network_index = -1

        self.osk_mode = None
        self.osk = None
        self.osk_prompt_text = ""
        self.connection_thread = None
        self.message_queue = queue.Queue()
        self.status_message = None
        self.status_color = BLACK
        self.status_expire_time = 0
        self.current_selection = 'networks'
        self.last_hover_time = 0
        self.hover_cooldown_ms = 300
        self.scan_interval = 10
        self.last_scan_time = 0

        # Define button and SSID list geometry (based on bubble)
        bx, by, bw, bh = self.app.bubble_rect
        self.button_width = 203
        self.button_height = 61
        self.button_y = by + 640

        self.rescan_button_rect = [bx + bw/2 - 320, self.button_y, self.button_width, self.button_height]
        self.manual_button_rect = [bx + bw/2 - 100, self.button_y, self.button_width, self.button_height]
        self.skip_button_rect = [bx + bw/2 + 120, self.button_y, self.button_width, self.button_height]

        self.ssid_box_width = 800
        self.ssid_box_height = 300
        self.ssid_box_x = bx + (bw - self.ssid_box_width) / 2
        self.ssid_box_y = by + 275

        self.ssid_scroll_offset = 0
        self.ssid_line_height = 30

        self.placeholder_images = self.define_placeholder_images()

        self.rescan_images = self.load_button_images("rescan")
        self.manual_images = self.load_button_images("manual_ssid")
        self.skip_images = self.load_button_images("skip")
        self.continue_images = self.load_button_images("continue")

        self.click_sound = None
        self.hover_sound = None
        self.load_sounds()

        self.user_just_clicked = False

        self.layout = FloatLayout(size=(PHYSICAL_WIDTH, PHYSICAL_HEIGHT))
        self.add_widget(self.layout)

        self.ssid_scroll_view = ScrollView(size_hint=(None, None),
                                             size=(self.ssid_box_width, self.ssid_box_height),
                                             pos=(self.ssid_box_x, self.ssid_box_y))
        self.ssid_label = Label(text="", font_size='24sp', color=BLACK, halign='left', valign='top', size_hint=(None, None))
        self.ssid_label.bind(texture_size=self.ssid_label.setter('size'))
        self.ssid_scroll_view.add_widget(self.ssid_label)
        self.layout.add_widget(self.ssid_scroll_view)

        self.rescan_button = Image(size_hint=(None, None), size=(self.button_width, self.button_height),
                                    pos=(self.rescan_button_rect[0], self.rescan_button_rect[1]))
        self.manual_button = Image(size_hint=(None, None), size=(self.button_width, self.button_height),
                                   pos=(self.manual_button_rect[0], self.manual_button_rect[1]))
        self.skip_button = Image(size_hint=(None, None), size=(self.button_width, self.button_height),
                                 pos=(self.skip_button_rect[0], self.skip_button_rect[1]))
        self.layout.add_widget(self.rescan_button)
        self.layout.add_widget(self.manual_button)
        self.layout.add_widget(self.skip_button)

        self.status_label = Label(text="", font_size='24sp', color=BLACK,
                                  pos=(PHYSICAL_WIDTH/2, self.button_y - 50), size_hint=(None, None))
        self.layout.add_widget(self.status_label)

        self.layout.bind(on_touch_down=self.on_touch_down)

        self.scan_wifi()
        Clock.schedule_interval(self.update, 1/30.)

    def define_placeholder_images(self):
        configs = [
            {
                "path": "connect_to_wifi.png",
                "size": (500,165),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 250,
                        self.app.bubble_rect[1] + 50),
            },
            {
                "path": "navigation_legend.png",
                "size": (896,56),
                "pos": (self.app.bubble_rect[0] + self.app.bubble_rect[2]/2 - 448,
                        self.app.bubble_rect[1] + 740),
            },
            {
                "path": "page_indicator_4.png",
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
                log(f"Failed to load WiFi placeholder {cfg['path']}: {e}")
                texture = None
            result.append({"texture": texture, "pos": cfg["pos"], "size": cfg["size"]})
        return result

    def load_button_images(self, base_name):
        from kivy.core.image import Image as CoreImage
        try:
            n = CoreImage(self.app.get_path("images", f"{base_name}_normal_sm.png")).texture
            h = CoreImage(self.app.get_path("images", f"{base_name}_hover_sm.png")).texture
            p = CoreImage(self.app.get_path("images", f"{base_name}_pressed_sm.png")).texture
        except Exception as e:
            log(f"Failed to load {base_name} button images: {e}")
            n = h = p = None
        return (n, h, p)

    def load_sounds(self):
        try:
            click_path = self.app.get_path("sounds", "select.ogg")
            hover_path = self.app.get_path("sounds", "hover.ogg")
            from kivy.core.audio import SoundLoader
            self.click_sound = SoundLoader.load(click_path)
            if self.click_sound:
                self.click_sound.volume = 0.5
            self.hover_sound = SoundLoader.load(hover_path)
            if self.hover_sound:
                self.hover_sound.volume = 0.1
        except Exception as e:
            log(f"Failed to load WiFi screen sounds: {e}")
            self.click_sound = self.hover_sound = None

    def on_touch_down(self, touch):
        x, y = touch.pos
        if self.ssid_scroll_view.collide_point(x, y):
            local_y = (y - self.ssid_scroll_view.y) + self.ssid_scroll_offset
            idx = int(local_y // self.ssid_line_height)
            if 0 <= idx < len(self.networks):
                self.selected_network_index = idx
                self.ask_for_password(idx)
                return True
        for rect, action in [(self.rescan_button_rect, self.scan_wifi),
                             (self.manual_button_rect, self.ask_for_custom_ssid),
                             (self.skip_button_rect, self.on_skip_or_continue)]:
            rx, ry, rw, rh = rect
            if rx <= x <= rx+rw and ry <= y <= ry+rh:
                if self.click_sound:
                    self.click_sound.play()
                action()
                return True
        return super(WiFiScreen, self).on_touch_down(touch)

    def ask_for_custom_ssid(self):
        self.osk_mode = "custom_ssid"
        self.osk = OnScreenKeyboardPopup("")
        self.osk.prompt_label = "Enter your custom SSID name"
        self.layout.add_widget(self.osk)

    def ask_for_password(self, index=None, custom_ssid=None):
        if index is not None:
            ssid = self.networks[index]
        else:
            ssid = custom_ssid
        self.osk_mode = "password"
        self.osk = OnScreenKeyboardPopup("")
        self.osk.prompt_label = f"Enter password for {ssid}"
        self.layout.add_widget(self.osk)

    def on_skip_or_continue(self):
        if self.connected_ssid:
            self.app.screen_manager.current = 'update'
        else:
            self.app.screen_manager.current = 'final'

    def try_connect(self, ssid, password):
        def worker():
            self.message_queue.put(("info", f"Connecting to {ssid}", BLACK))
            cmd = ["/usr/bin/nmcli", "dev", "wifi", "connect", ssid, "password", password]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
                if "successfully activated" in res.stdout:
                    self.message_queue.put(("success", ssid, BLACK))
                else:
                    self.message_queue.put(("error", f"Failed: {res.stdout}", RED))
            except subprocess.CalledProcessError as cpe:
                err_msg = f"nmcli failed (RC={cpe.returncode}): {cpe.stderr or cpe.stdout}"
                self.message_queue.put(("error", err_msg, RED))
            except subprocess.TimeoutExpired:
                self.message_queue.put(("error", "Connection timed out.", RED))
            except Exception as ex:
                self.message_queue.put(("error", str(ex), RED))
        threading.Thread(target=worker, daemon=True).start()

    def update(self, dt):
        while not self.message_queue.empty():
            msg = self.message_queue.get()
            if len(msg) == 3:
                msg_type, content, color = msg
            else:
                msg_type, content = msg
                color = BLACK
            if msg_type == "info":
                self.set_status_message(content, color, 3)
            elif msg_type == "success":
                if content not in self.networks:
                    self.networks.insert(0, content)
                self.connected_ssid = content
                self.set_status_message(f"Connected to {content}!", color, 3)
                self.scan_wifi()
            elif msg_type == "error":
                self.set_status_message(content, color, 4)
        self.ssid_label.text = "\n".join(self.networks)
        self.status_label.text = self.status_message if self.status_message and time.time() < self.status_expire_time else ""

    def set_status_message(self, text, color, duration=2):
        self.status_message = text
        self.status_color = color
        self.status_expire_time = time.time() + duration

    def scan_wifi(self):
        def scan_worker():
            now = time.time()
            if (now - self.last_scan_time) < self.scan_interval:
                time.sleep(self.scan_interval - (now - self.last_scan_time))
            self.message_queue.put(("info", "Scanning networks...", BLACK))
            subprocess.run(["/usr/bin/nmcli", "device", "wifi", "rescan"], capture_output=True)
            time.sleep(2)
            p = subprocess.run(["/usr/bin/nmcli", "-t", "-f", "SSID,IN-USE", "device", "wifi", "list"],
                               capture_output=True, text=True)
            lines = p.stdout.strip().split("\n")
            new_networks = []
            new_connected = None
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue
                ssid_val = parts[0].strip()
                in_use = parts[1].strip()
                if in_use == "*":
                    new_connected = ssid_val
                if ssid_val:
                    new_networks.append(ssid_val)
            self.networks = new_networks
            self.connected_ssid = new_connected
            self.last_scan_time = time.time()
            self.message_queue.put(("info", f"Found {len(new_networks)} networks.", BLACK))
        threading.Thread(target=scan_worker, daemon=True).start()
