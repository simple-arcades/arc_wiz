# constants.py
import os

###############################################################################
# GLOBAL CONSTANTS
###############################################################################
PHYSICAL_WIDTH = 1920
PHYSICAL_HEIGHT = 1080
FPS = 60

LOG_DIR = "/home/pi/RetroPie/custom_scripts/logs"
APP_LOG_FILE = os.path.join(LOG_DIR, "setup_gui.log")
TERMS_LOG_FILE = os.path.join(LOG_DIR, "terms_agreement.log")

# Kivy colors are specified as RGBA tuples (values 0–1)
WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)
GRAY = (200/255., 200/255., 200/255., 1)
LIGHT_GRAY = (220/255., 220/255., 220/255., 1)
BLUE = (0, 0, 1, 1)
GREEN = (0, 200/255., 0, 1)
RED = (200/255., 0, 0, 1)
YELLOW = (1, 1, 0, 1)

SETUP_COMPLETE_FLAG = "/home/pi/RetroPie/custom_scripts/setup_wizard_completed"
AUTOSTART_PATH = "/opt/retropie/configs/all/autostart.sh"
AUTO_UPDATE_SCRIPT = "/home/pi/RetroPie/custom_scripts/update_system_auto.sh"
