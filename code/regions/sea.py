from settings import *

import opensimplex
from items import *


class Sea: # Used for fishing (e.g., holding loot tables, determining when a fish has been baited).
    def __init__(self):
        # setup
        self.catches = []
        self.fish_rarity_chances = {
            'common': 50,
            'uncommon': 27,
            'rare': 15,
            'epic': 6,
            'legendary': 2
        }

        # methods
        self.load_catches()

    def load_catches(self):
        with open('settings/fishes.txt', 'r') as file:
            dict_rows = list(csv.DictReader(file, delimiter=','))

            for row in dict_rows:
                name = row['name']
                image = pygame.image.load(f'graphics/fishes/{name}.png').convert_alpha()
                rarity = row['rarity']

                self.catches.append(Item(0, name, image, rarity, 0, 100))

    def get_bobbing_time(self):
        return 200#random.randint(1500, 5000)

    def get_catch(self, pos):
        num = random.randint(0, 100)
        catch_rarity = None

        cumulative_weight = 0
        for rarity, weight in self.fish_rarity_chances.items():
            cumulative_weight += weight
            if num <= cumulative_weight:
                catch_rarity = rarity
                break

        possible_catches = [possible_catch for possible_catch in self.catches if possible_catch.rarity == catch_rarity]
        catch = random.choice(possible_catches)
        weight = 10 * max(1, random.gauss(0, 1))
        golden = 1 == random.randint(0, 1000)
        price = 5 * RARITY_LOOKUP[catch.rarity] + 2 * weight

        return Fish(catch.id, catch.name, catch.image, catch.rarity, price,
                    f'A {weight}kg, {catch.rarity} {catch.name}.', weight, golden)

    def generate_hotspots(self):
        pass

    def update(self):
        pass