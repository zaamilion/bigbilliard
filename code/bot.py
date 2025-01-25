import math
from ai import *

def bot_take_turn(all_balls_stopped, balls, WHITE, white_ball, table_width, table_height):
    if not all_balls_stopped():
        return  # Бот ждет, пока шары остановятся

    target_ball = None
    min_distance = float("inf")

    # Находим ближайший шар к белому шару
    for ball in balls:
        if ball.color != WHITE:  # Исключаем белый шар
            distance = math.hypot(white_ball.rect.centerx - ball.rect.centerx,
                                  white_ball.rect.centery - ball.rect.centery)
            if distance < min_distance:
                min_distance = distance
                target_ball = ball

    if target_ball is not None:
        # Используем нейросеть для предсказания угла и силы
        angle, force = predict_shot(white_ball, target_ball, table_width, table_height)

        # Применяем удар
    
        white_ball.vx += math.cos(angle) * force
        white_ball.vy += math.sin(angle) * force
        white_x = white_ball.rect.centerx / table_width
        white_y = white_ball.rect.centery / table_height
        target_x = target_ball.rect.centerx / table_width
        target_y = target_ball.rect.centery / table_height

    # Дообучаем модель после хода
    return (white_x, white_y, target_x, target_y, angle, force)


def check_white_ball_collision(white_ball, balls):
    """
    Проверяет, задел ли белый шар другие шары.

    Args:
        white_ball: объект белого шара (Sprite).
        balls: список всех шаров (Sprite Group), включая белый шар.

    Returns:
        bool: True, если белый шар задел другие шары, иначе False.
    """
    for ball in balls:
        if ball == white_ball:  # Пропускаем сам белый шар
            continue

        # Вычисляем расстояние между центрами шаров
        distance = math.hypot(
            white_ball.rect.centerx - ball.rect.centerx,
            white_ball.rect.centery - ball.rect.centery
        )

        # Если расстояние меньше суммы радиусов, шары столкнулись
        if distance <= (white_ball.radius + ball.radius):
            return True  # Столкновение обнаружено

    return False  # Нет столкновений