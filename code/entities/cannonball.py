from settings import *


class Cannonball(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos, velocity):
        # setup
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_frect(center=pos)

        # age
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1000
        self.should_kill = False

        # vectors
        self.velocity = velocity
        self.drag = pygame.math.Vector2()

        # particles
        self.cannonball_particle_emitter = None

    def emit_particle_burst(self):
        particle_emitter = ParticleEmitter(self.groups()[0], self.rect.center, (0, 0), (6, 8),
                                           [SEA_FOAM], (0, 2 * math.pi), (30, 30), 40, emitting_type='burst')
        particle_emitter.emit = True
        particle_emitter.update(0) # dt is not needed, as particle spawning only happens once in burst mode
        self.kill()

    def check_age(self):
        if pygame.time.get_ticks() - self.spawn_time > self.life_time:
            self.should_kill = True
            self.emit_particle_burst()

    def update(self, dt):
        self.check_age()

        self.rect.center += self.velocity * dt


class CannonFiringCommand:
    def __init__(self, side):
        self.side = side