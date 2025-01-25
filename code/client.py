import pygame
import sys
import math
import time
import network
import variables as v
from classes import *
import ui
import funcs as f
import db

DB = db.Database()

pygame.init()


# ==== ПОДГОТОВКА ИГРЫ ===
def setup_balls_16():

    # Очищаем
    v.all_sprites.empty()
    v.balls.empty()
    v.pockets.empty()

    # создаем лунки
    setup_pockets()

    # создаем список игроков

    v.players = []
    v.current_player = 0

    if v.ONLINE:
        # будет меняться с подключением новых игроков
        v.players.append(Player(v.nickname))

    else:
        # локальный режим против бота
        v.players.append(Player(v.nickname))
        v.players.append(Player("Bot", bot=True, index=1))

    # Белый шар
    v.white_ball = Ball(v.WHITE, v.TABLE_RECT.centerx, v.TABLE_RECT.centery + 100)
    v.all_sprites.add(v.white_ball)

    # 15 цветных шаров (треугольником)
    row_count = 1
    placed = 0

    start_y = v.TABLE_RECT.centery
    while placed < 15:
        row_x = v.TABLE_RECT.centerx
        for i in range(row_count):
            if placed >= 15:
                break
            offset_x = (i - (row_count - 1) / 2) * (2 * v.BALL_RADIUS + 3)
            bx = row_x + offset_x
            by = start_y - (row_count - 1) * (v.BALL_RADIUS * 2 + 3)
            color = v.BALL_COLORS[placed % len(v.BALL_COLORS)]
            ball = Ball(color, bx, by, placed + 1)
            v.all_sprites.add(ball)
            placed += 1
        row_count += 1
    # инициализируем кий
    v.cue = Cue(v.players[0])


# создание лунок
def setup_pockets():
    v.pockets.empty()
    for pos in v.POCKET_POSITIONS:
        Pocket(*pos)


# ==== ИГРОВОЙ ЦИКЛ =====
def game_loop():
    running = True

    table_width = v.TABLE_RECT.width
    table_height = v.TABLE_RECT.height

    turn = None  # ход бота
    last_sync_time = time.time()

    if not v.ONLINE:
        try:
            from bot import bot_take_turn
        except:
            pass

    while running:
        dt = v.CLOCK.tick(v.FPS)
        current_time = time.time()

        # просим синхронизацию у сервера
        if v.IS_CLIENT:
            if current_time - last_sync_time >= v.SYNC_INTERVAL:
                last_sync_time = current_time
                network.request_sync()

        # ход бота -> создаем ивент=
        if not v.ONLINE:
            if v.players[v.current_player].bot:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))

        # игровые ивенты
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ИВЕНТ ХОДА БОТА
            elif event.type == pygame.USEREVENT + 1:
                # AI

                turn = bot_take_turn(
                    f.all_balls_stopped,
                    v.balls,
                    v.WHITE,
                    v.white_ball,
                    table_width,
                    table_height,
                )
                if turn:
                    # передаём ход
                    v.current_player = (v.current_player + 1) % len(v.players)

            # НАЖАТИЕ
            elif event.type == pygame.KEYDOWN:
                # пауза
                if event.key == pygame.K_ESCAPE:
                    return "pause"

                """
                Условия моего хода:
                    f.is_my_turn(): current_player is me
                    not v.ONLINE: офлайн режим против бота
                    v.IS_CLIENT: я не хост
                    not (len(v.players) == 1): больше 1 человека в руме

                """

                if v.ONLINE and v.chat_input_flag is True:
                    ui.Chat.handle_event(event)

                if (f.is_my_turn()) and ((not v.ONLINE) or not (len(v.players) == 1)):
                    if v.ONLINE:
                        v.GAME_STARTED = (
                            True  # игра начата, если онлайн, подключиться уже нельзя
                        )

                    else:
                        turn = None  # последний ход за мной, а не за ботом

                    """
                    Условия начала хода:
                        event.key == pygame.K_SPACE: нажат пробел
                        v.cue.force_window_active: кий активен
                    """
                    if event.key == pygame.K_SPACE and v.cue.force_window_active:
                        # запоминаем параметры хода
                        angle = v.cue.angle
                        force = v.cue.current_force

                        # ХОДИМ
                        v.cue.shoot()

                        # СИНХРОНИЗАЦИЯ в онлайн режиме
                        if v.ONLINE:
                            if v.IS_CLIENT:
                                # отправляем серверу удар
                                network.send_shoot(angle, force)

                            elif v.IS_SERVER:
                                # меняем параметры белого шара
                                v.white_ball.vx += math.cos(angle) * force
                                v.white_ball.vy += math.sin(angle) * force

                                # передаем ход следующему
                                v.current_player = (v.current_player - 1) % len(
                                    v.players
                                )
                                # отправляем стейт на клиенты
                                network.broadcast_state()

                        # ОФЛАЙН РЕЖИМ передаем ход следующему
                        else:
                            v.current_player = (v.current_player - 1) % len(v.players)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Если МОЙ ход + шары стоят => открыть "окно силы"

                if v.ONLINE and v.chat_input_area.collidepoint(event.pos):
                    v.chat_input_flag = True
                elif (
                    not (v.ONLINE or v.chat_input_area.collidepoint(event.pos))
                    and v.chat_input_flag == True
                ):
                    v.chat_input_flag = False
                elif f.is_my_turn() and f.all_balls_stopped():
                    v.cue.initiate_force_window()

        # проверка на попадание в лунки
        f.check_balls()

        # обновляем "окно силы"
        v.cue.update_force(dt)

        # Локально обновляем физику (и на клиенте тоже, для плавности)
        v.all_sprites.update()

        # Отрисовка
        v.screen.fill((40, 40, 40))
        pygame.draw.rect(v.screen, v.GREEN, v.TABLE_RECT)
        v.pockets.draw(v.screen)
        v.balls.draw(v.screen)
        v.cue.draw(v.screen)

        if v.ONLINE:
            ui.Chat.draw()

        ui.draw_scoreboard()

        """Отрисовка ожидания
            v.ONLINE: онлайн режим
            v.IS_SERVER: мы хост
            len(v.players) == 1: пока никто кроме нас не зашел
        """
        if v.ONLINE and len(v.players) == 1:
            text = f"Сервер: {v.SERVER_IP}:{v.SERVER_PORT}. Ожидаем второго игрока..."
            ui.draw_text_center(
                text, pygame.font.Font(v.FONT_PATH, 25), v.RED, v.WIDTH // 2 - 200, 100
            )
        pygame.display.flip()

        # КОНЕЦ ИГРЫ
        if len(v.balls) <= 1:

            if v.ONLINE and v.AUTHED:
                db.db.update_rating(v.username, v.players[0].score)

            return "end"

    return "end"


# ==== ОСНОВНАЯ ФУНКЦИЯ ====
def main():
    while True:
        # Если мы в главном меню
        if v.current_state == v.STATE_MENU:
            act = ui.main_menu()

            # локальная игра
            if act == "local_game":
                # обновляем параметры
                v.ENABLE_HINTS = False
                v.current_state = v.STATE_PLAYING
                v.ONLINE = False

                # подготавливаем игру
                setup_balls_16()

            # сетевая игра
            elif act == "network_game":
                # обновляем параметры
                v.current_state = v.STATE_PLAYING
                v.ENABLE_HINTS = False
                v.ONLINE = True

                # подготавливаем игру
                setup_balls_16()

            # выход
            elif act == "quit":
                pygame.quit()
                sys.exit()

        # Если мы в игре
        elif v.current_state == v.STATE_PLAYING:
            res = game_loop()
            # пауза
            if res == "pause":
                v.current_state = v.STATE_PAUSE

            # конец игры
            elif res == "end":
                v.current_state = v.STATE_END

        # Если мы на паузе
        elif v.current_state == v.STATE_PAUSE:
            pick = ui.pause_menu()

            # продолжить
            if pick == "resume":
                v.current_state = v.STATE_PLAYING

            # вернуться в меню
            elif pick == "menu":
                # обновляем глобальные переменные
                v.IS_CLIENT = False
                v.IS_SERVER = False
                v.ONLINE = False
                v.GAME_STARTED = False
                v.current_state = v.STATE_MENU
        # Если игра закончилась
        elif v.current_state == v.STATE_END:
            pick = ui.end_game_screen()

            # вернуться в меню
            if pick == "menu":
                v.current_state = v.STATE_MENU
