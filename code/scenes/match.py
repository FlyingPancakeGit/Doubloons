from camera import *
from ship import *
from structures.islands import *
from regions.sea import *
from code.generators.island_generator import *
from ui.hud import *
from regions.zones import *


class Match:
    def __init__(self):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.running = True
        self.clock = pygame.time.Clock()

        # groups
        self.match_sprites = CameraGroup()
        self.island_sprites = pygame.sprite.Group()
        self.port_zone_sprites = pygame.sprite.Group()
        self.cannonball_sprites = pygame.sprite.Group()

        # sea
        self.sea = Sea()

        # islands
        self.deserted_island_count = 1#random.randint(20, 30)
        self.merchant_island_count = 1#random.randint(10, 30)
        self.island_names = self.load_island_names()
        self.islands = []
        self.main_island = None
        self.island_generator = IslandGenerator()

        self.spawn_islands()

        # ship
        self.ship = None
        self.spawn_ship()

        self.cannonball_image = pygame.image.load('graphics/projectiles/cannonball.png').convert_alpha()

        # hud
        self.hud = HUD(self.main_island.rect.center, self.ship)

        # audio
        audio_manager.play('background_music', loop=True)

    def spawn_ship(self):
        image = pygame.image.load('graphics/ships/pirate_ship.png')
        self.ship = Ship(self.match_sprites, image, self.main_island.ship_spawn_pos, self.main_island.ship_spawn_rotation)

    def load_island_names(self):
        island_names = []

        with open('settings/island_names.txt', 'r') as f:
            for island in f.readlines():
                island_names.append(island.split('\n')[0])

        return island_names

    def spawn_islands(self):
        collision_count = 0
        # main island
        main_island_data = self.island_generator.generate_island(MERCHANT_ISLAND_SIZE, 'merchant')
        name = random.choice(self.island_names)
        pos = (0, 0)
        port_pos = pygame.math.Vector2(pos) + main_island_data['port_pos']
        ship_spawn_pos = pygame.math.Vector2(pos) + main_island_data['ship_spawn_pos']
        self.main_island = MerchantIsland((self.match_sprites, self.island_sprites), self.port_zone_sprites,
                                          main_island_data['image'], pos, port_pos, ship_spawn_pos,
                                          main_island_data['ship_spawn_rotation'], name)
        self.islands.append(self.main_island)

        # merchant islands
        for island in range(self.merchant_island_count):
            merchant_data = self.island_generator.generate_island(MERCHANT_ISLAND_SIZE, 'merchant')
            name = random.choice(self.island_names)
            collided = True
            new_island = None

            while collided:
                collision_count += 1
                pos = (random.randint(-ISLAND_SPAWN_DIST, ISLAND_SPAWN_DIST), random.randint(-ISLAND_SPAWN_DIST, ISLAND_SPAWN_DIST))
                port_pos = pygame.math.Vector2(pos) + merchant_data['port_pos']
                ship_spawn_pos = pygame.math.Vector2(pos) + merchant_data['ship_spawn_pos']
                new_island = MerchantIsland((self.match_sprites, self.island_sprites), self.port_zone_sprites,
                                            merchant_data['image'], pos,
                                            port_pos, ship_spawn_pos, merchant_data['ship_spawn_rotation'], name)
                collided = pygame.sprite.spritecollideany(new_island, self.islands)

                if collided:
                    new_island.destroy_island()

            self.islands.append(new_island)
        # deserted islands
        for island in range(self.deserted_island_count):
            deserted_image = self.island_generator.generate_island(DESERTED_ISLAND_SIZE, 'deserted')['image']
            collided = True
            new_island = None

            while collided:
                collision_count += 1
                pos = (random.randint(-ISLAND_SPAWN_DIST, ISLAND_SPAWN_DIST), random.randint(-ISLAND_SPAWN_DIST, ISLAND_SPAWN_DIST))
                new_island = Island((self.match_sprites, self.island_sprites), deserted_image, pos)
                collided = pygame.sprite.spritecollideany(new_island, self.islands)

                if collided:
                    new_island.kill()

            self.islands.append(new_island)

    def check_fire_cannon(self):
        if self.ship.cannon_firing_commands:
            for command in self.ship.cannon_firing_commands:
                self.fire_cannon(command)
            self.ship.cannon_firing_commands.clear()

    def fire_cannon(self, command):
        side = command.side
        side_rotation = (3 * math.pi) / 2 if side == PORT else math.pi / 2

        for pos_vector in self.ship.cannon_pos_vectors:
            pos = pygame.math.Vector2(self.ship.rect.center) + pos_vector
            direction = self.ship.direction.rotate_rad(side_rotation)
            speed = 400
            velocity = (direction * speed) + self.ship.velocity
            Cannonball((self.match_sprites, self.cannonball_sprites), self.cannonball_image, pos, velocity)

    def check_killed_cannonballs(self):
        for cannonball in self.cannonball_sprites:
            if cannonball.should_kill:
                cannonball.kill()

    def check_collisions(self):
        # ship collisions
        ship_collisions = pygame.sprite.spritecollide(self.ship, self.island_sprites, False, pygame.sprite.collide_mask)

        if ship_collisions:
            # calculate collision point using masks
            offset = (self.ship.rect.x - ship_collisions[0].rect.x, self.ship.rect.y - ship_collisions[0].rect.y)
            collision_point = ship_collisions[0].mask.overlap(self.ship.mask, offset)
            normal = self.get_mask_normal(ship_collisions[0].mask, collision_point[0], collision_point[1])
            speed = self.ship.velocity.magnitude()
            self.ship.external_forces.append(normal * speed * self.ship.mass * 100)

        else:
            self.ship.external_forces.clear()

        # fishing bob collisions
        if self.ship.casting:
            fishing_bob = self.ship.fishing_rod.fishing_bob
            fishing_bob_collisions = pygame.sprite.spritecollide(fishing_bob, self.island_sprites, False, pygame.sprite.collide_mask)

            if fishing_bob_collisions:
                # calculate collision point using masks
                offset = (fishing_bob.rect.x - fishing_bob_collisions[0].rect.x, fishing_bob.rect.y - fishing_bob_collisions[0].rect.y)
                collision_point = fishing_bob_collisions[0].mask.overlap(fishing_bob.mask, offset)
                normal = self.get_mask_normal(fishing_bob_collisions[0].mask, collision_point[0], collision_point[1])
                speed = fishing_bob.velocity.magnitude()
                fishing_bob.external_forces.append(normal * speed * fishing_bob.mass * 100)

    def get_mask_normal(self, mask, x, y, radius=2):
        average_vector = pygame.math.Vector2(0, 0)

        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                if (mask.get_size()[0] < (x+dx) < 0) or (mask.get_size()[0] < (y+dy) < 0):
                    break

                pixel = mask.get_at((x+dx, y+dy))

                if pixel:
                    average_vector += pygame.math.Vector2(-dx, -dy)

        return average_vector.normalize() if average_vector else average_vector

    def check_can_dock(self):
        port = pygame.sprite.spritecollide(self.ship, self.port_zone_sprites, False)

        if port and not self.ship.fishing:
            if self.ship.docking_timer.finished:
                self.ship.can_dock = True
                self.ship.port_docked_at = f'{port[0].name} Isle'
            else:
                self.ship.can_dock = False
        else:
            self.ship.can_dock = False
            self.ship.docked = False

    def check_fishing_rod(self): # Handles match-side fishing logic
        if self.ship.casting:
            fishing_rod = self.ship.fishing_rod

            if not fishing_rod.fishing_bob.time_to_spend_bobbing:
                fishing_rod.fishing_bob.time_to_spend_bobbing = self.sea.get_bobbing_time()

            if fishing_rod.hooked:
                if not fishing_rod.hooked_fish:
                    fishing_rod.hooked_fish = self.sea.get_catch(fishing_rod.fishing_bob.rect.center)
                elif self.hud.fishing_bar.fish_caught is not None:
                    if self.hud.fishing_bar.fish_caught:
                        self.ship.stop_casting()
                        self.ship.activate_engine_timer.start()
                        self.ship.inventory.add_item(fishing_rod.hooked_fish)

                    fishing_rod.fishing_bob.hooked = False
                    fishing_rod.hooked_fish = None

    def draw_sprites(self, surface):
        for sprite in self.match_sprites:
            if hasattr(sprite, 'draw') and callable(getattr(sprite, 'draw')):
                sprite.draw(surface)
            else:
                surface.blit(sprite.image, sprite.rect)

    def end_match(self):
        for filename in os.listdir('data'):
            file_path = os.path.join('data', filename)

            if os.path.isfile(file_path):
                os.remove(file_path)

    def match_loop(self):
        while self.running:
            dt = self.clock.tick() / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_match()
                    pygame.quit()
                    sys.exit()

            # update
            self.match_sprites.update(dt)
            self.hud.update(dt)

            self.check_fire_cannon()

            self.check_can_dock()
            self.check_fishing_rod()
            self.check_collisions()

            # draw
            self.display_surface.fill(SEA)

            self.match_sprites.draw(self.ship.rect.center)
            self.hud.draw()

            pygame.display.update()