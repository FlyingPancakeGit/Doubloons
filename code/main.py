from scenes.menu import *


class Main:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        pygame.display.set_caption('Doubloons')
        pygame.display.set_icon(pygame.image.load('graphics/ui/icon.png').convert_alpha())

    def quit(self):
        pygame.quit()

    def main_loop(self):
        Menu().menu_loop()
        self.quit()


if __name__ == "__main__":
    main = Main()
    main.main_loop()