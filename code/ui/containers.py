from ui_elements import *


class ScrollBox(UIElement):
    def __init__(self, groups, pos, size, sprites, scroll_bar, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.original_image = pygame.Surface(size, pygame.SRCALPHA)
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(topleft=pos)

        # scroll elements
        self.sprites = sprites
        self.scroll_bar = scroll_bar
        self.sprite_positions = self.create_sprite_positions((3, 3))
        self.set_sprite_pos()

        # animation
        self.init_target_y = pos[1] + self.rect.height // 2
        self.delete_target_y = pos[1] + WINDOW_HEIGHT + self.rect.height // 2

    def set_play_animation(self, state):
        self.play_animation = state

        for sprite in self.sprites:
            sprite.play_animation = state

    def create_sprite_positions(self, start_pos):
        positions = []

        if self.sprites:
            sprite_height = self.sprites.sprites()[0].image.height
            sprite_width = self.sprites.sprites()[0].image.width

            no_of_cols = self.image.width // (sprite_width + 20)
            col_spacing = self.image.width / no_of_cols
            col_x = [x * col_spacing for x in range(no_of_cols)]

            for i in range(len(self.sprites)):
                x_pos = start_pos[0] + int(col_x[i % no_of_cols]) + (sprite_width // 2)
                y_pos = start_pos[1] + int((sprite_height + 20) * (i // no_of_cols)) + (sprite_height // 2)
                positions.append((x_pos, y_pos))

        return positions

    def set_sprite_pos(self):
        for index, sprite in enumerate(self.sprites):
            sprite.set_play_animation(self.play_animation)
            sprite.animation_type = 'fade'
            sprite.set_init_pos(self.sprite_positions[index])

        if self.sprites:
            if self.sprite_positions[-1][1] + self.sprites.sprites()[0].rect.height // 2 <= self.rect.height:
                self.scroll_bar.set_can_move(False)
        else:
            self.scroll_bar.set_can_move(False)

    def scroll_sprites(self):
        if not (self.delete_animation_playing or self.init_animation_playing) and self.sprites:
            displacement_amount = (self.scroll_bar.displacement_proportion *
                                   (self.sprite_positions[-1][1]+self.sprites.sprites()[0].image.height//2-self.rect.height))

            if displacement_amount > 0:
                for sprite in self.sprites:
                    sprite.rect.centery = sprite.init_target_y - displacement_amount

    def draw(self, surface):
        self.image = self.original_image.copy()

        for sprite in self.sprites:
            self.image.blit(sprite.image, sprite.rect)

        surface.blit(self.image, self.rect)

    def delete(self):
        for sprite in self.sprites:
            sprite.delete()

        if self.play_animation and not self.delete_animation_playing:
            self.init_animation_playing = False
            self.delete_animation_playing = True
            self.animation_start_time = pygame.time.get_ticks()
        elif not self.play_animation:
            self.kill()

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.sprites.update(dt)
        self.scroll_sprites()