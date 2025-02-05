# widgets/onscreen_keyboard.py

from arcade_wizard.constants import PHYSICAL_WIDTH, PHYSICAL_HEIGHT, FPS, SETUP_COMPLETE_FLAG, APP_LOG_FILE, GRAY, LIGHT_GRAY, BLACK, BLUE, GREEN, RED, YELLOW
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.text import Label as CoreLabel

class OnScreenKeyboardPopup(Widget):
    def __init__(self, initial_text=""):
        super(OnScreenKeyboardPopup, self).__init__()
        self.font = None
        self.keys_normal = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["Shift", "z", "x", "c", "v", "b", "n", "m", "BS"],
            ["Special", "Space", "OK", "Back"],
        ]
        self.keys_special = [
            ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")"],
            ["-", "_", "=", "+", "[", "]", "{", "}", ";", ":"],
            ['"', "'", ",", ".", "/", "\\", "|", "`", "~"],
            ["Shift", "<", ">", "?", "^", "b", "n", "m", "BS"],
            ["Special", "Space", "OK", "Back"],
        ]
        self.keys = self.keys_normal
        self.shift = False
        self.special = False
        self.text = initial_text
        self.key_rects = []
        self.selected_row = 0
        self.selected_col = 0
        self.done = False
        self.prompt_label = ""

    def set_font(self, font):
        self.font = font

    def draw(self, canvas, mode, bottom_bar_rect):
        from kivy.graphics import Color, Rectangle
        with canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=bottom_bar_rect.pos, size=bottom_bar_rect.size)
            if not self.font:
                from kivy.core.text import Label as CoreLabel
                self.font = CoreLabel(font_size=36)
            key_w = 80
            key_h = 50
            margin = 5
            self.key_rects = []
            for row_index, row in enumerate(self.keys):
                for col_index, label in enumerate(row):
                    x = bottom_bar_rect.x + margin + col_index * (key_w + margin)
                    y = bottom_bar_rect.y + bottom_bar_rect.height - (row_index + 1) * (key_h + margin)
                    Color(1, 1, 1, 1)
                    Rectangle(pos=(x, y), size=(key_w, key_h))
                    core_label = CoreLabel(text=label, font_size=24)
                    core_label.refresh()
                    texture = core_label.texture
                    Rectangle(texture=texture, pos=(x, y), size=texture.size)
                    self.key_rects.append(((x, y, key_w, key_h), label, row_index, col_index))

    def handle_event(self, event):
        # Implement key handling logic (keyboard, joystick, mouse) here.
        pass

    def process_key(self, label):
        if label == "Shift":
            self.shift = not self.shift
        elif label == "Special":
            self.special = not self.special
            self.keys = self.keys_special if self.special else self.keys_normal
            self.selected_row = 0
            self.selected_col = 0
        elif label == "BS":
            self.text = self.text[:-1]
        elif label == "Space":
            self.text += " "
        elif label == "OK":
            self.done = True
        elif label == "Back":
            self.done = True
        else:
            char = label.upper() if self.shift else label
            self.text += char

    def get_text(self):
        return self.text
