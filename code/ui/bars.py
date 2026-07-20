from ui_elements import *
from sliders import *


class ScrollBar(UIElement):
    def __init__(self, groups, size, pos, sub_surfs, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.sub_surfs = sub_surfs
        self.image = self.create_image(size)
        self.rect = self.image.get_frect(center=pos)
        self.displacement_proportion = 0
        self.can_move = True

        # slider
        slider_image = pygame.image.load('graphics/ui/slider.png').convert_alpha()
        self.slider = ScrollBarSlider(groups, slider_image, self.rect.midtop, 1, self.rect.height - 6)

    def create_image(self, size):
        sub_surf_width = self.sub_surfs[0].get_width()
        sub_surf_height = self.sub_surfs[0].get_height()

        scroll_bar_width = size[0] // sub_surf_width

        surf = pygame.Surface(size, pygame.SRCALPHA)
        secondary_surf = pygame.Surface((size[0] - 6, size[1] - 6), pygame.SRCALPHA)
        surf.fill(self.sub_surfs[0].get_at((0, 0)))
        secondary_surf.fill(self.sub_surfs[0].get_at((4, 4)))
        surf.blit(secondary_surf, (3, 3))

        surf.blit(self.sub_surfs[0], (0, 0))
        surf.blit(self.sub_surfs[2], (sub_surf_width * (scroll_bar_width - 1), 0))
        surf.blit(self.sub_surfs[6], (0, surf.height - sub_surf_height))
        surf.blit(self.sub_surfs[8], (sub_surf_width * (scroll_bar_width - 1), surf.height - sub_surf_height))

        return surf

    def set_can_move(self, state):
        self.can_move = state
        self.slider.can_move = state

        self.image.set_alpha(255 if self.can_move else 0)
        self.slider.image.set_alpha(255 if self.can_move else 0)

    def check_state(self):
        self.image.set_alpha(255 if self.can_move else 0)

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        self.displacement_proportion = self.slider.displacement_proportion

        # methods
        self.check_state()


class ReloadBar(UIElement):
    def __init__(self, groups, size, pos, reload_time, text, play_animation=True):
        # setup
        image = pygame.surface.Surface(size, pygame.SRCALPHA)
        super().__init__(groups, pos, play_animation=play_animation)
        self.image = image
        self.rect = self.image.get_frect(center=pos)

        # reloading
        self.max_length = size[0]
        self.height = size[1]
        self.reload_time = reload_time
        self.reload_start_time = 0
        self.empty = False

        self.text = FONT.render(text, True, (250, 250, 250))
        self.text_rect = self.text.get_frect(midleft=(10, self.rect.height / 2))

    def display_reload(self):
        if not self.empty:
            if pygame.time.get_ticks() - self.reload_start_time < self.reload_time:
                colour = (255, 105, 97)
            else:
                colour = (90, 220, 90)
        else:
            colour = (100, 100, 100)

        length = self.max_length * (min(pygame.time.get_ticks() - self.reload_start_time, self.reload_time) / self.reload_time)
        self.image.fill((100, 100, 100))
        pygame.draw.rect(self.image, colour, (0, 0, length, self.height))

        self.image.blit(self.text, self.text_rect)

    def start_reload(self):
        self.reload_start_time = pygame.time.get_ticks()
        self.image.fill((0, 0, 0, 0))

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()


class HealthBar(UIElement):
    def __init__(self, groups, size, pos, player, play_animation=True):
        # setup
        image = pygame.surface.Surface(size, pygame.SRCALPHA)
        super().__init__(groups, pos, play_animation=play_animation)
        self.image = image
        self.rect = self.image.get_frect(center=pos)

        # bar
        self.player = player
        self.max_health = player.max_health

        self.max_length = size[0]
        self.height = size[1]

        self.text = FONT.render('text', True, (250, 250, 250))
        self.text_rect = self.text.get_frect(midleft=(10, self.rect.height / 2))

    def display_health(self):
        length = self.max_length * (self.player.health / self.max_health)
        self.image.fill((100, 100, 100))
        pygame.draw.rect(self.image, (255, 105, 97), (0, 0, length, self.height))

    def update(self, dt):
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()


class CountBar(UIElement):
    def __init__(self, groups, image, pos, label, colour, initial_count, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=pos)

        # count
        self.text = None
        self.colour = colour

        self.label = label
        self.count = initial_count

        self.set_count(self.count)

    def set_count(self, amount):
        self.count = amount

        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=self.rect.center)
        self.text = FONT.render(f'{self.label}: {self.count}' if self.label else f'{self.count}', True, self.colour)
        text_rect = self.text.get_frect(midleft=(50, self.image.height/2+1))
        self.image.blit(self.text, text_rect)

    def update(self, dt):
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()


class FishingBar(UIElement):
    def __init__(self, groups, image, pos, fish, play_animation=True):
        super().__init__(groups, pos, play_animation=play_animation)
        # setup
        self.image = image
        self.rect = self.image.get_frect(center=pos)
        self.fish = fish

        # flags
        self.fish_caught = None

        # image
        self.green_width = (self.rect.width*0.5)
        self.create_image()

        # slider
        slider_image = pygame.image.load('graphics/items/fishing_bob.png').convert_alpha()
        self.slider = FishingBarSlider(groups, slider_image, self.rect.center, 0, self.fish, self.rect.width // 2 - 12,
                                       play_animation=play_animation)
        self.slider_direction_change_timer = Timer(200)

        # catching stats
        self.start_time = None
        self.time_to_spend_in_green = 100#4000 * (RARITY_LOOKUP[self.fish.rarity] ** 0.5)
        self.time_spent_in_green = 0
        self.time_can_spend_in_red = 500
        self.time_spent_in_red = 0

    def check_start_reeling(self):
        if not self.init_animation_playing and not self.start_time:
            self.slider.can_move = True
            self.start_time = pygame.time.get_ticks()
            audio_manager.play('reeling')

    def check_time_spent_in_colours(self):
        # update_times
        if abs(self.slider.rect.centerx - self.rect.centerx) < self.green_width / 2:
            self.time_spent_in_green = pygame.time.get_ticks() - self.start_time
        else:
            self.time_spent_in_red = pygame.time.get_ticks() - self.start_time

        # check times
        if self.time_spent_in_green >= self.time_to_spend_in_green:
            self.fish_caught = True
            audio_manager.stop('reeling')
        elif self.time_spent_in_red >= self.time_can_spend_in_red:
            self.fish_caught = False
            audio_manager.stop('reeling')

    def create_image(self):
        new_image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        red_surf = pygame.Surface((self.rect.width-4, self.rect.height-4), pygame.SRCALPHA)
        red_surf.fill(TEXT_BOX_RED)
        red_rect = red_surf.get_frect(center=(self.image.width//2, self.image.height//2))

        green_surf = pygame.Surface((self.green_width, self.rect.height-4), pygame.SRCALPHA)
        green_surf.fill((90, 220, 90))
        green_rect = green_surf.get_frect(center=(self.rect.width//2, self.rect.height//2))


        new_image.blit(red_surf, red_rect)
        new_image.blit(green_surf, green_rect)
        new_image.blit(self.image, (0, 0))

        self.image = new_image

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and self.slider_direction_change_timer.finished:
            self.slider.velocity *= -1
            self.slider_direction_change_timer.start()

    def delete(self):
        if self.play_animation and not self.delete_animation_playing:
            self.delete_animation_playing = True
            self.animation_start_time = pygame.time.get_ticks()
            self.slider.delete()
        elif not self.play_animation:
            self.slider.kill()
            self.kill()

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # movement
        if self.start_time:
            self.slider_direction_change_timer.update()
            self.check_time_spent_in_colours()
            self.get_input()
        else:
            self.check_start_reeling()