# game options/settings

TITLE = "Jumpy!"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'fonts/Amatic SC'
SAVES_FILE = 'Saves'
COIN_FILE = 'coins'
SPRITESHEET1 = 'spritesheet_jumper.png'

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_FRICTION_ON_SNOW = -0.04
PLAYER_GRAV = 0.8
PLAYER_JUMP_V = 20

# Game properties
BOOST_POWER = 40
BUBBLE_POWER = 15
POW_SPAWN_RATIO = 7
CLOUD_BG_SPAWN_RATIO = 6
CLOUD_SPAWN_RATIO = 3
COIN_SPAWN_RATIO = 3
MOVING_PLAT_SPAWN_RATIO = 11
MOB_FREQ = 15000
PLATFORM_LAYER = 1
PLAYER_LAYER = 4
POW_LAYER = 2
MOB_LAYER = 3
CLOUD_LAYER = 0
# Spikey properties
SPIKEY_ACC = 1
SPIKEY_SPAWN_RATIO = 7
SPIKEY_FRAME_TIME = 155
# Wingman properties
WM_ACC_UP = -2
WM_ACC_DOWN = 1.5
WM_VEL = 0.14
WM_SPAWN_RATIO = 3
WM_FRAME_TIME = 70
# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 55,),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100,)]

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (68, 142, 249)
ALMOST_WHITE = (226, 246, 247)
BG_COLOR = LIGHTBLUE

# Time properties
SEC = 1000
MINUTE = SEC * 60
