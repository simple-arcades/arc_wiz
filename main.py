# main.py
from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')

import os
import sys
import warnings

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage

# Use absolute imports referencing the package name 'arcade_wizard'
from arcade_wizard.constants import PHYSICAL_WIDTH, PHYSICAL_HEIGHT, FPS, SETUP_COMPLETE_FLAG, APP_LOG_FILE
from arcade_wizard.utils import log
from arcade_wizard.screen_manager import AppScreenManager
from arcade_wizard.screens.welcome_screen import WelcomeScreen
from arcade_wizard.screens.timezone_screen import EnterTimezoneScreen
from arcade_wizard.screens.terms_screen import TermsScreen
from arcade_wizard.screens.wifi_screen import WiFiScreen
from arcade_wizard.screens.update_screen import UpdateScreen
from arcade_wizard.screens.final_screen import FinalScreen

class Application(App):
    def build(self):
        # Set window size to the physical dimensions.
        Window.size = (PHYSICAL_WIDTH, PHYSICAL_HEIGHT)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Load font paths (for use by Label widgets later)
        try:
            self.nes_font_path = self.get_path("fonts", "NESCyrillic_gamelist.ttf")
            self.tiny_font_path = self.get_path("fonts", "TinyUnicode.ttf")
        except Exception as e:
            log(f"Failed to load fonts: {e}")
            self.nes_font_path = None
            self.tiny_font_path = None

        # Load background and bubble images as Kivy textures.
        self.background_texture = self.load_bg(self.get_path("images", "background_lg.png"))
        self.bubble_texture = self.load_bubble(self.get_path("images", "bubble_lg.png"))
        # Mimic the pygame bubble_rect (centered)
        self.bubble_rect = [PHYSICAL_WIDTH // 2 - 300, PHYSICAL_HEIGHT // 2 - 200, 600, 400]

        # Load background music.
        self.load_music(self.get_path("sounds", "background_music.ogg"))

        # Create and configure our screen manager.
        self.screen_manager = AppScreenManager(app=self)
        self.register_screens()
        return self.screen_manager

    def get_path(self, *subdirs):
        """Build an absolute path inside the project directory."""
        return os.path.join(self.base_dir, *subdirs)

    def load_bg(self, path):
        try:
            img = CoreImage(path).texture
            return img
        except Exception as e:
            log(f"Failed to load background image {path}: {e}")
            return None

    def load_bubble(self, path):
        try:
            img = CoreImage(path, nocache=True).texture
            return img
        except Exception as e:
            log(f"Failed to load bubble image {path}: {e}")
            return None

    def load_music(self, path):
        if os.path.exists(path):
            try:
                self.bg_music = SoundLoader.load(path)
                if self.bg_music:
                    self.bg_music.loop = True
                    self.bg_music.volume = 0.2
                    self.bg_music.play()
            except Exception as e:
                log(f"Failed to load music {path}: {e}")
        else:
            log(f"Music file not found: {path}")

    def register_screens(self):
        # Create instances of each screen.
        welcome = WelcomeScreen(app=self)
        timezone = EnterTimezoneScreen(app=self)
        terms = TermsScreen(app=self)
        wifi = WiFiScreen(app=self)
        update = UpdateScreen(app=self)
        final = FinalScreen(app=self)

        # Add them to the screen manager.
        self.screen_manager.add_widget(welcome)
        self.screen_manager.add_widget(timezone)
        self.screen_manager.add_widget(terms)
        self.screen_manager.add_widget(wifi)
        self.screen_manager.add_widget(update)
        self.screen_manager.add_widget(final)
        self.screen_manager.current = 'welcome'

    def remove_wizard_from_autostart(self):
        from arcade_wizard.constants import AUTOSTART_PATH
        log(f"Removing wizard from {AUTOSTART_PATH}")
        if not os.path.exists(AUTOSTART_PATH):
            log(f"Autostart not found at {AUTOSTART_PATH}")
            return
        try:
            with open(AUTOSTART_PATH, "r") as f:
                lines = f.readlines()
            new_lines = [line for line in lines if "arcade_wizard" not in line]
            found_es = any("emulationstation" in ln for ln in new_lines)
            if not found_es:
                new_lines.append("emulationstation #auto\n")
            with open(AUTOSTART_PATH, "w") as f:
                f.writelines(new_lines)
            log("Removed wizard from autostart and ensured EmulationStation is set.")
        except Exception as e:
            log(f"Failed to edit autostart: {e}")

    def create_setup_flag(self):
        from arcade_wizard.constants import SETUP_COMPLETE_FLAG
        try:
            with open(SETUP_COMPLETE_FLAG, "w") as f:
                f.write("Setup completed.\n")
            log(f"Created setup completion flag at {SETUP_COMPLETE_FLAG}")
        except Exception as e:
            log(f"Failed to create setup completion flag: {e}")

    def reboot_system(self):
        import subprocess
        log("Rebooting now...")
        self.stop()
        subprocess.run(["sudo", "reboot"])
        sys.exit()

if __name__ == '__main__':
    from arcade_wizard.constants import SETUP_COMPLETE_FLAG
    if os.path.exists(SETUP_COMPLETE_FLAG):
        print("Setup wizard already completed.")
        sys.exit(0)
    log("Launching setup application.")
    Application().run()
