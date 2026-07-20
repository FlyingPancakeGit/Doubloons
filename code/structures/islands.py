from regions.zones import *


class Island(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        pass

class MerchantIsland(Island):
    def __init__(self, groups, port_zone_group, image, pos, port_pos, ship_spawn_pos, ship_spawn_rotation, name):
        super().__init__(groups, image, pos)
        self.port_zone = PortZone((groups[0], port_zone_group), port_pos, name)
        self.ship_spawn_pos = ship_spawn_pos
        self.ship_spawn_rotation = ship_spawn_rotation
        self.name = name

    def destroy_island(self):
        self.port_zone.kill()
        self.kill()

    def update(self, dt):
        pass

