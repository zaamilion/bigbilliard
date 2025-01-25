import pygame
from dotenv import load_dotenv
import os
import json
import db

load_dotenv()


current_player = 0


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
BALL_COLORS = [
    (255, 255, 0, 255),  # Yellow
    (0, 0, 255, 255),  # Blue
    (255, 0, 0, 255),  # Red
    (128, 0, 128, 255),  # Purple
    (255, 165, 0, 255),  # Orange
    (0, 128, 0, 255),  # Green
    (0, 0, 128, 255),  # Navy
    (0, 0, 0, 255),  # Magenta
    (200, 200, 0, 255),  # Yellow-greenish
    (200, 0, 200, 255),  # Pinkish-purple
    (0, 200, 200, 255),  # Cyan
    (180, 90, 90, 255),  # Brownish-red
    (90, 180, 90, 255),  # Light green
    (90, 90, 180, 255),  # Light blue
    (128, 128, 128, 255),  # Gray
]


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
        user_data = ["Profile ", f"@{udata[0]}", f"Global score: {udata[1]}"]


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


login_selected_flag = False
reg_selected_flag = False
logout_selected_flag = False
