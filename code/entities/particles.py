from settings import *


class Particle(pygame.sprite.Sprite):
    def __init__(self, groups, size, pos, colour, velocity, deceleration=None,
                 fade_delay=None, fade_percentage_per_second=None):
        super().__init__(groups)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(colour)
        self.rect = self.image.get_frect(center=pos)

        # age
        self.spawn_time = pygame.time.get_ticks()

        # appearance
        self.fade_delay = fade_delay if fade_delay else 500 + random.randint(-100, 100)
        self.fade_percentage_per_second = fade_percentage_per_second if fade_percentage_per_second else 0.5
        self.fade = 255

        # vectors
        self.velocity = velocity
        self.deceleration = deceleration

    def check_fade(self):
        if self.image.get_alpha() <= 0:
            self.kill()

    def fade_out(self, dt):
        if pygame.time.get_ticks() - self.spawn_time > self.fade_delay:
            self.fade -= (self.fade_percentage_per_second * dt * 255)
            self.image.set_alpha(self.fade)

    def decelerate(self, dt):
        self.velocity += self.deceleration * dt

    def update(self, dt):
        self.check_fade()
        self.fade_out(dt)

        if self.deceleration:
            self.decelerate(dt)

        self.rect.center += self.velocity * dt


class ParticleEmitter(pygame.sprite.Sprite):
    def __init__(self, groups, pos, spawn_region_dimensions, size_range, colours, angle_range_radians, speed_range, frequency,
                 deceleration=None, percentage_fade_per_second=0.5, emitting_type='loop'):
        # setup
        super().__init__(groups)
        self.image = pygame.Surface(size_range, pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.spawn_region_dimensions = spawn_region_dimensions
        self.size_range = size_range
        self.colours = colours
        self.angle_range_radians = angle_range_radians
        self.speed_range = speed_range
        self.frequency = frequency
        self.deceleration = deceleration
        self.percentage_fade_per_second = percentage_fade_per_second
        self.emitting_type = emitting_type

        # spawning
        self.emit = False
        self.particle_spawn_cooldown = None
        self.last_particle_spawn_time = 0

        self.rotation_degrees = 0

        # methods
        self.set_particle_spawn_cooldown()

    def set_particle_spawn_cooldown(self):
        self.emit = self.frequency

        if self.frequency:
            self.particle_spawn_cooldown = 1 / self.frequency

    def check_spawn_particle(self, dt):
        if (pygame.time.get_ticks() - self.last_particle_spawn_time) > self.particle_spawn_cooldown and self.emit:
            for particle in range(1 + math.floor(dt / self.particle_spawn_cooldown)):
                self.spawn_particle()
            self.last_particle_spawn_time = pygame.time.get_ticks()

    def emit_particle_burst(self):
        for particle in range(self.frequency):
            self.spawn_particle()

        self.emit = False

    def spawn_particle(self):
        size = random.randint(self.size_range[0], self.size_range[1])

        if self.spawn_region_dimensions == (0, 0):
            rel_pos = (0, 0)
        else:
            rel_pos = (random.randint(-self.spawn_region_dimensions[0] // 2, self.spawn_region_dimensions[0] // 2),
                       random.randint(-self.spawn_region_dimensions[1] // 2, self.spawn_region_dimensions[1] // 2))

        rot_pos = pygame.math.Vector2(rel_pos).rotate(self.rotation_degrees)
        abs_pos = (self.rect.centerx + rot_pos.x, self.rect.centery + rot_pos.y)
        colour = random.choice(self.colours)
        angle = self.angle_range_radians[0] if len(set(self.angle_range_radians)) == 1 else random.uniform(self.angle_range_radians[0], self.angle_range_radians[1])
        speed = self.speed_range[0] if len(set(self.speed_range)) == 1 else random.uniform(self.speed_range[0], self.speed_range[1])
        velocity = pygame.math.Vector2(speed * math.cos(angle), speed * math.sin(angle)).rotate(self.rotation_degrees)

        Particle(self.groups(), (size, size), abs_pos, colour, velocity, deceleration=self.deceleration,
                 fade_percentage_per_second=self.percentage_fade_per_second)

    def update(self, dt):
        if self.emit:
            if self.emitting_type == 'loop':
                self.check_spawn_particle(dt)
            elif self.emitting_type == 'burst':
                self.emit_particle_burst()

        # attributes
        if self.emitting_type == 'loop':
            self.set_particle_spawn_cooldown()