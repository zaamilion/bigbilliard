---

# BigBilliard

> BigBilliard - многопользовательская игра с развитой архитектурой и дополнительными сервисами.
> Цель проекта - улучшить игровой опыт, используя различные технологии, применяемые в реальных условиях.


---

## 📋 Содержание
1. [Архитектура проекта](#архитектура-проекта)
2. [Установка и запуск](#установка-и-запуск)
3. [Используемые технологии](#используемые-технологии)
4. [Контакты](#контакты)
---

## 🏗️ Архитектура проекта

### Диаграмма архитектуры
![Архитектура проекта](https://github.com/zaamilion/bigbilliard/docs/Untitled%20Diagram-Components.drawio.png)

---

## ⚙️ Установка и запуск

### Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/zaamilion/bigbilliard.git
   cd bigbilliard
   ```
2. Соберите образ Docker:
   ```bash
   docker build -t bigbilliard .
   ```
3. Запустите:
   ```bash
   docker run -it bigbilliard 
   ```
#### Важно: для запуска у вас должны быть установлены vcxsrv и pulseaudio (для windows)
#### Также код можно запустить без сборки Docker контейнера
1. Установите зависимости:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Запустите :
   ```bash
   python main.py
   ```
---

## 🛠️ Используемые технологии

- **Python**: Основной язык программирования.
- **Socket**: Мультиплеер.
- **TensorFlow**: Ai бот в локальном режиме.
- **PostgreSQL**: хранение БД пользователей.
- **Docker**: Развертывание БД, сборка игры.
- **S3 (boto3)**: Хранение и работа с дополнениями к игре.
- **Threading**: Многопоточная загрузка данных.
- **Pygame**: Для создания графического интерфейса и обработки событий.
- **Tkinter**: Окна авторизации.
- **json**: Хранение локальных данных.
- **Git**: Систематизация версий
- **Markdown**: Для документации.

---

---

## 📧 Контакты

Артём - [@zaamilion](https://github.com/zaamilion) - tg [@zaamilion](https://t.me/zaamilion)



