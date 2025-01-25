import variables as v
import math
import pygame


# =========== КЛАСС СТАТИСТИКИ ==========
class Statistics:
    def __init__(self):
        self.total_shots = 0


# =========== КЛАСС ДОСТИЖЕНИЙ ==========
class Achievements:
    def __init__(self):
        self.achievements_unlocked = []

    def unlock(self, name: str) -> None:
        if name not in self.achievements_unlocked:
            self.achievements_unlocked.append(name)


# =========== КЛАСС ЛУНКИ ==========
class Pocket(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, radius: int = v.POCKET_RADIUS):
        # Инициализируем спрайт
        super().__init__(v.all_sprites, v.pockets)
        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, v.BLACK, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))


# =========== КЛАСС ШАРА ==========
class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        color: pygame.Color,
        x: int,
        y: int,
        number: int = None,
        radius: int = v.BALL_RADIUS,
    ):
        # Инициализируем спрайт
        super().__init__(v.all_sprites, v.balls)
        self.color = color
        self.radius = radius
        self.number = number
        self.mass = 1
        self.spin_x = 0.0
        self.spin_y = 0.0

        self.image = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)

        # Рисуем номер шара
        if self.number is not None:
            font_small = pygame.font.SysFont(None, 24)
            text_surf = font_small.render(str(self.number), True, v.WHITE)
            text_rect = text_surf.get_rect(center=(radius, radius))
            self.image.blit(text_surf, text_rect)

        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 0
        self.vy = 0

    def update(self):
        # Трение
        self.vx *= v.FRICTION
        self.vy *= v.FRICTION

        # Винт
        if v.ENABLE_SPIN:
            self.vx += self.spin_x * v.SPIN_FACTOR
            self.vy += self.spin_y * v.SPIN_FACTOR
            self.spin_x *= 0.99
            self.spin_y *= 0.99

        # Обновляем позицию
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Отскок от стен
        if self.rect.left < v.TABLE_RECT.left:
            self.rect.left = v.TABLE_RECT.left
            self.vx = -self.vx
        if self.rect.right > v.TABLE_RECT.right:
            self.rect.right = v.TABLE_RECT.right
            self.vx = -self.vx
        if self.rect.top < v.TABLE_RECT.top:
            self.rect.top = v.TABLE_RECT.top
            self.vy = -self.vy
        if self.rect.bottom > v.TABLE_RECT.bottom:
            self.rect.bottom = v.TABLE_RECT.bottom
            self.vy = -self.vy

        # Столкновения с другими шарами
        collided = pygame.sprite.spritecollide(self, v.balls, False)
        for b in collided:
            if b != self:
                self.resolve_collision(b)

    def resolve_collision(self, other: "Ball"):

        # считаем дистанцию
        dx = other.rect.centerx - self.rect.centerx
        dy = other.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        # нормализуем вектор
        if dist < self.radius + other.radius:
            angle = math.atan2(dy, dx)
            total_mass = self.mass + other.mass

            v1 = self.vx * math.cos(angle) + self.vy * math.sin(angle)
            v2 = other.vx * math.cos(angle) + other.vy * math.sin(angle)

            u1 = (v1 * (self.mass - other.mass) + 2 * other.mass * v2) / total_mass
            u2 = (v2 * (other.mass - self.mass) + 2 * self.mass * v1) / total_mass

            p1 = self.vx * (-math.sin(angle)) + self.vy * math.cos(angle)
            p2 = other.vx * (-math.sin(angle)) + other.vy * math.cos(angle)

            self.vx = u1 * math.cos(angle) - p1 * math.sin(angle)
            self.vy = u1 * math.sin(angle) + p1 * math.cos(angle)
            other.vx = u2 * math.cos(angle) - p2 * math.sin(angle)
            other.vy = u2 * math.sin(angle) + p2 * math.cos(angle)

            overlap = (self.radius + other.radius - dist) / 2
            self.rect.x -= overlap * math.cos(angle)
            self.rect.y -= overlap * math.sin(angle)
            other.rect.x += overlap * math.cos(angle)
            other.rect.y += overlap * math.sin(angle)


# =========== КЛАСС ИГРОКА ==========
class Player:
    def __init__(
        self, name: str, index: int = 0, ip: list = ["0.0.0.0", 0], bot: bool = False
    ):
        self.ip = ip
        self.index = index
        self.name = name
        self.score = 0
        self.stats = Statistics()
        self.ach = Achievements()
        self.bot = bot


# =========== КЛАСС КИЙ ==========
class Cue:
    def __init__(self, player: "Player"):
        self.player = player
        self.active = False
        self.angle = 0
        self.max_force = 20
        self.current_force = 0
        self.force_increasing = True
        self.force_window_active = False
        self.spin_x = 0.0
        self.spin_y = 0.0

    def initiate_force_window(self):
        # включаем "окно силы"
        self.active = True
        self.force_window_active = True
        self.current_force = 0
        self.force_increasing = True

    def update_force(self, dt: float):
        # обновляем силу
        if self.force_window_active:
            speed = 0.07
            if self.force_increasing:
                self.current_force += dt * speed
                if self.current_force >= self.max_force:
                    self.force_increasing = False
            else:
                self.current_force -= dt * speed
                if self.current_force <= 0:
                    self.force_increasing = True
            self.current_force = max(0, min(self.current_force, self.max_force))

    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        mx, my = pygame.mouse.get_pos()
        dx = v.white_ball.rect.centerx - mx
        dy = v.white_ball.rect.centery - my
        self.angle = math.atan2(dy, dx)

        # Пунктирная линия
        cue_length = 200
        dash_len = 10
        gap_len = 5
        total_len = cue_length
        n_dashes = int(total_len / (dash_len + gap_len))

        sx = v.white_ball.rect.centerx
        sy = v.white_ball.rect.centery

        for i in range(n_dashes):
            dsx = sx + math.cos(self.angle) * (i * (dash_len + gap_len))
            dsy = sy + math.sin(self.angle) * (i * (dash_len + gap_len))
            dex = dsx + math.cos(self.angle) * dash_len
            dey = dsy + math.sin(self.angle) * dash_len
            pygame.draw.line(screen, v.RED, (dsx, dsy), (dex, dey), 2)

        # Окно силы
        if self.force_window_active:
            pygame.draw.rect(
                screen, v.DARK_GRAY, (v.WIDTH // 2 - 100, v.HEIGHT - 60, 200, 30), 2
            )
            fw = (self.current_force / self.max_force) * 200
            pygame.draw.rect(screen, v.RED, (v.WIDTH // 2 - 100, v.HEIGHT - 60, fw, 30))

        # Обучающий режим (линия предсказания)
        if v.ENABLE_HINTS:
            pred_len = 400
            px, py = sx, sy
            px2 = px + math.cos(self.angle) * pred_len
            py2 = py + math.sin(self.angle) * pred_len
            pygame.draw.line(screen, v.YELLOW, (px, py), (px2, py2), 1)

    def shoot(self):
        # Бьем по шару
        if self.current_force > 0:
            mx, my = pygame.mouse.get_pos()
            dx = v.white_ball.rect.centerx - mx
            dy = v.white_ball.rect.centery - my
            angle = math.atan2(dy, dx)
            v.white_ball.vx += math.cos(angle) * self.current_force
            v.white_ball.vy += math.sin(angle) * self.current_force

            if v.ENABLE_SPIN:
                v.white_ball.spin_x = self.spin_x
                v.white_ball.spin_y = self.spin_y

        self.current_force = 0
        self.force_window_active = False
        self.active = False
