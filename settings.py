#game settings
TITLE  = 'Naruto Calculation'
WIDTH  = 480
HEIGHT = 600
FPS    = 60
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20

# Game properties
BOOST_POWER = 50
POW_SPAWN_PCT = 7
MOB_FREQ = 20000
WHITEBOARD_LAYER = 3
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0

# calculation range
CALC_MIN = 10
CALC_MAX = 15+1

# starting platforms
PLATFORM_LIST = [(0,HEIGHT-60),
                 (WIDTH/2-50,HEIGHT*3/4-50),
                 (125,HEIGHT-350),
                 (350,200),
                 (175,100)]

# define colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED   = (255,0,0)
GREEN = (0,255,0)
BLUE  = (0,0,255)
YELLOW= (255,255,0)
GRAY  = (100,100,100)
LIGHTBLUE = (0,100,155)
BGCOLOR = LIGHTBLUE
