from settings import *

import opensimplex
import numpy as np
import random


class IslandGenerator:
    def __init__(self):
        self.island_width = 800
        self.island_height = 800
        self.scale_factor = 3

        self.noise_map = None
        self.noise_map_mask = None
        self.radial_fade_map = None
        self.surf = None

        self.create_noise_map_time = None
        self.add_radial_fade_time = None
        self.colour_island_time = None
        self.seed_set_time = None

        # merchant island
        self.port_pos = None

        self.create_radial_fade_map()

    def create_radial_fade_map(self):
        radial_fade_map = np.zeros((int(self.island_width), int(self.island_height)))
        center = pygame.math.Vector2(self.island_width / 2, self.island_height / 2)
        max_dist = min(center.x, center.y)

        for j, row in enumerate(radial_fade_map):
            for i, col in enumerate(row):
                if not (i >= self.island_width or j >= self.island_height):
                    dist = (center - pygame.math.Vector2(i, j)).magnitude()
                    fade = 1 - (dist / max_dist)
                    radial_fade_map[j, i] = fade

        self.radial_fade_map = radial_fade_map

    def create_noise_map(self):
        start_time = pygame.time.get_ticks()

        x = np.linspace(0, 4, self.island_width)
        y = np.linspace(0, 4, self.island_height)

        noise_map = opensimplex.noise2array(x, y)
        self.noise_map = (noise_map + 1) / 2

        self.noise_map_time = pygame.time.get_ticks() - start_time

    def add_radial_fade(self):
        start_time = pygame.time.get_ticks()

        self.noise_map = self.radial_fade_map * self.noise_map

        self.radial_fade_time = pygame.time.get_ticks() - start_time

    def colour_island(self):
        start_time = pygame.time.get_ticks()

        BORDER_SAND_array = np.array(BORDER_SAND, dtype=np.uint8).reshape(1, 1, 3)
        SAND_array = np.array(SAND, dtype=np.uint8).reshape(1, 1, 3)
        BORDER_GRASS_array = np.array(BORDER_GRASS, dtype=np.uint8).reshape(1, 1, 3)
        GRASS_array = np.array(GRASS, dtype=np.uint8).reshape(1, 1, 3)
        BLACK_array = np.array([0, 0, 0], dtype=np.uint8).reshape(1, 1, 3)

        nm_3d = self.noise_map[:, :, np.newaxis]
        nm_2d = self.noise_map[:, :]

        colour_map = np.select(
            condlist=[
                nm_3d <= 0.25,
                nm_3d < 0.27,
                nm_3d < 0.30,
                nm_3d < 0.32,
            ],
            choicelist=[
                BLACK_array,
                BORDER_SAND_array,
                SAND_array,
                BORDER_GRASS_array,
            ],
            default=GRASS_array,
        )
        alpha_map = np.select(
            condlist=[
                nm_2d <= 0.25,
                nm_2d > 0.25
            ],
            choicelist=[
                np.uint8(0),
                np.uint8(255)
            ],
            default=np.uint8(255)
        )

        pygame.surfarray.blit_array(self.surf, colour_map)
        alpha_view = pygame.surfarray.pixels_alpha(self.surf)
        alpha_view[:] = alpha_map
        del alpha_view

        self.colour_island_time = pygame.time.get_ticks() - start_time

    def create_noise_map_mask(self):
        set_mask = np.where(self.noise_map < 0.25, 0, 1)
        mask_surf = pygame.surfarray.make_surface(set_mask)
        mask_surf.set_colorkey((0, 0, 0))

        self.noise_map_mask = pygame.mask.from_surface(mask_surf)

    def determine_port_pos(self):
        successful = False
        max_dist = self.island_width

        while not successful:
            initial_vector = pygame.math.Vector2(self.island_width / 2, 0)
            rotation = random.randint(0, 360)
            rotated_vector = initial_vector.rotate(rotation)
            reducing_direction = (pygame.math.Vector2(self.island_width / 2, self.island_height / 2) - rotated_vector).normalize()

            collision_detected = False
            attempts = 0

            while not collision_detected:
                pos = pygame.math.Vector2(self.island_width / 2, self.island_height / 2) + rotated_vector

                try:
                    if self.noise_map_mask.get_at(pos):
                        collision_detected = True
                        successful = True
                        self.port_pos = pos
                    else:
                        rotated_vector += reducing_direction
                        attempts += 1
                except:
                    rotated_vector += reducing_direction
                    attempts += 1

                if attempts > max_dist:
                    break

    def determine_ship_spawn_pos(self, direction):
        return self.port_pos + direction * 100 + direction.rotate(90) * 100

    def determine_port_rotation(self, x, y):
        set_mask = np.where(self.noise_map < 0.25, 0, 1)
        average_vector = pygame.math.Vector2(0, 0)

        for dx in range(-5, 6):
            for dy in range(-5, 6):
                if (self.island_width < (x + dx) < 0) or (self.island_height < (y + dy) < 0):
                    break

                pixel = set_mask[int(x + dx), int(y + dy)]

                if pixel:
                    average_vector += pygame.math.Vector2(-dx, -dy)

        direction = average_vector.normalize() if average_vector else average_vector
        rotation = direction.angle_to(pygame.math.Vector2(0, 1))

        return rotation, direction

    def draw_port(self, rotation):
        port = pygame.image.load('graphics/islands/port.png').convert_alpha()
        rotated_port = pygame.transform.rotate(port, rotation)
        port_surf = pygame.Surface((self.island_width, self.island_height), pygame.SRCALPHA)

        nm_2d = self.noise_map[:, :]
        alpha_map = np.select(
            condlist=[
                nm_2d <= 0.25,
                nm_2d > 0.25
            ],
            choicelist=[
                np.uint8(0),
                np.uint8(255)
            ],
            default=np.uint8(255)
        )

        alpha_view = pygame.surfarray.pixels_alpha(port_surf)
        alpha_view[:] = alpha_map
        del alpha_view

        port_rect = rotated_port.get_rect(center=(self.port_pos[0], self.port_pos[1]))
        port_surf.blit(rotated_port, port_rect)
        port_surf.blit(self.surf, (0, 0))
        self.surf = port_surf

    def generate_island(self, size, island_type):
        start_time = pygame.time.get_ticks()

        opensimplex.seed(int(pygame.time.get_ticks()))

        self.seed_set_time = start_time - pygame.time.get_ticks()

        self.island_width = size
        self.island_height = size

        self.surf = pygame.Surface((self.island_width, self.island_height), pygame.SRCALPHA)
        self.create_radial_fade_map()
        self.create_noise_map()
        self.add_radial_fade()
        self.create_noise_map_mask()

        self.colour_island()

        if island_type == 'merchant':
            self.determine_port_pos()
            rotation, port_direction = self.determine_port_rotation(self.port_pos[0], self.port_pos[1])
            self.draw_port(rotation)

            data = {
                'image': self.surf,
                'port_pos': pygame.math.Vector2(self.port_pos) + pygame.math.Vector2(-600, -600) + port_direction * 100,
                'ship_spawn_pos': self.determine_ship_spawn_pos(port_direction) + pygame.math.Vector2(-600, -600),
                'ship_spawn_rotation': rotation
            }
        else:
            data = {
                'image': self.surf
            }

        return data

    def _print_times(self):
        print(f'Noise Map Generation: {self.noise_map_time}\n'
              f'Adding Radial Fade: {self.add_radial_fade_time}\n'
              f'Colouring Island: {self.colour_island_time}\n'
              f'Set New Seed: {self.seed_set_time}\n\n')