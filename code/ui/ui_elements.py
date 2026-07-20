from ..settings import *
from ..audio_manager import audio_manager


class UIElement(pygame.sprite.Sprite):
    def __init__(self, groups, pos, play_animation=True, animation_type='slide'):
        # setup
        super().__init__(groups)

        # animation
        self.play_animation = play_animation
        self.animation_type = animation_type
        self.init_animation_playing = self.play_animation
        self.delete_animation_playing = False
        self.init_target_y = pos[1]
        self.delete_target_y = pos[1] + WINDOW_HEIGHT
        self.animation_dist = self.delete_target_y - self.init_target_y
        self.animation_time = 500
        self.animation_start_time = pygame.time.get_ticks()

    def set_play_animation(self, state):
        self.play_animation = state

        self.init_animation_playing = False if not state else self.init_animation_playing

    def set_init_pos(self, pos):
        self.rect.center = pos
        self.init_target_y = pos[1]
        self.delete_target_y = pos[1] + WINDOW_HEIGHT
        self.animation_dist = self.delete_target_y - self.init_target_y

    def delete(self):
        if self.play_animation and not self.delete_animation_playing:
            self.init_animation_playing = False
            self.delete_animation_playing = True
            self.animation_start_time = pygame.time.get_ticks()
        elif not self.play_animation:
            self.kill()

    def play_delete_animation(self):
        animation_time_elapsed = pygame.time.get_ticks() - self.animation_start_time

        if animation_time_elapsed < self.animation_time:
            if self.animation_type == 'slide':
                distance = self.animation_dist * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)
                self.rect.centery = self.init_target_y + distance
        else:
            self.delete_animation_playing = False
            self.kill()

        # fading
        alpha = 255 * (1 - ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time))
        self.image.set_alpha(alpha)

    def play_init_animation(self):
        animation_time_elapsed = pygame.time.get_ticks() - self.animation_start_time

        if animation_time_elapsed < self.animation_time:
            if self.animation_type == 'slide':
                distance = self.animation_dist * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)
                self.rect.centery = self.delete_target_y - distance
        else:
            self.init_animation_playing = False
            self.rect.centery = self.init_target_y

        # fading
        alpha = 255 * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)
        self.image.set_alpha(alpha)


class PageUIElement(UIElement):
    def __init__(self, groups, image, pos, text_box_sub_surfs, play_animation=True, animation_type='slide'):
        # setup
        super().__init__(groups, pos, play_animation=play_animation, animation_type=animation_type)
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=pos)
        self.killed = False

        # groups
        self.ui_sprites = pygame.sprite.Group()
        self.button_sprites = pygame.sprite.Group()
        self.tile_sprites = pygame.sprite.Group()

        # ui elements
        self.start_time = pygame.time.get_ticks()
        self.alpha_time = self.animation_time
        self.alpha_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.alpha_surf, (50, 50, 50, 150), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        self.text_box_sub_surfs = text_box_sub_surfs

        self.item_tile_image = pygame.image.load('graphics/ui/item_tile.png').convert_alpha()
        self.item_card_image = pygame.image.load('graphics/ui/item_card.png').convert_alpha()
        self.button_image = pygame.image.load('graphics/ui/buttons/button.png').convert_alpha()
        self.exit_button_image = pygame.image.load('graphics/ui/buttons/exit_button.png').convert_alpha()

        self.name = None
        self.exit_button = None
        self.current_page = None
        self.current_displayed_tile = None
        self.item_card = None

    def play_delete_animation(self):
        animation_time_elapsed = pygame.time.get_ticks() - self.animation_start_time

        if animation_time_elapsed < self.animation_time:
            alpha = 150 * (1 - ease_in_ease_out_cubic(animation_time_elapsed / self.alpha_time))
            pygame.draw.rect(self.alpha_surf, (50, 50, 50, alpha), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            distance = self.animation_dist * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)
            self.rect.centery = self.init_target_y + distance
        else:
            self.delete_animation_playing = False
            self.kill()

        alpha = 255 * (1 - ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time))
        self.image.set_alpha(alpha)

    def play_init_animation(self):
        animation_time_elapsed = pygame.time.get_ticks() - self.animation_start_time

        if animation_time_elapsed < self.animation_time:
            alpha = 150 * ease_in_ease_out_cubic(animation_time_elapsed / self.alpha_time)
            pygame.draw.rect(self.alpha_surf, (50, 50, 50, alpha), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            distance = self.animation_dist * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)
            self.rect.centery = self.delete_target_y - distance
        else:
            pygame.draw.rect(self.alpha_surf, (50, 50, 50, 150), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
            self.rect.centery = self.init_target_y
            self.init_animation_playing = False

        alpha = 255 * ease_in_ease_out_cubic(animation_time_elapsed / self.animation_time)
        self.image.set_alpha(alpha)

    def set_play_animation(self, state):
        self.play_animation = state

        for element in self.ui_sprites:
            element.set_play_animation(state)

    def check_buttons(self):
        if self.exit_button.pressed:
            self.delete()

        for tile in self.tile_sprites:
            if tile.pressed and tile != self.current_displayed_tile:
                if self.current_displayed_tile:
                    self.current_displayed_tile.unstick()

                self.create_item_card(tile)
                tile.stick()

    def create_tile_positions(self, start_pos):
        positions = []

        for j in range(self.image.height // (self.item_tile_image.height + 20)):
            for i in range((self.image.width // 3 * 2) // (self.item_tile_image.width + 20)):
                new_pos = (start_pos + j * pygame.math.Vector2(0, self.item_tile_image.width + 20) +
                           i * pygame.math.Vector2(self.item_tile_image.height + 20, 0))
                positions.append(new_pos)

        return positions

    def create_item_card(self, tile):
        if self.item_card:
            self.item_card.delete()

        self.current_displayed_tile = tile
        self.item_card = ItemCard(self.ui_sprites, copy.deepcopy(self.item_card_image), tile.item, tile.stock,
                                  (self.rect.right - 20 - (self.item_card_image.width // 2),
                                   self.rect.top + 50 + (self.item_card_image.height // 2)),
                                  self.text_box_sub_surfs['wood'], play_animation=True)

    def delete(self):
        for sprite in self.ui_sprites:
            sprite.delete()

        if self.play_animation and not self.delete_animation_playing:
            self.init_animation_playing = False
            self.delete_animation_playing = True
            self.animation_start_time = pygame.time.get_ticks()
        elif not self.play_animation:
            self.kill()

    def draw_sprites(self, surface):
        self.image = self.original_image.copy()

        for sprite in self.ui_sprites:
            if hasattr(sprite, 'draw') and callable(getattr(sprite, 'draw')):
                sprite.draw(surface)
            else:
                surface.blit(sprite.image, sprite.rect)

    def draw(self, surface):
        # blurred background
        surface.blit(self.alpha_surf, (0, 0))

        # main UI background
        surface.blit(self.image, self.rect)

        # UI elements
        self.draw_sprites(surface)

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.check_buttons()
        self.ui_sprites.update(dt)