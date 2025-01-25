import pygame
import network
import variables as v
import sys
import db
import auth_windows
from threading import Thread


# --- ГЛАВНОЕ МЕНЮ ---
def main_menu():
    """
    Главное меню
    Returns: pick (str)
    """

    selected = 0  # индекс выбранной кнопки

    opts = [
        "Новая игра (Локальная)",
        "Выбрать сервер",
        "Создать сервер (Локальная сеть)",
        "Создать сервер (Глобальная сеть)",
        "Выход",
    ]

    input_active = False  # флаг активного ввода никнейма
    # прямоугольник ввода
    input_rect = pygame.Rect(130, 70, 300, 50)
    login_rect = pygame.Rect(800, 70, 100, 50)
    register_rect = pygame.Rect(800, 110, 100, 50)
    logout_rect = login_rect
    # Цикл главного меню
    while True:
        # отрисовка тайтла
        v.screen.fill(v.DARK_GREEN)
        draw_text_center(
            "Бильярд", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, v.WIDTH // 2, 50
        )

        # отрисовка кнопко
        for idx, opt in enumerate(opts):
            ccolor = v.YELLOW if idx == selected else v.WHITE
            draw_text_center(
                opt,
                pygame.font.Font(v.FONT_PATH2, 20),
                ccolor,
                v.WIDTH // 2,
                170 + idx * 70,
            )

        # меняем шрифт
        font = pygame.font.Font(v.FONT_PATH, 36)

        # Отрисовка текстового поля
        pygame.draw.rect(
            v.screen,
            v.GRAY if input_active else v.WHITE,
            input_rect,
            0,
            border_radius=5,
        )
        pygame.draw.rect(v.screen, v.BLACK, input_rect, 2, border_radius=5)

        # Отображение никнейма
        text_surface = font.render(v.nickname, True, v.BLACK)
        v.screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))

        font = pygame.font.Font(v.FONT_PATH2, 15)  # меняем шрифт

        # отрисовка подсказки
        help_surface = font.render("Press Enter to save", True, v.GREEN)
        v.screen.blit(help_surface, (input_rect.x, input_rect.y + 55))

        if not v.AUTHED:
            font = pygame.font.Font(v.FONT_PATH2, 25)
            color = v.YELLOW if v.login_selected_flag else v.GREEN

            login_surface = font.render("Login", True, color)
            v.screen.blit(login_surface, (login_rect.x, login_rect.y))

            color = v.YELLOW if v.reg_selected_flag else v.GREEN

            register_surface = font.render("Register", True, color)
            v.screen.blit(register_surface, (register_rect.x, register_rect.y))
        else:
            font = pygame.font.Font(v.FONT_PATH2, 25)
            color = v.YELLOW if v.logout_selected_flag else v.GREEN

            logout_surface = font.render("Log out", True, color)
            v.screen.blit(logout_surface, (login_rect.x, login_rect.y))

            offset_y = 200
            for line in v.user_data:
                user_data_surface = font.render(line, True, v.WHITE)
                v.screen.blit(user_data_surface, (130, offset_y))
                offset_y += 40

        pygame.display.flip()
        v.CLOCK.tick(v.FPS)

        # Обработка событий
        for event in pygame.event.get():
            # Выход
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Нажатие
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверка нажатия на текстовое поле
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                if not v.AUTHED:
                    if v.login_selected_flag:
                        login_thread = Thread(target=auth_windows.login_window)
                        login_thread.start()
                    if v.reg_selected_flag:
                        reg_thread = Thread(target=auth_windows.register_window)
                        reg_thread.start()
                else:
                    if v.logout_selected_flag:
                        v.user_data = ""
                        v.drop_auth_data()

            # Набор букв при активном вводе
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:  # Сохранение никнейма
                    input_active = False
                    if v.AUTHED:
                        db.db.set_nickname(v.username, v.nickname)
                    v.update_auth_data()

                elif event.key == pygame.K_BACKSPACE:  # Удаление символа
                    v.nickname = v.nickname[:-1]
                else:
                    v.nickname += event.unicode

            # Выбор кнопок

            elif event.type == pygame.MOUSEMOTION:
                if not v.AUTHED:
                    if login_rect.collidepoint(event.pos):
                        v.login_selected_flag = True
                    else:
                        v.login_selected_flag = False
                    if register_rect.collidepoint(event.pos):
                        v.reg_selected_flag = True
                    else:
                        v.reg_selected_flag = False
                else:
                    if logout_rect.collidepoint(event.pos):
                        v.logout_selected_flag = True
                    else:
                        v.logout_selected_flag = False
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opts)

                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opts)

                elif event.key == pygame.K_RETURN:
                    pick = opts[selected]

                    # Начало локальной игры
                    if pick == "Новая игра (Локальная)":
                        return "local_game"

                    # Создание сервера на глобальной сети
                    elif pick == "Создать сервер (Глобальная сеть)":
                        if network.host_server(mode=v.GLOBAL_MODE):
                            return "network_game"
                        else:
                            continue

                    # Создание сервера на локальной сети
                    elif pick == "Создать сервер (Локальная сеть)":
                        if network.host_server(mode=v.LOCAL_MODE):
                            return "network_game"
                        else:
                            continue

                    # Выбор сервера
                    elif pick == "Выбрать сервер":
                        # Отрисовываем список серверов,
                        # Если сервер выбран, начинаем игру по сети
                        if server_list_screen():
                            return "network_game"
                        else:
                            continue

                    # Выход
                    elif pick == "Выход":
                        pygame.quit()
                        sys.exit()


# --- ПАУЗА ---
def pause_menu():
    """Меню при нажатии ESC во время игры
    Returns: pick (str)
    """

    selected = 0  # Индекс выбранной кнопки

    options = ["Вернуться в игру", "Вернуться в меню", "Выйти"]

    # Основной цикл
    while True:
        v.screen.fill((50, 50, 120))

        # рисуем тайтл
        draw_text_center(
            "ПАУЗА", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, v.WIDTH // 2, 80
        )

        # рисуем кнопки
        for idx, opt in enumerate(options):
            color = v.YELLOW if idx == selected else v.WHITE
            draw_text_center(
                opt,
                pygame.font.Font(v.FONT_PATH, 36),
                color,
                v.WIDTH // 2,
                200 + idx * 60,
            )

        pygame.display.flip()
        v.CLOCK.tick(v.FPS)

        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Выбор кнопок
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)

                # Нажатие на кнопку
                elif event.key == pygame.K_RETURN:
                    pick = options[selected]
                    if pick == "Вернуться в игру":
                        return "resume"

                    elif pick == "Вернуться в меню":
                        return "menu"

                    elif pick == "Выйти":
                        pygame.quit()
                        sys.exit()


# --- ЭКРАН ОКОНЧАНИЯ ---
def end_game_screen():
    """Меню после окончания игры
    Returns: pick (str)"""

    selected = 0  # индекс выбранной кнопки
    opts = ["Вернуться в меню", "Выйти"]

    # Основной цикл
    while True:
        v.screen.fill((100, 30, 30))

        # рисуем тайтл
        draw_text_center(
            "Игра завершена!",
            pygame.font.Font(v.FONT_PATH, 50),
            v.WHITE,
            v.WIDTH // 2,
            80,
        )

        for idx, opt in enumerate(opts):
            color = v.YELLOW if idx == selected else v.WHITE
            draw_text_center(
                opt,
                pygame.font.Font(v.FONT_PATH, 36),
                color,
                v.WIDTH // 2,
                200 + idx * 60,
            )

        pygame.display.flip()
        v.CLOCK.tick(v.FPS)

        # Обработчик событий
        for event in pygame.event.get():
            # Выход
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Выбор кнопки
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opts)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opts)

                # Нажатие на кнопку
                elif event.key == pygame.K_RETURN:
                    pick = opts[selected]
                    # вернуться в меню
                    if pick == "Вернуться в меню":
                        return "menu"
                    # выход из игры
                    elif pick == "Выйти":
                        pygame.quit()
                        sys.exit()


def server_list_screen() -> bool:
    """
    Отображает список доступных серверов в виде кнопок.
    Если серверов нет, выводит сообщение "Нет доступных серверов" и кнопку "Назад".
    """

    # получаем список серверов у центрального сервера
    servers = network.get_server_list()

    while True:

        # Отрисовка экрана
        v.screen.fill(v.DARK_GREEN)
        draw_text_center(
            "Доступные серверы",
            pygame.font.Font(v.FONT_PATH, 50),
            v.WHITE,
            v.WIDTH // 2,
            50,
        )

        # При наличии серверов отображаем у клиента
        if servers:
            for i, server in enumerate(servers):
                button_rect = pygame.Rect(v.WIDTH // 2 - 150, 150 + i * 50, 300, 40)
                pygame.draw.rect(v.screen, v.DARK_GRAY, button_rect)
                draw_text_center(
                    server,
                    pygame.font.Font(v.FONT_PATH, 30),
                    v.WHITE,
                    button_rect.centerx,
                    button_rect.centery,
                )
        # Если серверов нет
        else:
            draw_text_center(
                "Нет доступных серверов",
                pygame.font.Font(v.FONT_PATH, 40),
                v.WHITE,
                v.WIDTH // 2,
                v.HEIGHT // 2,
            )

        # Кнопка "Назад"
        back_button_rect = pygame.Rect(v.WIDTH // 2 - 100, v.HEIGHT - 100, 200, 50)
        pygame.draw.rect(v.screen, v.DARK_GRAY, back_button_rect)
        draw_text_center(
            "Назад",
            pygame.font.Font(v.FONT_PATH, 30),
            v.WHITE,
            back_button_rect.centerx,
            back_button_rect.centery,
        )

        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():

            # Выход
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Нажатие ЛКМ
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                mouse_x, mouse_y = event.pos

                # Проверяем, нажата ли кнопка "Назад"
                if back_button_rect.collidepoint(mouse_x, mouse_y):
                    v.current_state = v.STATE_MENU
                    return False

                # Проверяем, нажата ли кнопка с сервером
                for i, server in enumerate(servers):

                    button_rect = pygame.Rect(v.WIDTH // 2 - 150, 150 + i * 50, 300, 40)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        # Подключаемся к выбранному серверу
                        ip, port = server.split(":")

                        # меняем параметры
                        v.SERVER_IP = ip
                        v.SERVER_PORT = int(port)
                        v.IS_SERVER = False
                        v.IS_CLIENT = True

                        # меняем состояние
                        v.current_state = v.STATE_PLAYING

                        # подключаемся к серверу
                        if network.connect_to_server(v.SERVER_IP, v.SERVER_PORT):
                            return True
                        else:
                            v.current_state = v.STATE_MENU
                            return False


def draw_scoreboard() -> None:
    """
    Рисует счет игроков на экране.
    """

    font = pygame.font.Font(v.FONT_PATH, 36)

    # отступ
    x_offset = 50
    y_offset = 20

    # рисуем счет
    for i, player in enumerate(v.players):
        if i == 0:
            text = f"{player.name}: {player.score} (you)"
        else:
            text = f"{player.name}: {player.score}"
        color = (
            v.YELLOW if player.index == v.current_player else v.WHITE
        )  # Подсвечиваем текущего игрока

        text_surface = font.render(text, True, color)
        v.screen.blit(text_surface, (x_offset, y_offset + i * 40))


def draw_text_center(
    text: str, font: pygame.font.Font, color: pygame.Color, x: int, y: int
) -> None:
    """Рисует заданный текст в заданном месте
    Args:
        text: str
        font: pygame.font.Font
        color: pygame.Color
        x: int
        y: int
    Returns:
        None
    """
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    v.screen.blit(surf, rect)


import pygame


class Chat:
    def draw():

        # Зона истории сообщений
        chat_area = pygame.Rect(
            v.CHAT_X + 10, v.CHAT_Y + 10, v.CHAT_WIDTH - 20, v.CHAT_HEIGHT - 50
        )
        y_offset = chat_area.bottom

        # Рисуем историю сообщений
        font = pygame.font.Font(v.FONT_PATH2, 13)
        for author, text in reversed(v.chat[v.chat_scroll :]):

            message_surface = font.render(f"{author}: {text}", True, v.TEXT_COLOR)
            y_offset -= v.FONT_SIZE + 5
            if y_offset < chat_area.top:
                break
            v.screen.blit(message_surface, (chat_area.left, y_offset))

        # Зона ввода
        v.chat_input_area = pygame.Rect(
            v.CHAT_X + 10, v.CHAT_Y + v.CHAT_HEIGHT - 40, v.CHAT_WIDTH - 20, 30
        )
        pygame.draw.rect(v.screen, v.INPUT_COLOR, v.chat_input_area)
        pygame.draw.rect(v.screen, v.CHAT_BORDER_COLOR, v.chat_input_area, 2)

        # Рисуем текущий ввод
        input_surface = font.render(v.current_input, True, v.TEXT_COLOR)
        v.screen.blit(
            input_surface, (v.chat_input_area.left + 5, v.chat_input_area.top + 5)
        )

        # Рисуем курсор
        if (
            v.chat_input_flag and pygame.time.get_ticks() % 1000 < 500
        ):  # Мигающий курсор
            cursor_x = v.chat_input_area.left + 5 + input_surface.get_width()
            pygame.draw.line(
                v.screen,
                v.CURSOR_COLOR,
                (cursor_x, v.chat_input_area.top + 5),
                (cursor_x, v.chat_input_area.bottom - 5),
                2,
            )

    def handle_event(event):
        """Обрабатывает события ввода для чата."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if v.current_input.strip():
                    if v.IS_SERVER:
                        v.chat.append(
                            (v.nickname, v.current_input.strip())
                        )  # Добавляем сообщение от пользователя
                        network.broadcast_state()
                    else:
                        network.send_message()
                    v.current_input = ""  # Очищаем ввод
            elif event.key == pygame.K_BACKSPACE:
                v.current_input = v.current_input[:-1]  # Удаляем последний символ
            elif event.key == pygame.K_UP:
                v.chat_scroll = max(v.chat_scroll - 1, 0)  # Прокрутка вверх
            elif event.key == pygame.K_DOWN:
                v.chat_scroll = min(
                    v.chat_scroll + 1, len(v.chat) - 1
                )  # Прокрутка вниз
            else:
                if (
                    v.font.size(v.current_input)[0] < v.CHAT_WIDTH - 40
                ):  # Ограничение длины строки
                    v.current_input += event.unicode
