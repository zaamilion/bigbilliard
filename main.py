import pygame
import sys

pygame.init()
pygame.mixer.init()

import ui.loading_screen as loading_screen
from game.client import main


if __name__ == "__main__":
    loading_screen.main()
    main()
