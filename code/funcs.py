import variables as v
import math


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
                    if v.IS_SERVER:
                        v.chat.append(
                            (
                                "Server",
                                f"Игрок {v.players[previous_player].name} забил шар! +{v.BALL_AWARD} очко",
                            )
                        )
                    v.players[previous_player].score += v.BALL_AWARD
                    ball.kill()  # Убираем шар с поля
