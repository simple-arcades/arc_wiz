# screen_manager.py
from kivy.uix.screenmanager import ScreenManager, Screen
from arcade_wizard.utils import log
from kivy.core.window import Window

class AppScreenManager(ScreenManager):
    def __init__(self, app, **kwargs):
        super(AppScreenManager, self).__init__(**kwargs)
        self.app = app

# A common base class for our screens so we can share drawing routines.
class BaseScreen(Screen):
    def __init__(self, app, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.app = app
        self._update_event = None

    def on_enter(self):
        # Start an update loop if needed.
        from kivy.clock import Clock
        self._update_event = Clock.schedule_interval(self.update, 1/60.)
    
    def on_leave(self):
        if self._update_event:
            self._update_event.cancel()
            self._update_event = None

    def update(self, dt):
        # Override in subclasses if periodic updating is needed.
        pass

    from kivy.core.window import Window

    def render_background_and_bubble(self, canvas):
        from kivy.graphics import Rectangle, Color
        with canvas:
            Color(1, 1, 1, 1)
            if self.app.background_texture:
                Rectangle(texture=self.app.background_texture,
                          pos=(0, 0),
                          size=Window.size)
            if self.app.bubble_texture:
                bx, by, bw, bh = self.app.bubble_rect
                Rectangle(texture=self.app.bubble_texture, pos=(bx, by), size=(bw, bh))
