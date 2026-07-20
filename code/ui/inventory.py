from settings import *

from collections import Counter
from ui import *


class InventoryBackend:
    def __init__(self, player):
        # setup
        self.player = player
        self.items = {}
        self.max_item_count = 100

        self.doubloons = 100
        self.cannonballs = 0

        self.current_page = 'items'

    def remove_item(self, item):
        self.items[item] -= 1
        if self.items[item] <= 0:
            del self.items[item]

        self.update_stock()

    def update_stock(self):
        self.items = Counter(self.items)

    def add_item(self, item):
        if sum(self.items.values()) < self.max_item_count:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1
            return True

        else:
            return False

    def has_item(self, item):
        for check_item in self.items:
            if check_item == item:
                return True
        return False

class InventoryUI(PageUIElement):
    def __init__(self, groups, image, pos, text_box_sub_surfs, inventory_backend, play_animation=True):
        # setup
        super().__init__(groups, image, pos, text_box_sub_surfs, play_animation=play_animation)
        self.inventory_backend = inventory_backend

        # scroll box
        self.scroll_bar = None
        self.scroll_box = None

        # ui elements
        self.inventory_slot_image = pygame.image.load('graphics/ui/inventory_slot.png').convert_alpha()

        # methods
        self.create_elements()

    def create_elements(self):
        # name
        self.name = TextBox(self.ui_sprites, self.rect.midtop,
                            self.text_box_sub_surfs['wood'], 'Inventory')

        # buttons
        pos = (self.rect.right, self.init_target_y - self.rect.height // 2)
        self.exit_button = Button((self.ui_sprites, self.button_sprites), self.exit_button_image,
                                  pos, play_animation=True)

        # tile scroll box
        scroll_box_pos = self.rect.topleft + pygame.math.Vector2(20, 40)
        scroll_box_size = pygame.math.Vector2(500, self.rect.height - 120)

        limit = self.inventory_backend.max_item_count

        for index, (item, stock) in enumerate(self.inventory_backend.items.items()):
            ItemTile(self.tile_sprites, copy.deepcopy(self.item_tile_image), item, (0, 0), stock,
                     container_offset=scroll_box_pos)

        for slot in range(len(self.inventory_backend.items), limit):
            ItemTile(self.tile_sprites, copy.deepcopy(self.inventory_slot_image), None,(0, 0), 1,
                     container_offset=scroll_box_pos)

        # bars
        self.scroll_bar = ScrollBar(self.ui_sprites, (27*2, self.rect.height),
                                    (self.rect.left-27-15, WINDOW_HEIGHT//2), self.text_box_sub_surfs['wood'])

        self.scroll_box = ScrollBox(self.ui_sprites, scroll_box_pos, scroll_box_size, self.tile_sprites, self.scroll_bar)

    def update(self, dt):
        # animation
        if self.play_animation:
            if self.init_animation_playing:
                self.play_init_animation()
            elif self.delete_animation_playing:
                self.play_delete_animation()

        # methods
        self.check_buttons()
        self.ui_sprites.update(dt)