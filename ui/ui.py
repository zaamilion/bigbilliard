import pygame
import network.network as network
import game.variables as v
import sys
import network.db as db
import ui.auth_windows as auth_windows
from threading import Thread
import game.funcs as f
import time
import network.s3 as s3
import json
import os


class Option:
    def __init__(self, text, enabled):
        self.text = text
        self.enabled = enabled


# --- ГЛАВНОЕ МЕНЮ ---
def main_menu():
    try:
        if v.MUSIC_ENABLED:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.load(f"{v.to_sounds_path}/menu.mp3")
            pygame.mixer.music.play(-1)
            v.current_track = "menu"
    except:
        pass
    """
    Главное меню
    Returns: pick (str)
    """

    selected = 0  # индекс выбранной кнопки
    leaderboard = Leaderboard()
    opts = [
        Option(text="Новая игра (Локальная)", enabled=True),
        Option("Выбрать сервер", enabled=v.AUTHED),
        Option("Создать сервер (Локальная сеть)", enabled=v.AUTHED),
        Option("Создать сервер (Глобальная сеть)", enabled=v.AUTHED),
        Option("Настройки", enabled=True),
        Option("Выход", enabled=True),
    ]

    flag_leaderboard = False
    input_active = False  # флаг активного ввода никнейма
    # прямоугольник ввода
    input_rect = pygame.Rect(130, 70, 300, 50)
    login_rect = pygame.Rect(800, 70, 100, 50)
    register_rect = pygame.Rect(800, 110, 100, 50)
    logout_rect = login_rect
    profile_rect = pygame.Rect(130, 200, 100, 50)
    # Цикл главного меню
    while True:
        # отрисовка тайтла
        if not pygame.mixer.music.get_busy() and v.MUSIC_ENABLED:
            pygame.mixer.music.load(f"{v.to_sounds_path}/menu.mp3")
            pygame.mixer.music.play()
            v.current_track = "menu"
        opts = [
            Option(text="Новая игра (Локальная)", enabled=True),
            Option("Выбрать сервер", enabled=v.AUTHED),
            Option("Создать сервер (Локальная сеть)", enabled=v.AUTHED),
            Option("Создать сервер (Глобальная сеть)", enabled=v.AUTHED),
            Option("Настройки", enabled=True),
            Option("Выход", enabled=True),
        ]
        v.screen.fill(v.BLACK_BG)
        draw_text_center(
            "Бильярд", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, v.WIDTH // 2, 50
        )

        # отрисовка кнопко
        for idx, opt in enumerate(opts):
            ccolor = v.YELLOW if idx == selected else v.WHITE
            if opt.enabled is False:
                ccolor = v.GRAY
            draw_text_center(
                opt.text,
                pygame.font.Font(v.FONT_PATH2, 30),
                ccolor,
                v.WIDTH // 2,
                170 + idx * 70,
            )

        # меняем шрифт
        font = pygame.font.Font(v.FONT_PATH, 35)

        # Отрисовка текстового поля
        pygame.draw.rect(
            v.screen,
            v.GRAY if input_active else v.WHITE,
            input_rect,
            0,
            border_radius=20,
        )
        pygame.draw.rect(v.screen, v.BLACK, input_rect, 2, border_radius=20)

        # Отображение никнейма
        text_surface = font.render(v.nickname, True, v.BLACK)
        v.screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 5))

        font = pygame.font.Font(v.FONT_PATH2, 15)  # меняем шрифт

        # отрисовка подсказки
        help_surface = font.render("Press Enter to save", True, v.GRAY)
        v.screen.blit(help_surface, (input_rect.x, input_rect.y + 55))

        if not v.AUTHED:
            font = pygame.font.Font(v.FONT_PATH2, 25)
            color = v.YELLOW if v.login_selected_flag else v.WHITE

            login_surface = font.render("Login", True, color)
            v.screen.blit(login_surface, (login_rect.x, login_rect.y))

            color = v.YELLOW if v.reg_selected_flag else v.WHITE

            register_surface = font.render("Register", True, color)
            v.screen.blit(register_surface, (register_rect.x, register_rect.y))

            font = pygame.font.Font(v.FONT_PATH2, 10)

            help_surface = font.render("Auth to play with friends", True, v.GRAY)
            v.screen.blit(
                help_surface,
                ((v.WIDTH // 2) - (help_surface.get_rect().width // 2), 200),
            )
        else:
            font = pygame.font.Font(v.FONT_PATH2, 25)
            color = v.YELLOW if v.logout_selected_flag else v.WHITE

            logout_surface = font.render("Log out", True, color)
            v.screen.blit(logout_surface, (login_rect.x, login_rect.y))

            color = v.YELLOW if v.profile_selected_flag else v.WHITE
            profile_surface = font.render("Profile", True, color)
            v.screen.blit(profile_surface, (profile_rect.x, profile_rect.y))

        if flag_leaderboard is True:
            leaderboard.draw(v.screen, (250, 100))
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
                        f.playsound(v.click_sound)
                        login_thread = Thread(target=auth_windows.login_window)
                        login_thread.start()
                    if v.reg_selected_flag:
                        f.playsound(v.click_sound)
                        reg_thread = Thread(target=auth_windows.register_window)
                        reg_thread.start()
                else:
                    if v.logout_selected_flag:
                        v.user_data = ""
                        f.playsound(v.click_sound)
                        v.drop_auth_data()
                    if v.profile_selected_flag:
                        f.playsound(v.click_sound)
                        v.profile_selected_flag = False
                        profile_menu()

            # Набор букв при активном вводе
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:  # Сохранение никнейма
                    f.playsound(v.click_sound)
                    input_active = False
                    if v.AUTHED:
                        db.db.set_nickname(v.username, v.nickname)
                    v.update_auth_data()

                elif event.key == pygame.K_BACKSPACE:  # Удаление символа
                    v.nickname = v.nickname[:-1]
                else:
                    if text_surface.get_width() < input_rect.width - 50:
                        v.nickname += event.unicode
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                flag_leaderboard = True

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
                    if profile_rect.collidepoint(event.pos):
                        v.profile_selected_flag = True
                    else:
                        v.profile_selected_flag = False
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selectedd = (selected - 1) % len(opts)
                    if opts[selectedd].enabled is False:
                        for idx, opt in enumerate(opts[selectedd::-1]):
                            if opt.enabled:
                                selectedd -= idx
                                break
                    if opts[selectedd].enabled:
                        selected = selectedd
                elif event.key == pygame.K_DOWN:
                    selectedd = (selected + 1) % len(opts)
                    if opts[selectedd].enabled is False:
                        for idx, opt in enumerate(opts[selectedd:]):
                            if opt.enabled:
                                selectedd += idx
                                break
                    if opts[selectedd].enabled:
                        selected = selectedd
                elif event.key == pygame.K_RETURN:
                    pygame.mixer.music.stop()
                    f.playsound(v.click_sound)
                    pick = opts[selected].text

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
                    elif pick == "Настройки":
                        settings_menu()
                        continue

                    # Выход
                    elif pick == "Выход":
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.KEYDOWN and pygame.K_TAB in event.keys:
                flag_leaderboard = True
            else:
                flag_leaderboard = False


def settings_menu():
    selected = 0  # индекс выбранной кнопки
    opts = [
        Option(text="Музыка " + "вкл." if v.MUSIC_ENABLED else "выкл.", enabled=True),
        Option(text="Звуки " + "вкл." if v.SOUNDS_ENABLED else "выкл.", enabled=True),
        Option(text="Назад", enabled=True),
    ]

    # Цикл главного меню
    while True:
        opts = [
            Option(
                text="Музыка " + ("вкл." if v.MUSIC_ENABLED else "выкл."), enabled=True
            ),
            Option(
                text="Звуки " + ("вкл." if v.SOUNDS_ENABLED else "выкл."), enabled=True
            ),
            Option(text="Назад", enabled=True),
        ]
        v.screen.fill(v.BLACK_BG)
        draw_text_center(
            "Настройки", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, v.WIDTH // 2, 50
        )

        # отрисовка кнопко
        for idx, opt in enumerate(opts):
            ccolor = v.YELLOW if idx == selected else v.WHITE
            if opt.enabled is False:
                ccolor = v.GRAY
            draw_text_center(
                opt.text,
                pygame.font.Font(v.FONT_PATH2, 30),
                ccolor,
                v.WIDTH // 2,
                170 + idx * 70,
            )
        pygame.display.flip()
        v.CLOCK.tick(v.FPS)

        # Обработка событий
        for event in pygame.event.get():
            # Выход
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selectedd = (selected - 1) % len(opts)
                    if opts[selectedd].enabled is False:
                        for idx, opt in enumerate(opts[selectedd::-1]):
                            if opt.enabled:
                                selectedd -= idx
                                break
                    if opts[selectedd].enabled:
                        selected = selectedd
                elif event.key == pygame.K_DOWN:
                    selectedd = (selected + 1) % len(opts)
                    if opts[selectedd].enabled is False:
                        for idx, opt in enumerate(opts[selectedd:]):
                            if opt.enabled:
                                selectedd += idx
                                break
                    if opts[selectedd].enabled:
                        selected = selectedd
                elif event.key == pygame.K_RETURN:
                    pygame.mixer.music.stop()
                    f.playsound(v.click_sound)
                    pick = opts[selected].text

                    # Начало локальной игры
                    if pick[:6] == "Музыка":
                        v.MUSIC_ENABLED = not v.MUSIC_ENABLED
                        continue

                    # Создание сервера на глобальной сети
                    elif pick[:5] == "Звуки":
                        v.SOUNDS_ENABLED = not v.SOUNDS_ENABLED
                        continue
                    elif pick == "Назад":
                        return


def profile_menu():
    inventory = db.db.get_inventory(v.username)

    y_scroll = 0
    font_10 = pygame.font.Font(v.FONT_PATH2, 15)
    font_15 = pygame.font.Font(v.FONT_PATH2, 18)

    selected_button = None
    can_up = False
    can_down = False
    while True:

        v.screen.fill(v.BLACK_BG)

        # Рисуем тайтл
        font = pygame.font.Font(v.FONT_PATH, 50)
        surf = font.render("ИНВЕНТАРЬ", True, v.YELLOW)
        v.screen.blit(
            surf,
            (
                (v.WIDTH // 2) - 50,
                50,
            ),
        )
        draw_text_center("ПРОФИЛЬ", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, 200, 80)

        # Конфигурация отображения инвентар

        offset_y = 200
        font = pygame.font.Font(v.FONT_PATH2, 25)
        if pygame.time.get_ticks() % 1000 < 5:
            t = Thread(target=v.update_user_data)
            t.start()
        for line in v.user_data:
            user_data_surface = font.render(line, True, v.WHITE)
            v.screen.blit(user_data_surface, (80, offset_y))
            offset_y += 40

        # +=========== INVENTORY ==========+

        item_width = 120  # Ширина прямоугольника
        item_height = 150  # Высота прямоугольника
        row_padding = 20  # Отступ между строками

        # Начало отрисовки предметов

        start_x = item_width * 0.3  # Центрируем по горизонтали
        start_y = 10 + y_scroll  # Начало отрисовки предметов

        inventory_surface = pygame.Surface((750, 400), pygame.SRCALPHA)
        inventory_rect = inventory_surface.get_rect()

        can_up = start_y < 0
        can_down = (
            start_y + (((item_height + row_padding)) * (((len(inventory)) + 4) // 5))
            >= inventory_rect.h
        )
        for item_idx, item in enumerate(inventory):
            row = item_idx // 5

            x = start_x + (item_idx % 5 * (item_width + row_padding))
            y = start_y + (((item_height + row_padding)) * row)

            if y < -item_height:
                continue
            elif y > inventory_rect.h:
                break

            downloaded = f.check_module_downloaded(item)
            selected_items = f.get_module_selected()
            selected = selected_items[item["type"]] == item["name"]
            item_rect = pygame.Rect(x, y, item_width, item_height)
            # Рисуем прямоугольник
            pygame.draw.rect(
                inventory_surface,
                item.get("color", v.GRAY),
                (x, y, item_width, item_height),
                border_bottom_left_radius=15,
                border_bottom_right_radius=15,
            )

            # Отображаем название предмета внутри прямоугольника
            item_surface = font_15.render(item["name"], True, v.WHITE)
            img_surf = None

            # Определяем иконку в зависимости от типа предмета
            match item["type"]:
                case "sounds":
                    img_surf = v.sounds_pack_icon
                case "balls patterns":
                    img_surf = v.ballspattern_pack_icon
                case "loading screen":
                    img_surf = v.loadingscreen_pack_icon
                case "table pattern":
                    img_surf = v.table_pattern_icon

            if img_surf:
                inventory_surface.blit(img_surf, (x, y))

            inventory_surface.blit(
                item_surface,
                (
                    x + (item_width - item_surface.get_width()) // 2,
                    y + (item_height - item_surface.get_height()) - 5,
                ),
            )

            # Отображаем статус "скачан" или "не скачан"

            if not downloaded:
                downloaded_status = "not downloaded"
                downloaded_color = (255, 150, 150, 255)
                downloaded_surface = font_10.render(
                    downloaded_status, True, downloaded_color
                )
                inventory_surface.blit(
                    downloaded_surface,
                    (
                        x + (item_width - downloaded_surface.get_width()) // 2,
                        y,  # Позиция статуса "скачан"
                    ),
                )

            # Отображаем статус "выбран" или "не выбран"
            if selected:
                selected_surface = font_10.render("Selected", True, v.GREEN)
                inventory_surface.blit(
                    selected_surface,
                    (
                        x + 5,
                        y,  # Позиция статуса "выбран"
                    ),
                )
            mouse_pos = list(pygame.mouse.get_pos())
            mouse_pos[0] -= v.WIDTH // 3
            mouse_pos[1] -= 140
            mouse_pos = tuple(mouse_pos)
            if item_rect.collidepoint(mouse_pos) and not selected:
                overlay = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                pygame.draw.rect(
                    overlay,
                    (0, 0, 0, 200),
                    (0, 0, item_width, item_height),
                    border_bottom_right_radius=15,
                    border_bottom_left_radius=15,
                )
                inventory_surface.blit(overlay, (x, y))

                text = "Download" if not downloaded else "Select"
                if item in v.downloading_packs:
                    text = "Downloading"
                    ticks = pygame.time.get_ticks()
                    if ticks % 1000 <= 250:
                        add = ""
                    elif ticks % 1000 <= 500:
                        add = "."
                    elif ticks % 1000 <= 750:
                        add = ".."
                    else:
                        add = "..."
                    text += add

                    button = font_10.render(
                        text,
                        True,
                        (v.WHITE),
                    )
                    button_pos = (
                        x + (item_width) // 2 - 15 * len(text) // 4,
                        y + (item_height) // 2 - 20,
                    )
                    button_rect = pygame.Rect(button_pos[0], button_pos[1], 90, 20)
                else:
                    button_pos = (
                        x + (item_width) // 2 - 20 * len(text) // 4,
                        y + (item_height) // 2 - 20,
                    )
                    button_rect = pygame.Rect(button_pos[0], button_pos[1], 90, 20)
                    button = font_15.render(
                        text,
                        True,
                        (v.YELLOW if button_rect.collidepoint(mouse_pos) else v.WHITE),
                    )
                inventory_surface.blit(button, button_pos)
                if button_rect.collidepoint(mouse_pos):
                    selected_button = (text, button_rect, item)
            pygame.draw.rect(
                inventory_surface, v.BLACK, (0, 0, 750, 400), 1, border_radius=10
            )
            v.screen.blit(inventory_surface, (v.WIDTH // 3, 140))
        # Добавляем текст на кнопку
        back_button_rect = pygame.Rect(v.WIDTH // 2 - 100, v.HEIGHT - 100, 200, 50)
        pygame.draw.rect(v.screen, v.BLACK, back_button_rect, border_radius=25)
        draw_text_center(
            "Назад",
            pygame.font.Font(v.FONT_PATH2, 30),
            v.WHITE,
            back_button_rect.centerx,
            back_button_rect.centery,
        )
        shop_button_rect = pygame.Rect(v.WIDTH // 2 + 350, 50, 200, 50)

        font = pygame.font.Font(v.FONT_PATH, 50)
        color = v.GRAY if v.shop_selected_flag else v.WHITE

        login_surface = font.render("SHOP", True, color)
        v.screen.blit(login_surface, (shop_button_rect.x, shop_button_rect.y))

        pygame.display.flip()
        v.CLOCK.tick(v.FPS)

        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Возвращаемся в главное меню по нажатию ESC

            # Обработка клика на кнопку
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if v.shop_selected_flag:
                    f.playsound(v.click_sound)
                    v.shop_selected_flag = False
                    if shop_menu():
                        return
                    else:
                        inventory = db.db.get_inventory(v.username)
                if back_button_rect.collidepoint(event.pos):
                    f.playsound(v.click_sound)
                    return
                if not selected_button:
                    continue
                mouse_pos = list(event.pos)
                mouse_pos[0] -= v.WIDTH // 3
                mouse_pos[1] -= 140
                mouse_pos = tuple(mouse_pos)
                # Возвращаемся в главное меню при клике на кнопку
                if selected_button[1].collidepoint(mouse_pos):
                    f.playsound(v.click_sound)
                    if selected_button[0] == "Select":
                        if selected_button[2]["type"] == "sounds":
                            v.current_music_pack = selected_button[2]["name"]
                            pygame.mixer.music.load(
                                f"./assets/sounds/{v.current_music_pack}/menu.mp3"
                            )
                            pygame.mixer.music.play()
                        elif selected_button[2]["type"] == "balls patterns":
                            v.current_balls_pack = selected_button[2]["name"]
                        elif selected_button[2]["type"] == "table pattern":
                            v.current_table_pattern = selected_button[2]["name"]
                        else:
                            v.current_loading_screen = selected_button[2]["name"]
                        f.update_current_packs()
                        v.update_current_packs()
                        v.current_music_pack

                    elif selected_button[0] == "Download":
                        t = Thread(target=download_pack, args=(selected_button[2],))
                        t.start()
            elif event.type == pygame.MOUSEWHEEL:
                # Vertical scrolling (standard mouse wheel)
                if event.y != 0:
                    if (event.y < 0 and can_down) or (event.y > 0 and can_up):
                        y_scroll += event.y * 20  # Adjust scroll speed
            elif event.type == pygame.MOUSEMOTION:
                if shop_button_rect.collidepoint(event.pos):
                    v.shop_selected_flag = True
                else:
                    v.shop_selected_flag = False


def update_shop():
    v.update_user_data()
    inventory = db.db.get_inventory(v.username)
    s3.s3client.update_packs_data()
    with open("./data/packs_data.json") as file:
        packs = json.load(file)
    packs = list(
        filter(
            lambda x: x not in inventory,
            packs,
        )
    )
    return packs


def shop_menu():
    t = v.ThreadWithReturnValue(target=update_shop)
    t.start()
    y_scroll = 0
    font_10 = pygame.font.Font(v.FONT_PATH2, 15)
    font_15 = pygame.font.Font(v.FONT_PATH2, 18)
    packs = None
    selected_button = None
    can_up = False
    can_down = False
    while True:

        v.screen.fill(v.BLACK_BG)

        font = pygame.font.Font(v.FONT_PATH, 50)
        surf = font.render("SHOP", True, v.YELLOW)
        v.screen.blit(
            surf,
            (
                (v.WIDTH // 2) + 350,
                50,
            ),
        )

        draw_text_center("ПРОФИЛЬ", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, 200, 80)

        # Конфигурация отображения инвентар

        offset_y = 200
        font = pygame.font.Font(v.FONT_PATH2, 25)
        for line in v.user_data:
            user_data_surface = font.render(line, True, v.WHITE)
            v.screen.blit(user_data_surface, (80, offset_y))
            offset_y += 40

        # +=========== INVENTORY ==========+

        item_width = 120  # Ширина прямоугольника
        item_height = 150  # Высота прямоугольника
        row_padding = 20  # Отступ между строками

        # Начало отрисовки предметов

        start_x = item_width * 0.3  # Центрируем по горизонтали
        start_y = 10 + y_scroll  # Начало отрисовки предметов

        inventory_surface = pygame.Surface((750, 400), pygame.SRCALPHA)
        inventory_rect = inventory_surface.get_rect()

        t_res = t.join()
        if t_res and pygame.time.get_ticks() % 1000 < 10:
            packs = t_res
            t = v.ThreadWithReturnValue(target=update_shop)
            t.start()

        if packs:
            can_up = start_y < 0
            can_down = (
                start_y + (((item_height + row_padding)) * (((len(packs)) + 4) // 5))
                >= inventory_rect.h
            )
            for item_idx, item in enumerate(packs):
                row = item_idx // 5

                x = start_x + (item_idx % 5 * (item_width + row_padding))
                y = start_y + (((item_height + row_padding)) * row)

                if y < -item_height:
                    continue
                elif y > inventory_rect.h:
                    break
                item_rect = pygame.Rect(x, y, item_width, item_height)
                # Рисуем прямоугольник
                pygame.draw.rect(
                    inventory_surface,
                    item.get("color", v.GRAY),
                    (x, y, item_width, item_height),
                    border_bottom_left_radius=15,
                    border_bottom_right_radius=15,
                )

                # Отображаем название предмета внутри прямоугольника
                item_surface = font_15.render(item["name"], True, v.WHITE)
                img_surf = None

                # Определяем иконку в зависимости от типа предмета
                match item["type"]:
                    case "sounds":
                        img_surf = v.sounds_pack_icon
                    case "balls patterns":
                        img_surf = v.ballspattern_pack_icon
                    case "loading screen":
                        img_surf = v.loadingscreen_pack_icon
                    case "table pattern":
                        img_surf = v.table_pattern_icon

                if img_surf:
                    inventory_surface.blit(img_surf, (x, y))

                inventory_surface.blit(
                    item_surface,
                    (
                        x + (item_width - item_surface.get_width()) // 2,
                        y + (item_height - item_surface.get_height()) - 5,
                    ),
                )
                cost_text = "COST " + str(item.get("cost", 0))
                cost_color = (255, 153, 0)
                cost_surface = font_10.render(cost_text, True, cost_color)
                inventory_surface.blit(
                    cost_surface,
                    (
                        x + (item_width - cost_surface.get_width()) // 2,
                        y,  # Позиция статуса "скачан"
                    ),
                )

                mouse_pos = list(pygame.mouse.get_pos())
                mouse_pos[0] -= v.WIDTH // 3
                mouse_pos[1] -= 140
                mouse_pos = tuple(mouse_pos)
                if item_rect.collidepoint(mouse_pos):

                    overlay = pygame.Surface((item_width, item_height), pygame.SRCALPHA)
                    pygame.draw.rect(
                        overlay,
                        (0, 0, 0, 200),
                        (0, 0, item_width, item_height),
                        border_bottom_right_radius=15,
                        border_bottom_left_radius=15,
                    )
                    inventory_surface.blit(overlay, (x, y))
                    button_pos = (
                        x + (item_width) // 2 - 20 * len("BUY") // 2,
                        y + (item_height) // 2 - 20,
                    )
                    button_rect = pygame.Rect(button_pos[0], button_pos[1], 30, 20)

                    text = (
                        "BUY"
                        if item not in v.succes_buying_packs
                        and item not in v.failed_buying_packs
                        else "SUCCES" if item in v.succes_buying_packs else "FAILED"
                    )

                    color = (
                        v.RED
                        if item in v.failed_buying_packs
                        else (
                            v.GREEN
                            if item in v.succes_buying_packs
                            else (
                                v.YELLOW
                                if button_rect.collidepoint(mouse_pos)
                                else v.WHITE
                            )
                        )
                    )

                    button = font_15.render(
                        text,
                        True,
                        color,
                    )
                    inventory_surface.blit(button, button_pos)
                    if button_rect.collidepoint(mouse_pos):
                        selected_button = (text, button_rect, item)
            pygame.draw.rect(
                inventory_surface, v.BLACK, (0, 0, 750, 400), 1, border_radius=10
            )
            v.screen.blit(inventory_surface, (v.WIDTH // 3, 140))
        # Добавляем текст на кнопку
        back_button_rect = pygame.Rect(v.WIDTH // 2 - 100, v.HEIGHT - 100, 200, 50)
        pygame.draw.rect(v.screen, v.BLACK, back_button_rect, border_radius=25)
        draw_text_center(
            "Назад",
            pygame.font.Font(v.FONT_PATH, 30),
            v.WHITE,
            back_button_rect.centerx,
            back_button_rect.centery,
        )
        "button"
        inventory_button_rect = pygame.Rect(
            (v.WIDTH // 2) - 50,
            50,
            200,
            50,
        )
        font = pygame.font.Font(v.FONT_PATH, 50)
        color = v.GRAY if v.shop_selected_flag else v.WHITE

        login_surface = font.render("ИНВЕНТАРЬ", True, color)
        v.screen.blit(login_surface, (inventory_button_rect.x, inventory_button_rect.y))

        pygame.display.flip()
        v.CLOCK.tick(v.FPS)

        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Возвращаемся в главное меню по нажатию ESC

            # Обработка клика на кнопку
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if v.shop_selected_flag:
                    f.playsound(v.click_sound)
                    v.shop_selected_flag = False
                    return False
                if back_button_rect.collidepoint(event.pos):
                    f.playsound(v.click_sound)
                    return True
                if not selected_button:
                    continue
                mouse_pos = list(event.pos)
                mouse_pos[0] -= v.WIDTH // 3
                mouse_pos[1] -= 140
                mouse_pos = tuple(mouse_pos)
                # Возвращаемся в главное меню при клике на кнопку
                if selected_button[1].collidepoint(mouse_pos):
                    f.playsound(v.click_sound)
                    if selected_button[0] == "BUY":
                        th = Thread(target=buy_pack, args=(selected_button[2],))
                        th.start()
            elif event.type == pygame.MOUSEWHEEL:
                # Vertical scrolling (standard mouse wheel)
                if event.y != 0:
                    if (event.y < 0 and can_down) or (event.y > 0 and can_up):
                        y_scroll += event.y * 20  # Adjust scroll speed
            elif event.type == pygame.MOUSEMOTION:
                if inventory_button_rect.collidepoint(event.pos):
                    v.shop_selected_flag = True
                else:
                    v.shop_selected_flag = False


def buy_pack(module):
    # Проверяем, есть ли у игрока достаточно денег
    balance = db.db.get_balance(v.username)
    if balance:
        if balance >= module.get("cost", 0):
            balance -= module.get("cost", 0)
            db.db.update_balance(v.username, balance)
            v.succes_buying_packs.append(module)
            inventory = db.db.get_inventory(v.username)
            if module not in inventory:
                inventory.append(module)
            db.db.update_inventory(v.username, inventory)
            time.sleep(50)
            v.succes_buying_packs.remove(module)
            return
    v.failed_buying_packs.append(module)
    time.sleep(0.5)
    v.failed_buying_packs.remove(module)


def download_pack(module):
    v.downloading_packs.append(module)

    s3.s3client.get_pack(module)

    v.downloading_packs.remove(module)


def pause_menu():
    """Меню при нажатии ESC во время игры
    Returns: pick (str)
    """

    selected = 0  # Индекс выбранной кнопки

    options = ["Вернуться в игру", "Вернуться в меню", "Настройки", "Выйти"]

    # Основной цикл
    while True:
        v.screen.fill(v.BLACK_BG)

        # рисуем тайтл
        draw_text_center(
            "ПАУЗА", pygame.font.Font(v.FONT_PATH, 50), v.WHITE, v.WIDTH // 2, 80
        )

        # рисуем кнопки
        for idx, opt in enumerate(options):
            color = v.YELLOW if idx == selected else v.WHITE
            draw_text_center(
                opt,
                pygame.font.Font(v.FONT_PATH2, 36),
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
                    f.playsound(v.click_sound)
                    pick = options[selected]
                    if pick == "Вернуться в игру":
                        return "resume"

                    elif pick == "Вернуться в меню":
                        return "menu"

                    elif pick == "Настройки":
                        settings_menu()

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
    my_score = v.players[0].score
    v.WIN = True
    for player in v.players[1:]:
        if player.score > my_score:
            v.WIN = False
            v.LOSE = True
            break
    if v.MUSIC_ENABLED:
        pygame.mixer.music.load(
            f"{v.to_sounds_path}/end_win.mp3"
            if v.WIN
            else f"{v.to_sounds_path}/end_lose.mp3"
        )
        pygame.mixer.music.play()
    while True:
        v.screen.fill((31, 184, 31) if v.WIN else (184, 31, 0))

        # рисуем тайтл
        draw_text_center(
            "ПОБЕДА" if v.WIN else "ПОРАЖЕНИЕ",
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
                    f.playsound(v.click_sound)
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
        v.screen.fill(v.BLACK_BG)
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
                pygame.draw.rect(v.screen, v.BLACK, button_rect, border_radius=10)
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
                pygame.font.Font(v.FONT_PATH2, 40),
                v.WHITE,
                v.WIDTH // 2,
                v.HEIGHT // 2,
            )

        # Кнопка "Назад"
        back_button_rect = pygame.Rect(v.WIDTH // 2 - 100, v.HEIGHT - 100, 200, 50)
        pygame.draw.rect(v.screen, v.BLACK, back_button_rect, border_radius=25)
        draw_text_center(
            "Назад",
            pygame.font.Font(v.FONT_PATH2, 30),
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


class Chat:
    def draw():

        # Зона истории сообщений
        chat_area = pygame.Rect(
            v.CHAT_X + 10, v.CHAT_Y + 10, v.CHAT_WIDTH - 20, v.CHAT_HEIGHT - 50
        )
        y_offset = chat_area.bottom

        # Рисуем историю сообщений
        font = pygame.font.Font(v.FONT_PATH2, 20)
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
        pygame.draw.rect(v.screen, v.INPUT_COLOR, v.chat_input_area, border_radius=10)
        pygame.draw.rect(
            v.screen, v.CHAT_BORDER_COLOR, v.chat_input_area, 2, border_radius=10
        )

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
                f.playsound(v.click_sound)
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


class Leaderboard:
    def __init__(self):
        self.image = pygame.Surface((700, 500), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()

    def draw(self, screen, pos):
        pygame.draw.rect(
            self.image, (65, 65, 65, 250), (0, 0, 700, 500), border_radius=30
        )
        pygame.draw.rect(
            self.image, (30, 30, 30, 250), (0, 0, 700, 500), 10, border_radius=30
        )
        font = pygame.font.Font(v.FONT_PATH, 40)
        leaderboard_surface = font.render("LEADERBOARD", False, (255, 255, 255))
        self.image.blit(leaderboard_surface, (200, 42))
        users = sorted(v.db.db.get_global_rating(), key=lambda x: x[1])
        x_top_static = 52
        x_name_static = 152
        x_rating_static = 452
        y = 100
        i = 1
        font = pygame.font.Font(v.FONT_PATH, 25)
        user_colors = {1: (255, 220, 30), 2: (227, 227, 227), 3: (160, 50, 0)}

        top_surface = font.render("TOP", False, (100, 100, 100))
        nickname_surface = font.render("NICKNAME", False, (100, 100, 100))
        rating_surface = font.render("RATING", False, (100, 100, 100))

        self.image.blit(top_surface, (x_top_static, y))
        self.image.blit(nickname_surface, (x_name_static, y))
        self.image.blit(rating_surface, (x_rating_static, y))

        y += 50
        font = pygame.font.Font(v.FONT_PATH2, 20)
        if v.AUTHED:
            for j, data in enumerate(users):
                if data[0] == v.username:
                    client_top = j

        for username, rating in users:

            if len(username) > 20:
                username = username[:17] + "..."

            if v.AUTHED:
                if i == client_top + 1:
                    pygame.draw.rect(
                        self.image, (170, 170, 170), (10, y + 3, 680, 20), 1
                    )

            user_color = user_colors.get(i, (160, 160, 160))
            top_surface = font.render(str(i), False, user_color)
            nickname_surface = font.render(str(username), False, user_color)
            rating_surface = font.render(str(rating), False, user_color)
            self.image.blit(top_surface, (x_top_static, y))
            self.image.blit(nickname_surface, (x_name_static, y))
            self.image.blit(rating_surface, (x_rating_static, y))
            y += 20
            i += 1
            if y >= 400:
                if v.AUTHED:
                    if i < client_top + 1:
                        if i != client_top + 2:
                            y += 10
                        pygame.draw.rect(
                            self.image, (170, 170, 170), (10, y, 680, 20), 1
                        )
                        username = (
                            v.username
                            if len(v.username) <= 20
                            else v.username[:17] + "..."
                        )
                        user_color = (160, 160, 160)
                        top_surface = font.render(
                            str(client_top + 1), False, user_color
                        )
                        nickname_surface = font.render(str(username), False, user_color)
                        rating_surface = font.render(str(rating), False, user_color)
                        self.image.blit(top_surface, (x_top_static, y))
                        self.image.blit(nickname_surface, (x_name_static, y))
                        self.image.blit(rating_surface, (x_rating_static, y))

                break
        screen.blit(self.image, pos)
