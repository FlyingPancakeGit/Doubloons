from ui_elements import *


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