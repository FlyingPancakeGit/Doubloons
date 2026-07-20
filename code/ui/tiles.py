from ui_elements import *
from buttons import *

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