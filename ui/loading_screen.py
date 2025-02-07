import pygame
from PIL import Image
import os
import sys
import game.variables as v


def load_image(name, colorkey=None):
    # если файл не существует, то выходим
    if not os.path.isfile(name):
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()
    image = pygame.image.load(name)
    return image


def main():

    all_sprites = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite(all_sprites)
    sprite.image = pygame.transform.scale(
        load_image(v.LOADING_SCREEN_IMAGE), (v.WIDTH, v.HEIGHT)
    )
    # и размеры
    sprite.rect = sprite.image.get_rect()

    sprite.rect.x = 0
    sprite.rect.y = 0

    x_off = 600
    y_off = 500
    i = 1
    size = 5
    run = True
    if v.MUSIC_ENABLED:
        pygame.mixer.music.load(f"{v.to_sounds_path}/loading.mp3")
        pygame.mixer.music.play()
    color = [
        col - 50 if col >= 50 else 0
        for col in list(sprite.image.get_at((x_off, y_off)))
    ]
    while run:
        v.CLOCK.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        v.screen.fill(0)

        all_sprites.draw(v.screen)

        if i <= 45:
            pygame.draw.rect(
                v.screen, color, (x_off, y_off, size * i, 50), border_radius=5
            )
        else:
            pygame.draw.rect(
                v.screen, color, (x_off, y_off, size * 45, 50), border_radius=5
            )
        pygame.display.flip()
        i += 1
        if i == 60:
            return
