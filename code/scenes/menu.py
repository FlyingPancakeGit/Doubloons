from scenes.match import *


class Menu:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.running = True
        self.clock = pygame.time.Clock()

        # groups
        self.menu_sprites = pygame.sprite.Group()
        self.button_sprites = pygame.sprite.Group()

        # background
        background_image = pygame.image.load('graphics/ui/backgrounds/menu_background.png').convert_alpha()
        self.background = Image((self.menu_sprites), background_image, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        self.loading_image = pygame.image.load('graphics/ui/backgrounds/loading_background.png').convert_alpha()
        loading_text = FONT.render('loading...', True, (255, 255, 255))
        loading_rect = loading_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.loading_image.blit(loading_text, loading_rect)

        # buttons
        self.button_image = pygame.image.load('graphics/ui/buttons/button.png').convert_alpha()

        self.create_buttons()

    def create_buttons(self):
        margin_x = self.button_image.width / 2 + 26 # to align with left side of title


        TextButton((self.menu_sprites, self.button_sprites), self.button_image,
                   (margin_x, WINDOW_HEIGHT * 0.25), 'Play', play_animation=False)

    def check_buttons_pressed(self):
        for button in self.button_sprites:
            if button.pressed:
                self.display_surface.blit(self.loading_image, (0, 0))
                pygame.display.update()
                Match().match_loop()

    def menu_loop(self):
        while self.running:
            dt = self.clock.tick() / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update
            self.menu_sprites.update(dt)

            self.check_buttons_pressed()

            # draw
            self.menu_sprites.draw(self.display_surface)

            pygame.display.update()