from ship import *
from structures.islands import *
from particles import *


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2(0, 0)

    def draw(self, target_pos):
        self.offset.x = (target_pos[0] - WINDOW_WIDTH / 2) * -1
        self.offset.y = (target_pos[1] - WINDOW_HEIGHT / 2) * -1

        zone_sprites = [sprite for sprite in self if type(sprite) == PortZone or type(sprite) == FishingZone]
        island_sprites = [sprite for sprite in self if type(sprite) == Island or type(sprite) == MerchantIsland]
        particle_sprites = [sprite for sprite in self if type(sprite) == Particle]
        projectile_sprites = [sprite for sprite in self if type(sprite) == Cannonball or type(sprite) == FishingBob]
        line_sprites = [sprite for sprite in self if type(sprite) == FishingRod]
        ship_sprites = [sprite for sprite in self if type(sprite) == Ship]

        for layer in [zone_sprites, island_sprites, particle_sprites, projectile_sprites, line_sprites, ship_sprites]:
            for sprite in sorted(layer, key=lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)