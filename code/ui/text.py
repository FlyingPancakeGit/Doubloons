from ui_elements import *


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