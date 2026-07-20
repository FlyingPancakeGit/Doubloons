from settings import *

from audio_manager import audio_manager
from formulas import *
from particles import *


class FishingBob(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos, ship, initial_force):
        # setup
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.ship = ship

        # scalars
        self.mass = 0.5
        self.height_above_water = 10
        self.velocity_vertical = 0

        # vectors
        self.velocity = pygame.math.Vector2(0, 0)
        self.thrust = pygame.math.Vector2(0, 0)
        self.drag = pygame.math.Vector2()
        self.resultant_force = pygame.math.Vector2()

        self.external_forces = []
        self.external_forces.append(initial_force)

        # initial casting
        audio_manager.play('whoosh')
        self.initial_ship_pos = self.ship.rect.center
        self.equilibrium = None

        self.casting_time = 500
        self.casting_start_time = pygame.time.get_ticks()

        # ambient bobbing
        self.ambient_animation_angle = 0
        self.max_bob_displacement = pygame.math.Vector2(0, 3)
        self.equilibrium = None

        self.bobbing_start_time = None
        self.time_to_spend_bobbing = 1000

        # baiting
        self.baited = False
        self.baited_particle_emitter = None

        self.baited_start_time = None
        self.time_to_spend_baited = 1000

        # hooking
        self.hooked = False

        # reeling
        self.reeling_in = False

    def check_fish_escaped(self):
        if self.baited_start_time and pygame.time.get_ticks() - self.baited_start_time > self.time_to_spend_baited:
            self.set_fish_escaped()

    def set_fish_escaped(self):
        self.baited = False
        self.baited_particle_emitter.kill()
        self.baited_particle_emitter = None

        self.bobbing_start_time = pygame.time.get_ticks()
        self.time_to_spend_bobbing = 1000

    def check_fish_baited(self):
        if (self.bobbing_start_time and self.time_to_spend_bobbing
                and pygame.time.get_ticks() - self.bobbing_start_time > self.time_to_spend_bobbing):

            self.baited = True
            self.baited_start_time = pygame.time.get_ticks()

            if not self.baited_particle_emitter:
                self.baited_particle_emitter = ParticleEmitter(self.groups()[0],
                                pygame.math.Vector2(self.rect.center),(5, 5), (5, 10),
                                                    [SEA_FOAM], (0, math.pi * 2),
                                                    (30, 50), 10, percentage_fade_per_second=1)
                self.baited_particle_emitter.emit = True

            audio_manager.play('splash')

    def add_ambient_bobbing(self, dt):
        self.rect.center = self.equilibrium + self.max_bob_displacement * math.sin(self.ambient_animation_angle)
        self.ambient_animation_angle = (self.ambient_animation_angle + 2 * dt) % (2 * math.pi)

    def add_baited_bobbing(self, dt):
        self.rect.center = self.equilibrium + self.max_bob_displacement * 0.5 * math.sin(self.ambient_animation_angle * 32)
        self.ambient_animation_angle = (self.ambient_animation_angle + 2 * dt) % (2 * math.pi)

    def reel_in(self):
        displacement = pygame.math.Vector2(self.ship.rect.center) - pygame.math.Vector2(self.rect.center)
        direction = displacement.normalize()
        self.thrust = 10000 * direction
        self.height_above_water = 10

        if displacement.magnitude() < 50:
            self.reeling_in = False
            self.kill()

    # dynamics calculations
    def calculate_drag(self):
        magnitude = (0.01 if self.height_above_water > 0 else 1) * DRAG_FACTOR * (self.velocity.magnitude() ** 2)
        velocity_direction = self.velocity.normalize() if self.velocity else self.velocity
        self.drag = -velocity_direction * magnitude

    def calculate_velocity(self, dt):
        # Forces exerted onto the bob externally (e.g., from island collisions).
        sum_external_force = pygame.math.Vector2(0, 0)

        for external_force in self.external_forces:
            sum_external_force += external_force

        self.resultant_force = self.thrust + self.drag + sum_external_force
        acceleration_horizontal = self.resultant_force / self.mass
        acceleration_vertical = -9.8

        self.velocity += acceleration_horizontal * dt
        self.velocity_vertical  += acceleration_vertical * dt

        # External forces are appended to the list each frame they are active for, and so this list should be cleared each
        # frame to prevent the same force stacking up over time.
        self.external_forces.clear()

    def delete(self):
        if not self.reeling_in:
            self.reeling_in = True
            audio_manager.play('whoosh')

        if self.baited:
            self.baited_particle_emitter.kill()
            self.baited_particle_emitter = None

    def move(self, dt):
        self.rect.center += self.velocity * dt
        self.height_above_water = max(0, self.height_above_water + self.velocity_vertical * dt)

        if self.equilibrium:
            self.equilibrium += self.velocity * dt

    def update(self, dt):
        if self.reeling_in:
            self.reel_in()
        elif self.height_above_water == 0:
            if not self.baited:
                self.check_fish_baited()

                if self.equilibrium is None:
                    self.equilibrium = self.rect.center
                    self.bobbing_start_time = pygame.time.get_ticks()

                self.add_ambient_bobbing(dt)
            elif self.hooked:
                self.add_baited_bobbing(dt)
            else:
                self.check_fish_escaped()
                self.add_baited_bobbing(dt)

        # dynamics calculations
        self.calculate_drag()
        self.calculate_velocity(dt)
        self.move(dt)


class FishingRod(pygame.sprite.Sprite):
    def __init__(self, groups, fishing_bob_image, ship, fishing_zone, displacement):
        # setup
        super().__init__(groups)
        self.original_image = pygame.Surface((fishing_zone.rect.width, fishing_zone.rect.height), pygame.SRCALPHA)
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=ship.rect.center)

        # vectors
        self.rect_center_displacement = pygame.math.Vector2(self.image.get_width()//2, self.image.get_height()//2)

        # scalars
        self.hooked_fish = None

        # flags
        self.snapped = False
        self.baited = False
        self.hooked = False

        self.deleted = False

        # initial casting
        self.init_animation_playing = True
        self.ship = ship
        self.fishing_zone = fishing_zone
        self.initial_ship_pos = self.ship.rect.center
        self.displacement = displacement
        self.final_pos = self.ship.rect.center + self.displacement

        self.movement_time = 500
        self.movement_start_time = pygame.time.get_ticks()

        # ambient bobbing
        self.ambient_animation_angle = 0
        self.max_bob_displacement = pygame.math.Vector2(0, 3)

        # fishing bob
        if displacement:
            thrust = displacement.normalize() * 20000
        else:
            thrust = pygame.math.Vector2(0, 0)
        self.fishing_bob = FishingBob(groups, fishing_bob_image, self.rect.center, ship, thrust)

    # if the player moves too far from the bob, the line will snap
    def check_line_snapped(self):
        bob_dist_from_center = (pygame.math.Vector2(self.fishing_bob.rect.center) - pygame.math.Vector2(self.rect.center)).magnitude()

        if bob_dist_from_center > self.fishing_zone.rect.width // 2:
            self.init_animation_playing = False
            self.baited = False
            self.snapped = True

    def update_image(self):
        if self.fishing_bob:
            self.image = self.original_image.copy()
            pygame.draw.line(self.image, (50, 50, 50), (self.image.width//2, self.image.height//2),
                             pygame.math.Vector2(self.fishing_bob.rect.center) - pygame.math.Vector2(self.rect.topleft), width=3)
            self.rect = self.image.get_frect(center=self.ship.rect.center)

    def delete(self):
        self.deleted = True
        self.fishing_bob.delete()

    def update(self, dt):
        if not self.deleted:
            self.baited = self.fishing_bob.baited
            self.hooked = self.fishing_bob.hooked
            self.check_line_snapped()
        elif not self.fishing_bob.alive():
            self.kill()

        self.update_image()