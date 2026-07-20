from settings import *


class Item:
    def __init__(self, id, name, image, rarity, price, description):
        # setup
        self.id = id
        self.name = name
        self.image = image
        self.rarity = rarity
        self.price = price
        self.description = description

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Fish(Item):
    def __init__(self, id, name, image, rarity, price, description, weight, golden):
        # setup
        super().__init__(id, name, image, rarity, price, description)
        self.weight = weight
        self.golden = golden

    def __eq__(self, other):
        return False

    def __hash__(self):
        return hash(self.id)