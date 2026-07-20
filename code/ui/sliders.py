from ui_elements import *


class Slider(UIElement):
    def __init__(self, groups, image, pos, axis, range, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.image = image
        self.rect = self.image.get_frect(center=pos)
        self.range = range
        self.axis = axis

        # movement
        self.can_move = False
        self.min_pos = pos[axis]
        self.max_pos = pos[axis] + range

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()


class FishingBarSlider(Slider):
    def __init__(self, groups, image, pos, axis, fish, range, play_animation=True):
        # setup
        super().__init__(groups, image, pos, axis, range, play_animation=play_animation)
        self.fish = fish

        # movement
        self.min_pos = pos[axis] - range // 2
        self.max_pos = pos[axis] + range // 2

        self.velocity = 250 * RARITY_LOOKUP[self.fish.rarity]

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        self.rect.centerx = min(max(self.rect.centerx + self.velocity * dt, self.min_pos), self.max_pos) if self.can_move else self.rect.centerx


class ScrollBarSlider(Slider):
    def __init__(self, groups, image, pos, axis, range, play_animation=True):
        # setup
        super().__init__(groups, image, pos, axis, range, play_animation=play_animation)
        self.original_image = image.copy()
        self.pressed = False
        self.can_move = True

        self.displacement_proportion = 0

    def check_pressed(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        if not self.pressed:
            if self.rect.collidepoint(mouse_pos) and mouse_down:
                self.pressed = True
        elif not mouse_down:
            self.pressed = False

    def rotate(self):
        if self.can_move:
            alpha = self.image.get_alpha()
            self.original_image.set_alpha(alpha)
        else:
            self.original_image.set_alpha(0)

        self.displacement_proportion = (self.rect.centery - self.min_pos) / (self.max_pos - self.min_pos)
        self.image = pygame.transform.rotate(self.original_image, 360 * self.displacement_proportion)
        self.rect = self.image.get_frect(center=self.rect.center)

    def move(self, pos):
        if self.pressed and self.can_move:
            self.rect.centery = min(max(self.min_pos, pos), self.max_pos)
            self.set_init_pos(self.rect.center)

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        self.check_pressed()
        self.move(pygame.mouse.get_pos()[self.axis])
        self.rotate()