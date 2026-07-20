from ui_elements import *


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
