import pygame
from dotenv import load_dotenv
import os
import json
import network.db as db
from threading import Thread
load_dotenv()


current_player = 0

class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

CENTRAL_SERVER_IP = os.environ.get("CENTRAL_SERVER_IP")
CURRENT_VERSION = os.environ.get("CURRENT_VERSION")

SERVER_IP = ""
SERVER_PORT = 5007
IS_SERVER = True
IS_CLIENT = False
ONLINE = False
GAME_STARTED = False
sound_played = False
# =========== ПЕРЕМЕННЫЕ ==========
server_socket = None
client_sockets = []
server_thread = None
client_socket = None
client_thread = None
balls = pygame.sprite.Group()
players = []
cue = None
white_ball = None

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_AI_GAME = "ai_playing"
STATE_PAUSE = "pause"
STATE_END = "end"
LOCAL_MODE = "local"
GLOBAL_MODE = "global"
current_state = STATE_MENU

# --- НАСТРОЙКИ ОКНА ---
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
pygame.display.set_caption("Бильярд")
icon = pygame.image.load("./assets/icons/icon.png")
pygame.display.set_icon(icon)
# Цвета
GREEN = (34, 139, 34)
DARK_GREEN = (10, 80, 10)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
YELLOW = (255, 255, 0)

BLACK_BG = (36, 36, 45)

# --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ ---
FRICTION = 0.98
SPIN_FACTOR = 0.02
POCKET_RADIUS = 25
BALL_RADIUS = 15
TABLE_PADDING = 50
FPS = 60
CLOCK = pygame.time.Clock()
SYNC_INTERVAL = 0.5
LAST_SHOOT_TIME = None
BALL_AWARD = 1
WHITE_BALL_PUNISHMENT = -1
# Флаги
ENABLE_SPIN = True
ENABLE_HINTS = False  # если выберем "Обучающий режим"
LOBBY = 0
CUE_COLOR = RED
# 16 шаров
TOTAL_BALLS = 16


# Сетевая часть

TABLE_RECT = pygame.Rect(
    TABLE_PADDING, TABLE_PADDING, WIDTH - 2 * TABLE_PADDING, HEIGHT - 2 * TABLE_PADDING
)

POCKET_POSITIONS = [
    (TABLE_RECT.left, TABLE_RECT.top),
    (TABLE_RECT.centerx, TABLE_RECT.top),
    (TABLE_RECT.right, TABLE_RECT.top),
    (TABLE_RECT.left, TABLE_RECT.bottom),
    (TABLE_RECT.centerx, TABLE_RECT.bottom),
    (TABLE_RECT.right, TABLE_RECT.bottom),
]

# --- ГРУППЫ СПРАЙТОВ ---
all_sprites = pygame.sprite.Group()
pockets = pygame.sprite.Group()

username = None
nickname = "Player"
password = None
enemies_nicknames = []
WIN = False
LOSE = False


def load_auth_data():
    global username, nickname, password
    try:
        with open("./data/auth_data.json") as file:
            data = json.load(file)
            username = data["username"]
            nickname = data["nickname"]
            password = data["password"]
    except:
        pass


def update_auth_data():
    global username, nickname, password
    try:
        with open("./data/auth_data.json", "w") as file:
            data = {"username": username, "nickname": nickname, "password": password}
            json.dump(data, file)
    except:
        pass


def drop_auth_data():
    global username, nickname, password, AUTHED
    try:
        with open("./data/auth_data.json", "w") as file:
            data = {}
            json.dump(data, file)
            username = None
            password = None
            AUTHED = False
    except:
        pass


load_auth_data()

AUTHED = db.db.auth(username, password)

user_data = ""


def update_user_data():
    global user_data
    udata = db.db.get_user_data(username)
    if udata:
        user_data = [
            f"@{udata[0]}",
            f"Global score: {udata[1]}",
            f"Balance: {udata[2]}",
        ]


if AUTHED:
    udata = db.db.get_user_data(username)
    update_user_data()


# --- Настройки ---
CHAT_WIDTH = 400
CHAT_HEIGHT = 200
CHAT_X = 50
CHAT_Y = 500
FONT_SIZE = 20
CHAT_BG_COLOR = (30, 30, 30)  # Тёмно-серый фон чата
CHAT_BORDER_COLOR = (200, 200, 200)  # Светло-серый для границ
TEXT_COLOR = (255, 255, 255)  # Белый цвет текста
INPUT_COLOR = (50, 50, 50)  # Цвет фона для ввода
CURSOR_COLOR = (255, 255, 255)  # Цвет курсора

# --- Инициализация ---
pygame.init()


FONT_PATH = "./assets/font.ttf"
FONT_PATH2 = "./assets/font2.ttf"
font = pygame.font.Font(None, FONT_SIZE)
font = pygame.font.Font(FONT_PATH, FONT_SIZE)
# --- Переменные чата ---
chat = [("Server", "Welcome to BigBilliard!")]
current_input = ""  # Текущее сообщение, вводимое пользователем
chat_scroll = 0  # Прокрутка чата

chat_input_area = pygame.Rect(0, 0, 0, 0)
chat_input_flag = False

shop_selected_flag = False
profile_selected_flag = False
login_selected_flag = False
reg_selected_flag = False
logout_selected_flag = False


# SOUNDS

current_track = None


with open("./data/сurrent_packs.json") as current_file:
    data = json.load(current_file)
    current_music_pack = data["sounds"]
    current_balls_pack = data["balls patterns"]
    current_loading_screen = data["loading screen"]
    current_table_pattern = data["table pattern"]
if current_music_pack not in os.listdir("./assets/sounds/"):
    data["sounds"] = "default"
    current_music_pack = "default"
if current_balls_pack + ".json" not in os.listdir("./assets/balls patterns/"):
    data["balls patterns"] = "default"
    current_balls_pack = "default"
if current_loading_screen + ".png" not in os.listdir("./assets/loading screen"):
    data["loading screen"] = "default"
    current_loading_screen = "default"
if current_table_pattern + ".png" not in os.listdir("./assets/table patterns"):
    data["table pattern"] = "default"
    current_table_pattern = "default"

with open("./data/сurrent_packs.json", "w") as current_file:
    json.dump(data, current_file)
LOADING_SCREEN_IMAGE = "./assets/loading screen/" + current_loading_screen + ".png"

table_pattern_img = pygame.image.load(
    "./assets/table patterns/" + current_table_pattern + ".png"
)

with open("./assets/balls patterns/" + current_balls_pack + ".json") as colors:
    BALL_COLORS = json.load(colors)

to_sounds_path = f"./assets/sounds/{current_music_pack}"
click_sound = pygame.mixer.Sound(f"{to_sounds_path}/select_menu.mp3")
gamestart_sound = pygame.mixer.Sound(f"{to_sounds_path}/join_me.mp3")
playerjoin_sound = pygame.mixer.Sound(f"{to_sounds_path}/join_enemy.mp3")

beat_sound = pygame.mixer.Sound(f"{to_sounds_path}/beat.mp3")

battle_start_music = [
    f"{to_sounds_path}/ingame_music/{filename}"
    for filename in os.listdir(f"{to_sounds_path}/ingame_music")
]

scored_sounds = [
    pygame.mixer.Sound(f"{to_sounds_path}/replics/{filename}")
    for filename in os.listdir(f"{to_sounds_path}/replics")
]
balls_beat_sound = pygame.mixer.Sound(f"{to_sounds_path}/balls_beat.mp3")
battle_all_music = battle_start_music

MUSIC_ENABLED = True
SOUNDS_ENABLED = True

loadingscreen_pack_icon = pygame.image.load(
    "./assets/icons/loadingscreen_pack_icon.png"
)
sounds_pack_icon = pygame.image.load("./assets/icons/sounds_pack_icon.png")
ballspattern_pack_icon = pygame.image.load("./assets/icons/ballspattern_pack_icon.png")
table_pattern_icon = pygame.image.load("./assets/icons/tablepattern_icon.png")


def update_current_packs():
    global data, current_music_pack, current_balls_pack, current_loading_screen, current_table_pattern, LOADING_SCREEN_IMAGE, table_pattern_img, BALL_COLORS, to_sounds_path, click_sound, gamestart_sound, playerjoin_sound, beat_sound, battle_start_music, scored_sounds, balls_beat_sound, battle_all_music
    with open("./data/сurrent_packs.json") as current_file:
        data = json.load(current_file)
        current_music_pack = data["sounds"]
        current_balls_pack = data["balls patterns"]
        current_loading_screen = data["loading screen"]
        current_table_pattern = data["table pattern"]

    if current_music_pack not in os.listdir("./assets/sounds/"):
        data["sounds"] = "default"
        current_music_pack = "default"
    if current_balls_pack + ".json" not in os.listdir("./assets/balls patterns/"):
        data["balls patterns"] = "default"
        current_balls_pack = "default"
    if current_loading_screen + ".png" not in os.listdir("./assets/loading screen"):
        data["loading screen"] = "default"
        current_loading_screen = "default"
    if current_table_pattern + ".png" not in os.listdir("./assets/table patterns"):
        data["table pattern"] = "default"
        current_table_pattern = "default"

    with open("./data/сurrent_packs.json", "w") as current_file:
        json.dump(data, current_file)
    LOADING_SCREEN_IMAGE = "./assets/loading screen/" + current_loading_screen + ".png"

    table_pattern_img = pygame.image.load(
        "./assets/table patterns/" + current_table_pattern + ".png"
    )
    with open("./assets/balls patterns/" + current_balls_pack + ".json") as colors:
        BALL_COLORS = json.load(colors)

    to_sounds_path = f"./assets/sounds/{current_music_pack}"
    click_sound = pygame.mixer.Sound(f"{to_sounds_path}/select_menu.mp3")
    gamestart_sound = pygame.mixer.Sound(f"{to_sounds_path}/join_me.mp3")
    playerjoin_sound = pygame.mixer.Sound(f"{to_sounds_path}/join_enemy.mp3")

    beat_sound = pygame.mixer.Sound(f"{to_sounds_path}/beat.mp3")

    battle_start_music = [
        f"{to_sounds_path}/ingame_music/{filename}"
        for filename in os.listdir(f"{to_sounds_path}/ingame_music")
    ]

    scored_sounds = [
        pygame.mixer.Sound(f"{to_sounds_path}/replics/{filename}")
        for filename in os.listdir(f"{to_sounds_path}/replics")
    ]

    balls_beat_sound = pygame.mixer.Sound(f"{to_sounds_path}/balls_beat.mp3")
    battle_all_music = battle_start_music


update_current_packs()

downloading_packs = []
succes_buying_packs = []
failed_buying_packs = []
