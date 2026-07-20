from entities.cannonball import *
from timer import *
from regions.zones import *
from entities.fishing_rod import *
from ui.inventory import *


class Ship(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos, initial_rotation):
        # setup
        super().__init__(groups)
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.name = None
        self.timers = []

        # groups
        self.match_sprites = groups[0] if type(groups) is list else groups

        # inventory
        self.inventory = InventoryBackend(self)
        self.inventory_open = False

        # engine
        self.activate_engine_timer = Timer(500)
        self.timers.append(self.activate_engine_timer)

        self.can_activate_engine = True
        self.engine_on = False

        # scalars
        self.mass = 100
        self.max_thrust_magnitude = 100000
        self.rudder_angle = 0
        self.angular_acceleration = 0
        self.rotation = math.pi - math.radians(initial_rotation)

        # health
        self.max_health = 100
        self.health = self.max_health

        # cannon
        self.cannon_firing_commands = []
        self.can_fire_cannon = {
            PORT: True,
            STARBOARD: True
        }
        self.cannon_cooldown = 3000
        self.last_cannon_firing_times = {
            PORT: -self.cannon_cooldown,
            STARBOARD: -self.cannon_cooldown
        }

        # docking
        self.can_dock = False
        self.docked = False
        self.port_docked_at = None

        self.docking_timer = Timer(1000)
        self.timers.append(self.docking_timer)

        # fishing
        self.can_fish = False
        self.fishing = False
        self.fishing_zone = None

        self.can_cast = False
        self.casting = False

        self.start_fishing_timer = Timer(500)
        self.stop_fishing_timer = Timer(500)
        self.start_casting_timer = Timer(500)
        self.stop_casting_timer = Timer(500)

        self.timers.append(self.start_fishing_timer)
        self.timers.append(self.stop_fishing_timer)
        self.timers.append(self.start_casting_timer)
        self.timers.append(self.stop_casting_timer)

        self.fishing_rod = None

        # vectors
        self.velocity = pygame.math.Vector2()
        self.thrust = pygame.math.Vector2()
        self.original_direction = pygame.math.Vector2(0, -1)
        self.direction = self.original_direction
        self.drag = pygame.math.Vector2()
        self.resultant_force = pygame.math.Vector2()

        self.external_forces = []

        self.original_water_particle_pos_vector = pygame.math.Vector2(0, 50)
        self.water_particle_pos_vector = self.original_water_particle_pos_vector

        self.original_cannon_pos_vectors = [
            pygame.math.Vector2(10, 18),
            pygame.math.Vector2(10, -18)
        ]
        self.cannon_pos_vectors = self.original_cannon_pos_vectors

        # particles
        self.water_particle_emitter = ParticleEmitter(self.match_sprites, self.rect.center + self.water_particle_pos_vector,
                                                      (30, 30), (8, 13), [SEA_FOAM],
                                                      (math.pi * 0.25, math.pi * 0.75), (10, 100),0)
        self.rotate()

        # audio
        self.movement_audio_playing = False

    def calculate_drag(self):
        magnitude = DRAG_FACTOR * (self.velocity.magnitude() ** 2)
        velocity_direction = self.velocity.normalize() if self.velocity else self.velocity
        self.drag = -velocity_direction * magnitude

    def calculate_thrust(self):
        if self.engine_on:
            self.thrust = self.direction * self.max_thrust_magnitude
        else:
            self.thrust = pygame.math.Vector2(0, 0)

    def calculate_velocity(self, dt):
        # Forces exerted onto the ship externally (e.g., from island collisions).
        sum_external_force = pygame.math.Vector2(0, 0)

        for external_force in self.external_forces:
            sum_external_force += external_force

        self.resultant_force = self.thrust + self.drag + sum_external_force
        acceleration = self.resultant_force / self.mass

        self.velocity += acceleration * dt

        # External forces are appended to the list each frame they are active for, and so this list should be cleared each
        # frame to prevent the same force stacking up over time.
        self.external_forces.clear()

    def calculate_rotation(self, dt):
        pressure = 5 * self.velocity.magnitude()
        torque_magnitude = pressure * math.sin(self.rudder_angle)
        self.angular_acceleration = torque_magnitude / self.mass
        self.rotation += self.angular_acceleration * dt

    def get_input(self, dt):
        keys = pygame.key.get_pressed()
        if not self.docked:
            # inventory
            if keys[pygame.K_i]:
                self.inventory_open = True

            # engine
            if self.activate_engine_timer.finished and self.casting and self.fishing_rod.fishing_bob.hooked:
                self.can_activate_engine = False
            else:
                self.can_activate_engine = True

            self.engine_on = keys[pygame.K_SPACE] if self.can_activate_engine else False

            # rotate rudder
            if keys[pygame.K_a]:
                self.rudder_angle -= math.pi / 18 * dt
            if keys[pygame.K_d]:
                self.rudder_angle += math.pi / 18 * dt
            if not (keys[pygame.K_a] or keys[pygame.K_d]):
                self.restore_rudder()
            self.rudder_angle = min(max(self.rudder_angle, -math.pi / 12), math.pi / 12)

            # fire cannon
            if keys[pygame.K_q] and self.can_fire_cannon[PORT]:
                self.cannon_firing_commands.append(CannonFiringCommand(PORT))
                self.last_cannon_firing_times[PORT] = pygame.time.get_ticks()
                self.inventory.cannonballs -= 2
            if keys[pygame.K_e] and self.can_fire_cannon[STARBOARD]:
                self.cannon_firing_commands.append(CannonFiringCommand(STARBOARD))
                self.last_cannon_firing_times[STARBOARD] = pygame.time.get_ticks()
                self.inventory.cannonballs -= 2

            # fishing
            if self.fishing:
                if self.stop_fishing_timer.finished and keys[pygame.K_f]:
                    self.stop_fishing()
            elif self.can_fish and keys[pygame.K_f]:
                self.fish()

            # casting
            if self.casting and keys[pygame.K_c]:
                if self.fishing_rod.baited:
                    self.fishing_rod.fishing_bob.hooked = True
                elif self.stop_casting_timer.finished:
                    self.stop_casting()
            elif self.can_cast and keys[pygame.K_c]:
                self.cast()

            # dock
            if self.can_dock and keys[pygame.K_t]:
                self.docked = True
                self.docking_timer.start()

        elif self.docked and self.can_dock and keys[pygame.K_t]:
                self.docked = False
                self.docking_timer.start()

    def restore_rudder(self):
        if self.rudder_angle > 0:
            self.rudder_angle -= self.rudder_angle * math.sin(self.rudder_angle)
        else:
            self.rudder_angle += self.rudder_angle * math.sin(self.rudder_angle)

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_image, math.degrees(-self.rotation))
        self.rect = self.image.get_frect(center=self.rect.center)
        self.direction = self.original_direction.rotate_rad(self.rotation)

        self.water_particle_pos_vector = self.original_water_particle_pos_vector.rotate_rad(self.rotation)

        self.cannon_pos_vectors = []
        for cannon_pos_vector in self.original_cannon_pos_vectors:
            self.cannon_pos_vectors.append(cannon_pos_vector.rotate_rad(self.rotation))

    def move(self, dt):
        self.rect.center += self.velocity * dt

    def check_can_fire_cannon(self):
        if self.inventory.cannonballs > 0:
            if pygame.time.get_ticks() - self.last_cannon_firing_times[PORT] > self.cannon_cooldown:
                self.can_fire_cannon[PORT] = True
            else:
                self.can_fire_cannon[PORT] = False

            if pygame.time.get_ticks() - self.last_cannon_firing_times[STARBOARD] > self.cannon_cooldown:
                self.can_fire_cannon[STARBOARD] = True
            else:
                self.can_fire_cannon[STARBOARD] = False
        else:
            self.can_fire_cannon[PORT] = False
            self.can_fire_cannon[STARBOARD] = False

    def check_can_fish(self):
        if self.velocity.magnitude() < 300 and self.start_fishing_timer.finished:
            self.can_fish = True
        else:
            self.can_fish = False

            if self.fishing:
                self.stop_fishing()

    def check_can_cast(self):
        if self.fishing and self.start_casting_timer.finished:
            self.can_cast = True
        else:
            self.can_cast = False

    def check_play_audio(self):
        if self.velocity.magnitude() > 300 and not self.movement_audio_playing:
            audio_manager.play('water_crashing', loop=True, fade=True)
            self.movement_audio_playing = True
        elif self.velocity.magnitude() < 300:
            audio_manager.stop('water_crashing')
            self.movement_audio_playing = False

    def _display_vectors(self, island_pos_list=None):
        start_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        thrust_direction = 100 * self.thrust.normalize() if self.thrust else self.thrust
        velocity_direction = 100 * self.velocity.normalize() if self.velocity else self.velocity
        drag_direction = 100 * self.drag.normalize() if self.drag else self.drag

        min_dist = 0
        min_dist_vector = None
        min_dist_direction = None

        if island_pos_list:
            for pos in island_pos_list:
                displacement = (pygame.math.Vector2(pos[0], pos[1]) - pygame.math.Vector2(self.rect.center[0], self.rect.center[1]))
                distance = displacement.magnitude()

                if min_dist_vector is None or distance < min_dist:
                    min_dist_vector = displacement
                    min_dist = distance

            min_dist_direction = 100 * min_dist_vector.normalize() if min_dist_vector else min_dist_vector

        pygame.draw.line(pygame.display.get_surface(), (0, 255, 0), start_pos, start_pos+thrust_direction, width=3)
        pygame.draw.line(pygame.display.get_surface(), (0, 0, 255), start_pos, start_pos+velocity_direction, width=3)
        pygame.draw.line(pygame.display.get_surface(), (255, 0, 0), start_pos, start_pos+drag_direction, width=3)

        if island_pos_list:
            pygame.draw.line(pygame.display.get_surface(), (255, 0, 255), start_pos, start_pos+min_dist_direction, width=3)

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

    def damage(self, damage_amount):
        self.health = max(0, self.health - damage_amount)

    def fish(self):
        self.fishing = True
        self.fishing_zone = FishingZone((self.match_sprites), self)
        self.stop_fishing_timer.start()

    def cast(self):
        mouse_direction = (pygame.mouse.get_pos() - pygame.math.Vector2(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)).normalize()

        self.casting = True
        fishing_rod_image = pygame.image.load('graphics/projectiles/fishing_bob.png').convert_alpha()
        self.fishing_rod = FishingRod(self.match_sprites, fishing_rod_image, self, self.fishing_zone,
                                      mouse_direction * (self.fishing_zone.rect.width * 0.35))
        self.stop_casting_timer.start()

    def stop_fishing(self):
        self.fishing = False
        self.fishing_zone.delete()
        self.fishing_zone = None

        if self.casting:
            self.stop_casting()

        self.start_fishing_timer.start()

    def stop_casting(self):
        self.casting = False
        self.fishing_rod.delete()
        self.fishing_rod = None

        self.start_casting_timer.start()

    def check_fishing_rod(self):
        if self.fishing_rod and self.fishing_rod.snapped:
            self.stop_fishing()

    def update_particle_emitters(self, dt):
        self.water_particle_emitter.rect.center = self.rect.center + self.water_particle_pos_vector
        self.water_particle_emitter.rotation_degrees = math.degrees(self.rotation)
        self.water_particle_emitter.frequency = (self.velocity.magnitude() / 30) ** 2
        self.water_particle_emitter.speed_range = (0, self.velocity.magnitude() / 10)

        self.water_particle_emitter.update(dt)

    def validate_purchase(self, item, amount):
        cost = item.price * amount

        if cost < self.inventory.doubloons:
            for i in range(amount):
                self.inventory.add_item(item)
            return True
        else:
            return False

    def update(self, dt):
        # general
        for timer in self.timers:
            timer.update()

        self.update_mask()
        self.check_can_fire_cannon()
        self.check_fishing_rod()
        self.check_can_fish()
        self.check_can_cast()
        self.check_play_audio()
        self.get_input(dt)

        # movement
        self.calculate_drag()
        self.calculate_thrust()
        self.calculate_velocity(dt)
        self.calculate_rotation(dt)

        # appearance
        self.update_particle_emitters(dt)

        self.move(dt)
        self.rotate()