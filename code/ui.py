import pygame.mouse

from audio_manager import audio_manager
from formulas import *
from code.generators.hue_generator import *
from timer import *


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


class Image(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        # setup
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.hit_box_rect = self.rect


class Text(UIElement):
    def __init__(self, groups, text, font_size, pos, colour=TEXT_BOX_BLACK, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.image = self.create_image(text, colour, font_size)
        self.rect = self.image.get_frect(center=pos)

        self.colour = colour
        self.font_size = font_size

    def create_image(self, text, colour, font_size):
        rendered_text = None

        if font_size == 'small':
            rendered_text = SMALL_FONT.render(text, True, colour)
        elif font_size == 'medium':
            rendered_text = FONT.render(text, True, colour)
        elif font_size == 'large':
            rendered_text = LARGE_FONT.render(text, True, colour)

        surf = pygame.Surface((rendered_text.width, rendered_text.height), pygame.SRCALPHA)
        surf.blit(rendered_text, (0, 0))

        return surf

    def change_text(self, text):
        self.image = self.create_image(text, self.colour, self.font_size)

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()


class Button(UIElement):
    def __init__(self, groups, image, pos, play_animation=True, container_offset=(0, 0)):
        # setup
        super().__init__(groups, pos,  play_animation=play_animation)
        self.images = self.create_button_images(image)
        self.image = self.images['normal']
        self.rect = self.image.get_frect(center=pos)
        self.container_offset = pygame.math.Vector2(container_offset)

        # state
        self.disabled = False
        self.stuck = False
        self.pressed = False

    def create_button_images(self, normal_image):
        surf = pygame.Surface((normal_image.get_width() + 6, normal_image.get_height() + 6), pygame.SRCALPHA)


        for offset in [(-3, -3), (0, -3), (3, -3), (-3, 0), (3, 0), (-3, 3), (0, 3), (3, 3)]:
            outline_surf = pygame.mask.from_surface(normal_image).to_surface(setcolor=(255, 215, 0), unsetcolor=(0, 0, 0, 0))

            center_pos = pygame.math.Vector2(surf.width//2, surf.height//2) + offset
            outline_rect = outline_surf.get_rect(center=center_pos)
            surf.blit(outline_surf, outline_rect)


        surf.blit(normal_image, (3, 3))

        return {
            'normal': normal_image,
            'hover': surf,
            'pressed': pygame.transform.scale_by(surf, 0.9)
        }

    def check_state(self):
        # exit conditions
        if self.init_animation_playing or self.delete_animation_playing:
            return

        if self.stuck:
            self.image = self.images['pressed']
            self.rect = self.image.get_frect(center=self.rect.center)
            self.pressed = False
            return

        offset_mouse_pos = pygame.mouse.get_pos() - self.container_offset

        if self.rect.collidepoint(offset_mouse_pos):
            if pygame.mouse.get_just_pressed()[0]:
                self.image = self.images['pressed']
                self.rect = self.image.get_frect(center=self.rect.center)

                if not self.disabled:
                    self.pressed = True
                    audio_manager.play('button_press')
                else:
                    self.pressed = False
                    audio_manager.play('error')
            else:
                self.image = self.images['hover']
                self.rect = self.image.get_frect(center=self.rect.center)
                self.pressed = False
        else:
            self.image = self.images['normal']
            self.rect = self.image.get_frect(center=self.rect.center)
            self.pressed = False

    def stick(self):
        self.image = self.images['pressed']
        self.stuck = True

    def unstick(self):
        self.image = self.images['normal']
        self.stuck = False

    def delete(self):
        super().delete()
        self.pressed = False

    def update(self, dt):
        # animations
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.check_state()


class TextButton(Button):
    def __init__(self, groups, image, pos, text, colour=(240, 240, 240), play_animation=True):
        # setup
        super().__init__(groups, image, pos, play_animation=play_animation)

        # text
        self.text = text
        self.text_surf = FONT.render(text, True, colour)
        self.blit_text()

    def blit_text(self):
        for key, image in self.images.items():
            text_rect = self.text_surf.get_frect(center=(image.get_width()/2, image.get_height()/2))
            image.blit(self.text_surf, text_rect)


class ItemCard(UIElement):
    def __init__(self, groups, image, item, stock, pos, text_box_sub_surfs, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.image = image
        self.rect = self.image.get_frect(center=pos)
        self.item = item
        self.stock = stock

        # groups
        self.ui_sprites = pygame.sprite.Group()

        # text
        self.text_box_sub_surfs = text_box_sub_surfs
        self.price_text = None
        self.stock_text = None
        self.total_text = None

        self.descriptions = []

        # images
        self.button_image = pygame.image.load('graphics/ui/buttons/button.png').convert_alpha()

        # buttons
        self.minus_button = None
        self.plus_button = None

        # methods
        ItemCard.create_elements(self)

    def set_play_animation(self, state):
        for sprite in self.ui_sprites:
            sprite.set_play_animation(state)

        self.play_animation = state

    def create_elements(self):
        if self.item:
            # image
            display_image = pygame.Surface((self.image.width - 6, 150))
            hue = generate_hue(self.image.get_at((5, 5)), RARITY_COLOURS[self.item.rarity], (294, 150))
            display_image.blit(hue, (0, 0))
            item_image = pygame.transform.scale2x(self.item.image) if self.item.image.height * 2 < 120 else self.item.image
            item_rect = item_image.get_frect(center=(self.image.get_width() // 2, 90))
            display_image.blit(item_image, item_rect)

            self.image.blit(display_image, (3, 3))

            # text
            TextBox(self.ui_sprites, self.rect.midtop, self.text_box_sub_surfs,
                    self.item.name, colour=RARITY_COLOURS[self.item.rarity], play_animation=self.play_animation)

            self.price_text = Text(self.ui_sprites, f'${self.item.price}', 'medium',
                                   (self.rect.left + self.image.width * 0.25, self.rect.top + 172),
                                   play_animation=self.play_animation)
            self.stock_text = Text(self.ui_sprites, f'x{self.stock}', 'medium',
                                   (self.rect.left + self.image.width * 0.75, self.rect.top + 172),
                                   play_animation=self.play_animation)

            description_texts = self.render_description()
            description_rects = self.create_description_rects(description_texts,
                                                              [self.image.width // 2, self.image.get_height() * 0.45])
            self.descriptions = list(zip(description_texts, description_rects))

            for text, rect in self.descriptions:
                self.image.blit(text, rect)
        else:
            TextBox(self.ui_sprites, self.rect.midtop, self.text_box_sub_surfs,
                    'Empty Slot')

            description_text = SMALL_FONT.render('This slot is empty.', True, TEXT_BOX_GREY)
            description_rect = description_text.get_frect(center=(self.image.width//2, self.image.get_height()*0.45))
            self.image.blit(description_text, description_rect)

    def render_description(self):
        rendered_lines = []
        lines = self.item.description.split('|')

        for line in lines:
            rendered_lines.append(SMALL_FONT.render(line, True, TEXT_BOX_GREY))

        return rendered_lines

    def create_description_rects(self, texts, start_pos):
        description_rects = []
        pos = start_pos

        for text in texts:
            description_rects.append(text.get_frect(center=pos))
            pos[1] += text.height + 5

        return description_rects

    def delete(self):
        for sprite in self.ui_sprites:
            sprite.delete()

        if self.play_animation and not self.delete_animation_playing:
            self.init_animation_playing = False
            self.delete_animation_playing = True
            self.animation_start_time = pygame.time.get_ticks()
        elif not self.play_animation:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.ui_sprites.draw(surface)

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.ui_sprites.update(dt)


class SellItemCard(ItemCard):
    def __init__(self, groups, image, item, stock, pos, text_box_sub_surfs,
                 item_bought_callback, out_of_stock_callback, play_animation=True):
        # setup
        super().__init__(groups, image, item, stock, pos, text_box_sub_surfs, play_animation=play_animation)

        # images
        self.arrow_button_image = pygame.image.load('graphics/ui/buttons/arrow_button.png').convert_alpha()
        self.number_display_image = pygame.image.load('graphics/ui/number_display.png').convert_alpha()

        # buttons
        self.buy_button = None
        self.buy_all_button = None
        self.number_display = None

        # callbacks
        self.item_bought_callback = item_bought_callback
        self.out_of_stock_callback = out_of_stock_callback

        # methods
        self.create_elements()

    def create_elements(self):
        # number display
        self.number_display = NumberDisplay(self.ui_sprites, self.number_display_image,
                                            (self.rect.centerx,
                                             self.rect.bottom - self.number_display_image.height // 2 - 10 - self.button_image.height - 10),
                                            1, self.stock, 1, play_animation=self.play_animation)

        # text
        total = self.number_display.num * self.item.price
        self.total_text = Text(self.ui_sprites, f'Total: ${total}', 'small',
                               (self.number_display.rect.centerx, self.number_display.rect.top - 10),
                               colour=TEXT_BOX_GREY,
                               play_animation=self.play_animation)

        # buttons
        self.minus_button = Button(self.ui_sprites, self.arrow_button_image,
                                   (self.number_display.rect.left - self.arrow_button_image.width // 2 - 10,
                                    self.rect.bottom - self.arrow_button_image.height // 2 - 10 - self.button_image.height - 10),
                                   play_animation=self.play_animation)

        self.plus_button = Button(self.ui_sprites, pygame.transform.flip(self.arrow_button_image, True, False),
                                  (self.number_display.rect.right + self.arrow_button_image.width // 2 + 10,
                                   self.rect.bottom - self.arrow_button_image.height // 2 - 10 - self.button_image.height - 10),
                                  play_animation=self.play_animation)

        self.buy_button = TextButton(self.ui_sprites, copy.deepcopy(self.button_image),
                                      (self.rect.left+self.button_image.width//2+10,
                                       self.rect.bottom-self.button_image.height//2-10),
                                      'Buy', play_animation=self.play_animation)

        self.buy_all_button = TextButton(self.ui_sprites, copy.deepcopy(self.button_image),
                                      (self.rect.right-self.button_image.width//2-10,
                                       self.rect.bottom-self.button_image.height//2-10),
                                      'Buy All', play_animation=self.play_animation)

    def update_text(self):
        self.stock_text.change_text(f'x{self.stock}')
        self.total_text.change_text(f'Total: ${self.item.price * self.number_display.num}')

    def purchase_made(self, amount):
        self.stock -= amount
        self.number_display.update_range(0, self.stock)
        audio_manager.play('purchase')

        TextMessage(self.ui_sprites, self.rect.center, f'x{amount}| {self.item.name}',
                    (TEXT_BOX_BLACK, RARITY_COLOURS[self.item.rarity]), time_until_fade=0, fade_time=1000)

        if self.stock == 0:
            self.out_of_stock_callback()

    def purchase_denied(self, button_pressed):
        TextMessage(self.ui_sprites,
                    button_pressed.rect.center, f'Insufficient funds',
                    [TEXT_BOX_RED], time_until_fade=0, fade_time=1000, centered=True)

    def check_buttons_pressed(self):
        # button pressing
        if self.minus_button and self.minus_button.pressed:
            self.number_display.add_to_num(-1)
        if self.plus_button and self.plus_button.pressed:
            self.number_display.add_to_num(1)
        if self.buy_button and self.buy_button.pressed:
            result = self.item_bought_callback(self.item, self.number_display.num)

            if result:
                self.purchase_made(self.number_display.num)
            else:
                self.purchase_denied(self.buy_button)
                audio_manager.play('error')

        if self.buy_all_button and self.buy_all_button.pressed:
            result = self.item_bought_callback(self.item, self.stock)

            if result:
                self.purchase_made(self.stock)
            else:
                self.purchase_denied(self.buy_all_button)
                audio_manager.play('error')

        # button disabling
        if self.number_display.num == self.number_display.min_num:
            self.minus_button.disabled = True
        else:
            self.minus_button.disabled = False

        if self.number_display.num == self.number_display.max_num:
            self.plus_button.disabled = True
        else:
            self.plus_button.disabled = False

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.ui_sprites.update(dt)

        self.check_buttons_pressed()
        self.update_text()


class BuyItemCard(ItemCard):
    def __init__(self, groups, image, item, stock, pos, text_box_sub_surfs,
                 item_bought_callback, out_of_stock_callback, play_animation=True):
        # setup
        super().__init__(groups, image, item, stock, pos, text_box_sub_surfs, play_animation=play_animation)

        # images
        self.arrow_button_image = pygame.image.load('graphics/ui/buttons/arrow_button.png').convert_alpha()
        self.number_display_image = pygame.image.load('graphics/ui/number_display.png').convert_alpha()

        # buttons
        self.sell_button = None
        self.sell_all_button = None
        self.number_display = None

        # callbacks
        self.item_bought_callback = item_bought_callback
        self.out_of_stock_callback = out_of_stock_callback

        # methods
        self.create_elements()

    def create_elements(self):
        # number display
        self.number_display = NumberDisplay(self.ui_sprites, self.number_display_image,(self.rect.centerx,
                                             self.rect.bottom-self.number_display_image.height//2-10-self.button_image.height-10),
                                            1, self.stock, 1, play_animation=self.play_animation)

        # text
        total = self.number_display.num * self.item.price
        self.total_text = Text(self.ui_sprites, f'Total: ${total}', 'small',
                               (self.number_display.rect.centerx, self.number_display.rect.top - 10),
                               colour=TEXT_BOX_GREY,
                               play_animation=self.play_animation)

        # buttons
        self.minus_button = Button(self.ui_sprites, self.arrow_button_image,
                                   (self.number_display.rect.left - self.arrow_button_image.width // 2 - 10,
                                    self.rect.bottom - self.arrow_button_image.height // 2 - 10 - self.button_image.height - 10),
                                   play_animation=self.play_animation)

        self.plus_button = Button(self.ui_sprites, pygame.transform.flip(self.arrow_button_image, True, False),
                                  (self.number_display.rect.right + self.arrow_button_image.width // 2 + 10,
                                   self.rect.bottom - self.arrow_button_image.height // 2 - 10 - self.button_image.height - 10),
                                  play_animation=self.play_animation)

        self.sell_button = TextButton(self.ui_sprites, copy.deepcopy(self.button_image),
                                      (self.rect.left+self.button_image.width//2+10,
                                       self.rect.bottom-self.button_image.height//2-10),
                                      'Sell', play_animation=self.play_animation)

        self.sell_all_button = TextButton(self.ui_sprites, copy.deepcopy(self.button_image),
                                      (self.rect.right-self.button_image.width//2-10,
                                       self.rect.bottom-self.button_image.height//2-10),
                                      'Sell All', play_animation=self.play_animation)

    def update_text(self):
        self.stock_text.change_text(f'x{self.stock}')
        self.total_text.change_text(f'Total: ${self.item.price * self.number_display.num}')

    def sale_made(self, amount):
        self.stock -= amount
        self.number_display.update_range(0, self.stock)
        audio_manager.play('purchase')

        TextMessage(self.ui_sprites, self.rect.center, f'x{amount}| {self.item.name}',
                    (TEXT_BOX_BLACK, RARITY_COLOURS[self.item.rarity]), time_until_fade=0, fade_time=1000)

        if self.stock == 0:
            self.out_of_stock_callback()

    def check_buttons_pressed(self):
        # button pressing
        if self.minus_button and self.minus_button.pressed:
            self.number_display.add_to_num(-1)
        if self.plus_button and self.plus_button.pressed:
            self.number_display.add_to_num(1)
        if self.sell_button and self.sell_button.pressed:
            self.item_bought_callback(self.item, self.number_display.num)
            self.sale_made(self.number_display.num)
        if self.sell_all_button and self.sell_all_button.pressed:
            self.item_bought_callback(self.item, self.stock)
            self.sale_made(self.stock)

        # button disabling
        if self.number_display.num == self.number_display.min_num:
            self.minus_button.disabled = True
        else:
            self.minus_button.disabled = False

        if self.number_display.num == self.number_display.max_num:
            self.plus_button.disabled = True
        else:
            self.plus_button.disabled = False

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.ui_sprites.update(dt)

        self.check_buttons_pressed()
        self.update_text()


class ItemTile(Button):
    def __init__(self, groups, images, item, pos, stock,
                 play_animation=True, container_offset=(0, 0)):
        # setup
        super().__init__(groups, images, pos, play_animation=play_animation, container_offset=container_offset)

        # item info
        self.item = item
        self.stock = stock

        # ui elements
        self.create_tile_images()

    def create_tile_images(self):
        if self.item:
            rarity_hue_image = generate_hue(self.image.get_at((5, 5)), RARITY_COLOURS[self.item.rarity],
                                      (self.image.width-6, self.image.height-6))
            scaled_rarity_hue_image = pygame.transform.scale_by(rarity_hue_image, 0.91)
            scaled_item_image = pygame.transform.scale_by(self.item.image, 0.9)

            normal_image = self.images['normal']
            rarity_image_rect = (rarity_hue_image.get_frect(center=(normal_image.width // 2, normal_image.height // 2)))
            item_image_rect = self.item.image.get_frect(center=(normal_image.width // 2, normal_image.height // 2))
            self.images['normal'].blit(rarity_hue_image, rarity_image_rect)
            self.images['normal'].blit(self.item.image, item_image_rect)

            hover_image = self.images['hover']
            rarity_image_rect = (rarity_hue_image.get_frect(center=(hover_image.width // 2, hover_image.height // 2)))
            item_image_rect = self.item.image.get_frect(center=(hover_image.width // 2, hover_image.width // 2))
            self.images['hover'].blit(rarity_hue_image, rarity_image_rect)
            self.images['hover'].blit(self.item.image, item_image_rect)

            pressed_image = self.images['pressed']
            rarity_image_rect = (scaled_rarity_hue_image.get_frect(topleft=(5,5)))
            item_image_rect = scaled_item_image.get_frect(center=(pressed_image.width // 2, pressed_image.height // 2))
            self.images['pressed'].blit(scaled_rarity_hue_image, rarity_image_rect)
            self.images['pressed'].blit(scaled_item_image, item_image_rect)


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


class TextMessage(UIElement):
    def __init__(self, groups, pos, text, colours, play_animation=True, time_until_fade=1000, fade_time=500, centered=False):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.colours = colours
        self.texts = self.render_texts(text)
        self.image = self.create_image()
        self.rect = self.image.get_frect(bottomleft=pos)
        self.centered = centered

        # fading out
        self.message_init_time = pygame.time.get_ticks()
        self.time_until_fade = time_until_fade
        self.fade_time = fade_time
        self.fade_start_time = None

        # methods
        self.check_centered()

    def check_centered(self):
        if self.centered:
            self.rect = self.image.get_frect(center=self.rect.bottomleft)

    def render_texts(self, text):
        rendered_texts = []
        text_sections = text.split('|')

        for index, section in enumerate(text_sections):
            rendered_texts.append(FONT.render(section, True, self.colours[index]))

        return rendered_texts

    def create_image(self):
        height = self.texts[0].get_height()
        total_length = sum(text.get_width() for text in self.texts)
        image = pygame.Surface((total_length, height), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))

        current_margin = 0

        for text in self.texts:
            image.blit(text, (current_margin, 0))
            current_margin += text.get_width()

        return image

    def check_age(self):
        if pygame.time.get_ticks() - self.message_init_time > self.time_until_fade:
            self.fade_start_time = pygame.time.get_ticks()

    def fade_out(self, dt):
        time_elapsed = pygame.time.get_ticks() - self.fade_start_time

        if time_elapsed >= self.fade_time:
            self.kill()
        else:
            alpha = 255 * (1 - time_elapsed / self.fade_time)
            self.image.set_alpha(alpha)

            self.rect.centery -= 100 * dt

    def update(self, dt):
        if not self.fade_start_time:
            self.check_age()
        else:
            self.fade_out(dt)


class TextBox(UIElement):
    def __init__(self, groups, pos, sub_surfs, text, colour=TEXT_BOX_BLACK, play_animation=True):
        # setup
        super().__init__(groups, pos, play_animation=play_animation)
        self.sub_surfs = sub_surfs
        self.colour = colour
        self.text = FONT.render(text, True, colour)
        self.original_image = self.create_image()
        self.image = self.original_image.copy()
        self.blit_text()
        self.rect = self.image.get_rect(center=pos)

    def create_image(self):
        width = self.sub_surfs[0].get_width()
        height = self.sub_surfs[0].get_height()

        text_width = self.text.get_width() // width + (1 if self.text.get_width() - (self.text.get_width() // width) * width > 30 else 2)
        text_height = self.text.get_height() // height + 1

        surf = pygame.Surface((text_width * width, text_height * height), pygame.SRCALPHA)

        for x in range(text_width):
            for y in range(text_height):
                pos = (x * width, y * height)

                if x == 0:
                    if y == 0:
                        surf.blit(self.sub_surfs[0], pos)
                    elif y == text_height - 1:
                        surf.blit(self.sub_surfs[6], pos)
                    else:
                        surf.blit(self.sub_surfs[3], pos)
                elif x == text_width - 1:
                    if y == 0:
                        surf.blit(self.sub_surfs[2], pos)
                    elif y == text_height - 1:
                        surf.blit(self.sub_surfs[8], pos)
                    else:
                        surf.blit(self.sub_surfs[5], pos)
                else:
                    if y == 0:
                        surf.blit(self.sub_surfs[1], pos)
                    elif y == text_height - 1:
                        surf.blit(self.sub_surfs[7], pos)
                    else:
                        surf.blit(self.sub_surfs[4], pos)

        return surf

    def update_text(self, text, colour=None):
        if colour:
            self.colour = colour

        self.text = FONT.render(text, True, self.colour)
        self.blit_text()

    def blit_text(self):
        self.image = self.original_image.copy()
        text_rect = self.text.get_rect(center=(self.image.get_width()//2, self.image.get_height()//2))
        self.image.blit(self.text, text_rect)

    def update(self, dt):
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()


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