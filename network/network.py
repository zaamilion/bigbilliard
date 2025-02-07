import socket
import json
import time
import threading
import math
import game.variables as v
from game.classes import Player
import game.funcs as f
import requests

def get_local_ip():
    """Возвращает локальный IP-адрес машины."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Подключаемся к "мнимому" адресу, чтобы узнать интерфейс
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return None  # В крайнем случае возвращаем localhost


# =========== СЕТЕВЫЕ ФУНКЦИИ ==========
def register_with_central_server(ip, port, output=True):
    """Регистрирует игровой сервер на центральном сервере."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(
                (v.CENTRAL_SERVER_IP, 5000)
            )  # Замените на реальный IP центрального сервера
            s.sendall(f"register:{ip}:{port}".encode("utf-8"))
            response = s.recv(4096).decode("utf-8")
            print(response)
            if response == "registered":
                if output:
                    print(f"Game server registered at {ip}:{port}")
                return True
            else:
                print(f"Registration failed: {response}")
                return False
    except Exception as e:
        print(f"Failed to register with central server: {e}")
        return False


def get_public_ip():
    ip = None
    try:

        ip = requests.get("https://api.ipify.org").text
    except Exception:
        pass
    if ip:
        return ip
    if not ip:
        return


def keep_alive(ip, port):
    while not v.GAME_STARTED and v.ONLINE and v.IS_SERVER:
        register_with_central_server(ip, port, output=False)
        time.sleep(10)


def host_server(mode):
    if mode == v.GLOBAL_MODE:
        v.SERVER_IP = get_public_ip()
    elif mode == v.LOCAL_MODE:
        v.SERVER_IP = get_local_ip()
    if not v.SERVER_IP:
        return False
    v.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    v.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        v.server_socket.bind(("0.0.0.0", v.SERVER_PORT))
    except OSError as e:
        print(f"Bind не удался на '0.0.0.0':{v.SERVER_PORT}, ошибка: {e}")
        return False

    v.server_socket.listen(1)
    print("Сервер запущен, жду подключения...")
    v.IS_SERVER = True
    v.IS_CLIENT = False
    if not register_with_central_server(v.SERVER_IP, v.SERVER_PORT):
        print("Failed to register with central server. Exiting.")
        return False

    def accept_thread():
        while True:
            conn, addr = v.server_socket.accept()
            v.client_sockets.append(conn)
            print("Клиент подключился:", addr)
            t = threading.Thread(target=server_read_thread, args=(conn,))
            t.start()

    v.server_thread = threading.Thread(target=accept_thread)
    v.server_thread.start()

    keep_alive_thread = threading.Thread(
        target=keep_alive,
        args=(
            v.SERVER_IP,
            v.SERVER_PORT,
        ),
    )
    keep_alive_thread.start()

    return True


def server_read_thread(conn):
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            msg = data.decode("utf-8")
            handle_client_message(msg)
        except:
            break

    conn.close()
    if conn in v.client_sockets:
        v.client_sockets.remove(conn)


def get_server_list():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(
                (v.CENTRAL_SERVER_IP, 5000)
            )  # Замените на IP центрального сервера
            s.sendall(f"get_servers".encode("utf-8"))
            data = s.recv(4096).decode("utf-8")
            return [line for line in data.split("\n") if line]
    except Exception as e:
        print(f"Failed to fetch server list: {e}")
        return []


def broadcast(msg):
    for c in v.client_sockets:
        try:
            c.sendall(msg.encode("utf-8"))
        except:
            pass


def handle_client_message(msg):
    # Пришёл JSON
    try:
        data = json.loads(msg)
        t = data.get("type")
        if t == "shoot":
            angle = data["angle"]
            force = data["force"]
            # Применяем на сервере
            if force > 0:
                f.playsound(v.beat_sound)
            v.white_ball.vx += math.cos(angle) * force
            v.white_ball.vy += math.sin(angle) * force
            v.current_player = (v.current_player - 1) % len(v.players)
            broadcast_state()
        elif t == "spin":
            # Клиент меняет spin_x/spin_y
            v.cue.spin_x = data["spin_x"]
            v.cue.spin_y = data["spin_y"]

        elif t == "sync_request":
            broadcast_state()
        elif t == "register_in_game":
            v.enemies_nicknames.append(data["nickname"])
            v.players.append(
                Player(
                    v.enemies_nicknames[-1],
                    index=len(v.players),
                    username=data["username"],
                )
            )
            data = [(player.name, player.username) for player in v.players]
            f.playsound(v.beat_sound)
            broadcast(json.dumps({"type": "players", "data": data}))

        elif t == "message":
            nickname = data["nickname"]
            message = data["text"]
            v.chat.append((nickname, message))
            broadcast_state()

    except:
        pass


def broadcast_state():
    state = []
    for b in v.balls:
        state.append(
            {
                "num": b.number,
                "x": b.rect.centerx,
                "y": b.rect.centery,
                "vx": b.vx,
                "vy": b.vy,
                "sx": b.spin_x,
                "sy": b.spin_y,
                "alive": b.alive(),
            }
        )
    msg = json.dumps(
        {
            "type": "state",
            "balls": state,
            "current_player": v.current_player,
            "chat": v.chat,
        }
    )
    broadcast(msg)


def connect_to_server(ip, port):
    v.IS_SERVER = False
    v.IS_CLIENT = True
    v.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        v.client_socket.connect((ip, port))
        v.LOBBY = port - 5007
        print("Клиент подключён к серверу.")
    except OSError as e:
        print("Не удалось подключиться к серверу:", e)
        return False

    def client_read():
        try:
            while True:
                data = v.client_socket.recv(4096)
                if not data:
                    break
                handle_server_message(data.decode("utf-8"))
        except ConnectionAbortedError:
            print("Соединение разорвано сервером.")
        except Exception as e:
            print(f"Ошибка в client_read: {e}")
        finally:
            v.client_socket.close()
            print("Сокет клиента закрыт.")

    v.client_thread = threading.Thread(target=client_read)
    v.client_thread.start()
    send_nickname()
    return True


def handle_server_message(msg):
    try:
        data = json.loads(msg)
        if data["type"] == "state":
            # Обновляем позиции шаров

            ball_states = data["balls"]
            v.chat = data["chat"]
            v.current_player = data["current_player"]
            for st in ball_states:
                num = st["num"]
                alive = st["alive"]
                if alive:
                    # Ищем шар
                    found = None
                    for b in v.balls:
                        if b.number == num:
                            found = b
                            break
                    if found:
                        found.rect.center = (st["x"], st["y"])
                        found.vx = st["vx"]
                        found.vy = st["vy"]
                        found.spin_x = st["sx"]
                        found.spin_y = st["sy"]
                else:
                    # Удаляем шар
                    for b in v.balls:
                        if b.number == num:
                            b.kill()
        elif data["type"] == "players":
            data = data["data"]
            nicknames = [d[0] for d in data]

            usernames = [d[1] for d in data]
            v.players = []
            me_index = usernames.index(v.username)
            for idx in range(me_index, len(nicknames)):
                v.players.append(
                    Player(nicknames[idx], index=idx, username=usernames[idx])
                )
            for idx in range(0, me_index):
                v.players.append(
                    Player(nicknames[idx], index=idx, username=usernames[idx])
                )
    except:
        pass


def send_shoot(angle, force):
    if v.client_socket:
        payload = {"type": "shoot", "angle": angle, "force": force, "lobby": v.LOBBY}
        v.client_socket.sendall(json.dumps(payload).encode("utf-8"))


def request_sync():
    if v.client_socket and not v.client_socket._closed:
        payload = {"type": "sync_request", "lobby": v.LOBBY}
        v.client_socket.sendall(json.dumps(payload).encode("utf-8"))


def send_nickname():
    if v.client_socket and not v.client_socket._closed:
        payload = {
            "type": "register_in_game",
            "lobby": v.LOBBY,
            "nickname": v.nickname,
            "username": v.username,
        }
        v.client_socket.sendall(json.dumps(payload).encode("utf-8"))


def send_message():
    if v.client_socket and not v.client_socket._closed:
        payload = {
            "type": "message",
            "lobby": v.LOBBY,
            "nickname": v.nickname,
            "text": v.current_input.strip(),
        }
        v.client_socket.sendall(json.dumps(payload).encode("utf-8"))
