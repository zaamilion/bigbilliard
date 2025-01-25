import numpy as np
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf

# Инициируем модель
model = tf.keras.models.load_model("./data/bot_model.h5", compile=False)
model.compile(optimizer="adam", loss="mse")

# Переменные для обучения
training_data = []
training_labels = []


def predict_shot(white_ball, target_ball, table_width, table_height):
    """
    Использует нейросеть для предсказания угла и силы удара и добавляет успешные удары в тренировочный набор.

    Args:
        white_ball: объект белого шара (Sprite).
        target_ball: объект целевого шара (Sprite).
        table_width: ширина стола.
        table_height: высота стола.

    Returns:
        angle (float): угол удара в радианах.
        force (float): сила удара.
    """
    # Нормализация данных
    white_x = white_ball.rect.centerx / table_width
    white_y = white_ball.rect.centery / table_height
    target_x = target_ball.rect.centerx / table_width
    target_y = target_ball.rect.centery / table_height

    # Подготовка данных для модели
    input_data = np.array([[white_x, white_y, target_x, target_y]], dtype=np.float32)

    # Предсказание
    angle, force = model.predict(input_data)[0]
    return angle, force


def retrain_model(white_x, white_y, target_x, target_y, angle, force):
    """
    Дообучает модель на собранных данных.
    """

    training_data.append([white_x, white_y, target_x, target_y])
    training_labels.append([angle, force])

    if len(training_data) > 0:
        x = np.array(training_data, dtype=np.float32)
        y = np.array(training_labels, dtype=np.float32)

        # Дообучение модели
        print(f"Начало дообучения на {len(x)} образцах...")
        model.fit(x, y, epochs=5, verbose=1)

        # Очищаем данные после обучения
        training_data.clear()
        training_labels.clear()

        # Сохранение модели
        model.save("bot_model.h5")
        print("Модель сохранена.")
