from settings import *
from formulas import *


class PortZone(pygame.sprite.Sprite):
    def __init__(self, groups, pos, island_name):
        # setup
        super().__init__(groups)
        self.image = pygame.Surface((400, 400), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255, 128), (200, 200), 200)
        self.rect = self.image.get_rect(center=pos)
        self.name = island_name

    def update(self, dt):
        pass

class FishingZone(pygame.sprite.Sprite):
    def __init__(self, groups, ship, play_animation=True):
        # setup
        super().__init__(groups)
        self.original_image = pygame.Surface((400, 400), pygame.SRCALPHA)
        self.image = self.original_image.copy()
        pygame.draw.circle(self.image, (0, 255, 0, 0), (200, 200), 200)
        self.rect = self.image.get_rect(center=ship.rect.center)
        self.ship = ship

        # animation
        self.play_animation = play_animation
        self.init_animation_playing = True
        self.delete_animation_playing = False
        self.animation_time = 500
        self.animation_start_time = pygame.time.get_ticks()

    def play_init_animation(self):
        animation_time_elapsed = pygame.time.get_ticks() - self.animation_start_time

        if animation_time_elapsed > self.animation_time:
            alpha = 128
            self.init_animation_playing = False
        else:
            alpha = 128 * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)

        self.image = self.original_image.copy()
        pygame.draw.circle(self.image, (0, 255, 0, alpha), (200, 200), 200)
        self.rect = self.image.get_rect(center=self.ship.rect.center)

    def play_delete_animation(self):
        animation_time_elapsed = pygame.time.get_ticks() - self.animation_start_time

        if animation_time_elapsed > self.animation_time:
            alpha = 0
            self.kill()
        else:
            alpha = 128 * (1 - ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time))

        self.image = self.original_image.copy()
        pygame.draw.circle(self.image, (0, 255, 0, alpha), (200, 200), 200)
        self.rect = self.image.get_rect(center=self.ship.rect.center)

    def delete(self):
        if self.play_animation and not self.delete_animation_playing:
            self.delete_animation_playing = True
            self.animation_start_time = pygame.time.get_ticks()
        elif not self.play_animation:
            self.kill()

    def update(self, dt):
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        self.rect.center = self.ship.rect.center