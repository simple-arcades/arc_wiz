# screens/timezone_screen.py

import subprocess
import threading

from arcade_wizard.screen_manager import BaseScreen
from arcade_wizard.constants import GREEN, RED, BLUE
from arcade_wizard.utils import log, show_message

class EnterTimezoneScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super(EnterTimezoneScreen, self).__init__(app, name="timezone", **kwargs)
        self.zones = self.build_zones()
        self.selected_zone_index = 0
        if self.zones:
            self.zones[self.selected_zone_index]["hovered"] = True

        self.load_sounds()
        self.placeholder_images = []
        self.define_placeholder_images()

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
            log(f"Failed to load EnterTimezoneScreen sounds: {e}")
            self.click_sound = self.hover_sound = None

    def define_placeholder_images(self):
        configs = [
            {
                "path": "choose_timezone.png",
                "size": (822, 239),
                "pos": (
                    self.app.bubble_rect[0] + 1419 // 2 - 411,
                    self.app.bubble_rect[1] + 100,
                ),
            },
            {
                "path": "navigation_legend.png",
                "size": (896, 56),
                "pos": (
                    self.app.bubble_rect[0] + 1419 // 2 - 448,
                    self.app.bubble_rect[1] + 740,
                ),
            },
            {
                "path": "page_indicator_2.png",
                "size": (212, 18),
                "pos": (
                    self.app.bubble_rect[0] + 1419 // 2 - 106,
                    self.app.bubble_rect[1] + 880,
                ),
            },
        ]
        for cfg in configs:
            try:
                ip = self.app.get_path("images", cfg["path"])
                from kivy.core.image import Image as CoreImage
                texture = CoreImage(ip).texture
            except Exception as e:
                log(f"Failed to load image {cfg['path']}: {e}")
                texture = None
            self.placeholder_images.append({"texture": texture, "pos": cfg["pos"], "size": cfg["size"]})

    def build_zones(self):
        data = [
            {
                "name": "Pacific",
                "tz": "America/Los_Angeles",
                "map_img": "map_western.png",
                "map_size": (272, 150),
                "btn_norm": "western_normal_lg.png",
                "btn_hov": "western_hover_lg.png",
            },
            {
                "name": "Mountain",
                "tz": "America/Denver",
                "map_img": "map_mountain.png",
                "map_size": (272, 150),
                "btn_norm": "mountain_normal_lg.png",
                "btn_hov": "mountain_hover_lg.png",
            },
            {
                "name": "Central",
                "tz": "America/Chicago",
                "map_img": "map_central.png",
                "map_size": (272, 150),
                "btn_norm": "central_normal_lg.png",
                "btn_hov": "central_hover_lg.png",
            },
            {
                "name": "Eastern",
                "tz": "America/New_York",
                "map_img": "map_eastern.png",
                "map_size": (272, 150),
                "btn_norm": "eastern_normal_lg.png",
                "btn_hov": "eastern_hover_lg.png",
            },
        ]
        map_x_positions = [85, 411, 737, 1063]
        map_y = 420
        gap = 30
        zones = []
        for i, d in enumerate(data):
            try:
                mp = self.app.get_path("images", d["map_img"])
                from kivy.core.image import Image as CoreImage
                map_texture = CoreImage(mp).texture
            except Exception as e:
                log(f"Failed to load map image {d['map_img']}: {e}")
                map_texture = None
            ax_map = self.app.bubble_rect[0] + map_x_positions[i]
            ay_map = self.app.bubble_rect[1] + map_y
            try:
                bn_path = self.app.get_path("images", d["btn_norm"])
                bh_path = self.app.get_path("images", d["btn_hov"])
                btn_norm = CoreImage(bn_path).texture
                btn_hover = CoreImage(bh_path).texture
            except Exception as e:
                log(f"Failed to load button images for {d['name']}: {e}")
                btn_norm = btn_hover = None
            btn_w = 222
            btn_h = 55
            map_w = d["map_size"][0]
            ax_btn = ax_map + (map_w // 2) - (btn_w // 2)
            ay_btn = ay_map + d["map_size"][1] + gap
            zones.append({
                "name": d["name"],
                "tz": d["tz"],
                "map_texture": map_texture,
                "map_x": ax_map,
                "map_y": ay_map,
                "btn_norm": btn_norm,
                "btn_hov": btn_hover,
                "btn_rect": [ax_btn, ay_btn, btn_w, btn_h],
                "hovered": False,
            })
        return zones
