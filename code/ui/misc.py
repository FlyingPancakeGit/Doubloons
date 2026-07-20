from ui_elements import *


class Image(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        # setup
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.hit_box_rect = self.rect


class NumberDisplay(UIElement):
    def __init__(self, groups, image, pos, min_num, max_num, num, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=pos)

        # number
        self.num = num
        self.min_num = min_num
        self.max_num = max_num

        self.update_image()

    def update_image(self):
        image = self.original_image.copy()

        num_text = FONT.render(f'{self.num}', True, TEXT_BOX_BLACK)
        num_rect = num_text.get_frect(center=(image.width // 2, image.height // 2))
        image.blit(num_text, num_rect)

        self.image = image

    def update_range(self, min_num, max_num):
        self.min_num = min_num
        self.max_num = max_num

        self.num = max(min(self.num, self.max_num), self.min_num)

    def add_to_num(self, change):
        proposed_change = self.num + change

        if self.min_num <= proposed_change <= self.max_num:
            self.num = proposed_change

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.update_image()


class Compass(UIElement):
    def __init__(self, groups, image, pos, main_island_pos, player_ship, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.image = image
        self.rect = self.image.get_frect(center=pos)

        # calculation data
        self.main_island_pos = main_island_pos
        self.player_ship = player_ship

        # needle
        self.needle_vector = pygame.math.Vector2()

    def get_needle_vector(self):
        displacement = (pygame.math.Vector2(self.main_island_pos) - pygame.math.Vector2(self.player_ship.rect.center))
        needle_vector = 50 * displacement.normalize() if displacement else displacement

        return needle_vector

    def draw_needle(self):
        start_pos = pygame.math.Vector2(self.rect.center)
        pygame.draw.line(pygame.display.get_surface(), (255, 10, 10), start_pos, start_pos+self.needle_vector, width=3)

    def update(self, dt):
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        self.needle_vector = self.get_needle_vector()