import game.variables as v
import math
import pygame
import random
import network.db as db
import json
import os


def all_balls_stopped():
    """Проверяет, что все шары стоят
    Returns: bool
    """
    for b in v.balls:
        if abs(b.vx) > 0.05 or abs(b.vy) > 0.05:
            return False
    return True


def is_my_turn():
    """Проверяет, что сейчас мой ход
    Returns: bool
    """
    if v.ONLINE:
        return (v.current_player) == v.players[0].index
    else:
        return (v.current_player) == 0


def check_balls():
    """Проверяет шары на попадание в лунки.
    Награждает за забитые шары
    Штрафует за забитый белый шар
    """

    previous_player = (v.current_player - 1) % len(v.players)

    for ball in v.balls:
        for pocket in v.pockets:

            # дистанция до лунки
            distance = math.hypot(
                ball.rect.centerx - pocket.rect.centerx,
                ball.rect.centery - pocket.rect.centery,
            )

            if distance < v.POCKET_RADIUS:
                if ball.color == v.WHITE:
                    # Если это белый шар, штрафуем игрока
                    v.players[previous_player].score += v.WHITE_BALL_PUNISHMENT

                    if v.IS_SERVER:
                        v.chat.append(
                            (
                                "Server",
                                f"Игрок {v.players[previous_player].name} забил белый шар! Штраф {v.WHITE_BALL_PUNISHMENT} очко",
                            )
                        )

                    # Возвращаем на стол
                    ball.rect.center = (
                        v.TABLE_RECT.centerx,
                        v.TABLE_RECT.centery + 100,
                    )
                    ball.vx, ball.vy = 0, 0

                else:
                    # Если это цветной шар, увеличиваем счет игрока
                    if previous_player == 0:
                        sound = random.choice(v.scored_sounds)
                        sound.play()
                    if v.IS_SERVER:
                        v.chat.append(
                            (
                                "Server",
                                f"Игрок {v.players[previous_player].name} забил шар! +{v.BALL_AWARD} очко",
                            )
                        )
                    v.players[previous_player].score += v.BALL_AWARD
                    if v.players[previous_player].score > v.players[0].score:
                        pygame.mixer.music.load(f"{v.to_sounds_path}/panic.mp3")
                        pygame.mixer.music.play()
                    ball.kill()  # Убираем шар с поля


def playsound(sound: pygame.mixer.Sound, volume: float = 1.0):
    if v.SOUNDS_ENABLED:
        sound.set_volume(volume)
        sound.play()


def get_inventory():
    try:
        with open("./assets/inventory.json") as file:
            return json.load(file)
    except:
        return None


def check_module_downloaded(module):
    name = module["name"]
    type = module["type"]
    if type == "sounds":
        return name in os.listdir("./assets/sounds")
    elif type == "balls patterns":
        return name + ".json" in os.listdir("./assets/balls patterns")
    elif type == "loading screen":
        return name + ".png" in os.listdir("./assets/loading screen")
    elif type == "table pattern":
        return name + ".png" in os.listdir("./assets/table patterns")


def get_module_selected():
    with open("./data/сurrent_packs.json") as file:
        data = json.load(file)
    return data


def update_current_packs():
    v.data["sounds"] = v.current_music_pack
    v.data["balls patterns"] = v.current_balls_pack
    v.data["loading screen"] = v.current_loading_screen
    v.data["table pattern"] = v.current_table_pattern
    with open("./data/сurrent_packs.json", "w") as file:
        json.dump(v.data, file)
