from settings import *

from collections import Counter
from formulas import *
from ui import *
from items import *


class MerchantIslandBackend:
    def __init__(self, island_name, player_inventory, validate_purchase_callback):
        # setup
        self.island_name = island_name
        self.player_inventory = player_inventory
        self.current_page_name = 'selling'
        self.current_page = None

        # callbacks
        self.validate_purchase_callback = validate_purchase_callback

        # selling - items sold to the player
        self.proposed_purchase = {}
        self.selling_items = {}
        self.read_selling_items()

        # buying - items sold by the player
        self.buying_items = {}
        self.load_buying_items()

    def generate_selling_items(self):
        possible_items_list = []
        chosen_items_list = []
        selling_items_list = []

        with open('settings/selling_items.txt', 'r') as file:
            dict_rows = list(csv.DictReader(file, delimiter=','))

            for row in dict_rows:
                id = row['id']
                name = row['name']
                image = pygame.image.load(f'graphics/items/{name.replace(' ', '_')}.png').convert_alpha()
                rarity = row['rarity']
                price = int(row['price'])
                description = row['description']

                possible_items_list.append(Item(id, name, image, rarity, price, description))

        for i in range(random.randint(3, 5)):
            choice = random.choice(possible_items_list)
            chosen_items_list.append(choice)
            possible_items_list.remove(choice)

        for item in chosen_items_list:
            stock = random.randint(0, 10)
            selling_items_list.extend(item for _ in range(stock))

        return selling_items_list

    def read_selling_items(self): # from a csv file
        selling_items_list = []
        file_path = f'data/{self.island_name.lower().replace(' ', '_')}_selling_items.csv'

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                dict_rows = list(csv.DictReader(file, delimiter=','))

                for row in dict_rows:
                    id = row['id']
                    name = row['name']
                    image = pygame.image.load(f'graphics/items/{name.replace(' ', '_')}.png').convert_alpha()
                    rarity = row['rarity']
                    price = int(row['price'])
                    stock = int(row['stock'])
                    description = row['description']

                    for i in range(stock):
                        selling_items_list.append(Item(id, name, image, rarity, price, description))
        else:
            selling_items_list = self.generate_selling_items()

        self.selling_items = Counter(selling_items_list)

    def write_selling_items(self): # to a csv file
        headers = ['id', 'name', 'rarity', 'price', 'stock', 'description']
        data = []

        for (item, stock) in self.selling_items.items():
            data_list = [item.id, item.name, item.rarity, item.price, stock, item.description]
            data.append(data_list)

        with open(f'data/{self.island_name.lower().replace(' ', '_')}_selling_items.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)

    def remove_selling_item(self, item):
        del self.selling_items[item]

    def remove_buying_item(self, item):
        del self.buying_items[item]

    def load_buying_items(self): # from player inventory
        for item in self.player_inventory.items:
            self.buying_items[item] = 1

    def validate_purchase(self, item, amount):
        cost = item.price * amount

        if cost <= self.player_inventory.doubloons:
            return True
        else:
            return False

    # callbacks
    def item_bought(self, item, amount):
        result = self.validate_purchase(item, amount)

        if result:
            for i in range(amount):
                self.player_inventory.add_item(item)

            self.player_inventory.doubloons -= item.price * amount
            self.selling_items[item] -= amount
            return True
        else:
            return False

    def item_sold(self, item, amount):
        for i in range(amount):
            self.player_inventory.remove_item(item)

        self.player_inventory.doubloons += item.price * amount
        self.buying_items[item] += amount

    def get_player_doubloons(self):
        return self.player_inventory.doubloons


class MerchantIslandFrontend:
    def __init__(self, hud_sprites, large_ui_background, text_box_sub_surfs, merchant_island_backend):
        # setup
        self.hud_sprites = hud_sprites
        self.large_ui_background = large_ui_background
        self.text_box_sub_surfs = text_box_sub_surfs
        self.merchant_island_backend = merchant_island_backend

        self.island_name = self.merchant_island_backend.island_name

        # pages
        self.current_page = MarketSellingPage(self.hud_sprites, copy.deepcopy(self.large_ui_background),
                                              (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), self.text_box_sub_surfs, self)
        self.current_page_name = None

    def change_page(self, new_page_name):
        self.current_page.set_play_animation(False)
        self.current_page.delete()
        self.current_page = None

        if new_page_name == 'selling' or new_page_name == 'market':
            self.current_page = MarketSellingPage(self.hud_sprites, copy.deepcopy(self.large_ui_background),
                                                  (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), self.text_box_sub_surfs,
                                                  self, play_animation=False)
        elif new_page_name == 'buying':
            self.current_page = MarketBuyingPage(self.hud_sprites, copy.deepcopy(self.large_ui_background),
                                                 (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), self.text_box_sub_surfs,
                                                 self, play_animation=False)
        elif new_page_name == 'port':
            self.current_page = PortPage(self.hud_sprites, copy.deepcopy(self.large_ui_background),
                                                 (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), self.text_box_sub_surfs,
                                                 self, play_animation=False)


    def get_selling_items(self):
        return self.merchant_island_backend.selling_items

    def get_buying_items(self):
        return self.merchant_island_backend.buying_items

    # callbacks
    def get_player_doubloons(self):
        return self.merchant_island_backend.get_player_doubloons()

    def remove_selling_item(self, item):
        self.merchant_island_backend.remove_selling_item(item)

    def remove_buying_item(self, item):
        self.merchant_island_backend.remove_buying_item(item)

    def button_pressed(self, button_name):
        if button_name != self.current_page_name:
            if button_name == 'exit':
                self.delete()
            else:
                self.change_page(button_name)

    def item_bought(self, item, amount):
        result = self.merchant_island_backend.item_bought(item, amount)

        if result:
            return True
        else:
            return False

    def item_sold(self, item, amount):
        self.merchant_island_backend.item_sold(item, amount)

    def delete(self):
        self.merchant_island_backend.write_selling_items()
        self.current_page.set_play_animation(True)
        self.current_page.delete()


class MarketPage(PageUIElement):
    def __init__(self, groups, image, pos, text_box_sub_surfs, merchant_island_frontend,
                 play_animation=True, animation_type='slide'):
        # setup
        super().__init__(groups, image, pos, text_box_sub_surfs, play_animation=play_animation, animation_type=animation_type)
        self.merchant_island_frontend = merchant_island_frontend

        # images
        self.market_button_image = pygame.image.load('graphics/ui/buttons/market_button.png').convert_alpha()
        self.port_button_image = pygame.image.load('graphics/ui/buttons/port_button.png').convert_alpha()
        self.doubloon_bar_image = pygame.image.load('graphics/ui/bars/doubloon_bar.png').convert_alpha()

        # buttons
        self.market_button = None
        self.port_button = None
        self.sell_page_button = None
        self.buy_page_button = None

        # bars
        self.doubloon_bar = None
        self.scroll_bar = None

        self.scroll_box = None

    def create_elements(self):
        # island name
        self.name = TextBox(self.ui_sprites, self.rect.midtop, self.text_box_sub_surfs['wood'],
                            self.merchant_island_frontend.island_name, play_animation=self.play_animation)

        # global buttons (present on all pages)
        button_gap = 25

        pos = (self.rect.right, self.init_target_y - self.rect.height // 2)
        self.exit_button = Button((self.ui_sprites, self.button_sprites), self.exit_button_image,
                                  pos, play_animation=self.play_animation)

        pos = (self.rect.left + self.market_button_image.width // 2 + 50, self.rect.bottom)
        self.market_button = Button((self.ui_sprites, self.button_sprites), self.market_button_image, pos,
                                    play_animation=self.play_animation)

        pos = (self.market_button.rect.right + self.port_button_image.width // 2 + button_gap, self.rect.bottom)
        self.port_button = Button((self.ui_sprites, self.button_sprites), self.port_button_image, pos,
                                  play_animation=self.play_animation)

        # local buttons (present on some pages)
        pos = (self.rect.right - self.button_image.width // 2 - 50, self.rect.midbottom[1])
        self.buy_page_button = TextButton((self.ui_sprites, self.button_sprites), copy.deepcopy(self.button_image),
                                          pos, 'Sell', play_animation=self.play_animation)

        pos = (self.buy_page_button.rect.left - self.button_image.width // 2 - button_gap, self.rect.midbottom[1])
        self.sell_page_button = TextButton((self.ui_sprites, self.button_sprites), copy.deepcopy(self.button_image),
                                           pos, 'Buy', play_animation=self.play_animation)

        # bars
        pos = (self.rect.centerx, self.rect.bottom)
        self.doubloon_bar = CountBar(self.ui_sprites, self.doubloon_bar_image, pos, None, TEXT_BOX_BLACK,
                                     self.merchant_island_frontend.get_player_doubloons(), play_animation=self.play_animation)

    def create_tiles(self):
        pass

    def update_elements(self):
        # bars
        self.doubloon_bar.set_count(self.merchant_island_frontend.get_player_doubloons())

    def check_buttons(self):
        if self.exit_button.pressed:
            self.merchant_island_frontend.button_pressed('exit')
        if self.market_button.pressed:
            self.merchant_island_frontend.button_pressed('market')
        if self.port_button.pressed:
            self.merchant_island_frontend.button_pressed('port')
        if self.buy_page_button.pressed:
            self.merchant_island_frontend.button_pressed('buying')
        if self.sell_page_button.pressed:
            self.merchant_island_frontend.button_pressed('selling')

        for tile in self.tile_sprites:
            if tile.pressed and tile != self.current_displayed_tile:
                if self.current_displayed_tile:
                    self.current_displayed_tile.unstick()

                self.create_item_card(tile)
                tile.stick()

    def create_item_card(self, tile):
        pass


class MarketSellingPage(MarketPage):
    def __init__(self, groups, image, pos, text_box_sub_surfs, merchant_island_frontend,
                 play_animation=True, animation_type='slide'):
        # setup
        super().__init__(groups, image, pos, text_box_sub_surfs, merchant_island_frontend,
                         play_animation=play_animation, animation_type=animation_type)
        # scroll box
        self.scroll_bar = None
        self.scroll_box = None

        # methods
        self.create_elements()
        self.stick_buttons()

    def create_elements(self):
        super().create_elements()

        # scroll box
        scroll_box_pos = self.rect.topleft + pygame.math.Vector2(20, 40)
        scroll_box_size = pygame.math.Vector2(500, self.rect.height-60)

        for index, (item, stock) in enumerate(self.merchant_island_frontend.get_selling_items().items()):
            ItemTile(self.tile_sprites, copy.deepcopy(self.item_tile_image), item, (0, 0), stock,
                     container_offset=scroll_box_pos)

        self.scroll_bar = ScrollBar(self.ui_sprites, (27 * 2, self.rect.height),
                                    (self.rect.left - 27 - 15, WINDOW_HEIGHT // 2), self.text_box_sub_surfs['wood'])

        self.scroll_box = ScrollBox(self.ui_sprites, scroll_box_pos, scroll_box_size, self.tile_sprites, self.scroll_bar,
                                    play_animation=self.play_animation)

    def stick_buttons(self):
        self.market_button.stick()
        self.sell_page_button.stick()

    def create_item_card(self, tile):
        if self.item_card:
            self.item_card.delete()
            self.item_card = None

        self.current_displayed_tile = tile
        self.item_card = SellItemCard(self.ui_sprites, copy.deepcopy(self.item_card_image), tile.item, tile.stock,
                                  (self.rect.right - 20 - (self.item_card_image.width // 2),
                                   self.rect.top + 50 + (self.item_card_image.height // 2)),
                                  self.text_box_sub_surfs['wood'], self.item_bought, self.out_of_stock)

    # callbacks
    def item_bought(self, item, amount):
        result = self.merchant_island_frontend.item_bought(item, amount)

        if result:
            self.update_elements()
            return True
        else:
            return False

    def out_of_stock(self):
        self.merchant_island_frontend.remove_selling_item(self.item_card.item)
        self.tile_sprites.remove(self.current_displayed_tile)

        self.current_displayed_tile.delete()
        self.item_card.delete()
        self.current_displayed_tile = None
        self.item_card = None
        self.update_elements()


class MarketBuyingPage(MarketPage):
    def __init__(self, groups, image, pos, text_box_sub_surfs, merchant_island_frontend,
                 play_animation=True, animation_type='slide'):
        # setup
        super().__init__(groups, image, pos, text_box_sub_surfs, merchant_island_frontend, play_animation=play_animation,
                         animation_type=animation_type)

        # scroll box
        self.scroll_box = None
        self.scroll_bar = None

        # methods
        self.create_elements()
        self.stick_buttons()

    def stick_buttons(self):
        self.market_button.stick()
        self.buy_page_button.stick()

    def create_elements(self):
        super().create_elements()

        # scroll box
        scroll_box_pos = self.rect.topleft + pygame.math.Vector2(20, 40)
        scroll_box_size = pygame.math.Vector2(500, self.rect.height-60)

        for index, (item, stock) in enumerate(self.merchant_island_frontend.get_buying_items().items()):
            ItemTile(self.tile_sprites, copy.deepcopy(self.item_tile_image), item, (0, 0), stock,
                     container_offset=scroll_box_pos)

        self.scroll_bar = ScrollBar(self.ui_sprites, (27 * 2, self.rect.height),
                                    (self.rect.left - 27 - 15, WINDOW_HEIGHT // 2), self.text_box_sub_surfs['wood'])

        self.scroll_box = ScrollBox(self.ui_sprites, scroll_box_pos, scroll_box_size, self.tile_sprites, self.scroll_bar,
                                    play_animation=self.play_animation)

    def create_item_card(self, tile):
        if self.item_card:
            self.item_card.delete()
            self.item_card = None

        self.current_displayed_tile = tile
        self.item_card = BuyItemCard(self.ui_sprites, copy.deepcopy(self.item_card_image), tile.item, tile.stock,
                                  (self.rect.right - 20 - (self.item_card_image.width // 2),
                                   self.rect.top + 50 + (self.item_card_image.height // 2)), self.text_box_sub_surfs['wood'],
                                     self.item_sold, self.out_of_stock)

    # callbacks
    def item_sold(self, item, amount):
        self.merchant_island_frontend.item_sold(item, amount)
        self.update_elements()

    def out_of_stock(self):
        self.merchant_island_frontend.remove_buying_item(self.item_card.item)
        self.tile_sprites.remove(self.current_displayed_tile)

        self.current_displayed_tile.delete()
        self.item_card.delete()
        self.current_displayed_tile = None
        self.item_card = None
        self.update_elements()


class PortPage(PageUIElement):
    def __init__(self, groups, image, pos, text_box_sub_surfs, merchant_island_frontend,
                 play_animation=True, animation_type='slide'):
        # setup
        super().__init__(groups, image, pos, text_box_sub_surfs, play_animation=play_animation, animation_type=animation_type)
        self.merchant_island_frontend = merchant_island_frontend

        # ui elements
        self.market_button_image = pygame.image.load('graphics/ui/buttons/market_button.png').convert_alpha()
        self.port_button_image = pygame.image.load('graphics/ui/buttons/port_button.png').convert_alpha()

        self.market_button = None
        self.port_button = None
        self.boat_page_button = None
        self.rod_page_button = None

        self.tile_positions = []

        # methods
        self.create_elements()
        self.create_tiles()
        self.stick_buttons()

    def create_tiles(self):
        pass

    def stick_buttons(self):
        self.port_button.stick()

    def create_elements(self):
        # island name
        self.name = TextBox(self.ui_sprites, self.rect.midtop, self.text_box_sub_surfs['wood'],
                            self.merchant_island_frontend.island_name, play_animation=self.play_animation)

        # global buttons (present on all pages)
        button_gap = 25

        pos = (self.rect.right, self.init_target_y - self.rect.height // 2)
        self.exit_button = Button((self.ui_sprites, self.button_sprites), self.exit_button_image,
                                  pos, play_animation=self.play_animation)

        pos = (self.rect.left + self.market_button_image.width // 2 + 50, self.rect.bottom)
        self.market_button = Button((self.ui_sprites, self.button_sprites), self.market_button_image, pos,
                                    play_animation=self.play_animation)

        pos = (self.market_button.rect.right + self.port_button_image.width // 2 + button_gap, self.rect.bottom)
        self.port_button = Button((self.ui_sprites, self.button_sprites), self.port_button_image, pos,
                                  play_animation=self.play_animation)

        # local buttons (present on some pages)
        pos = (self.rect.right - self.button_image.width // 2 - 50, self.rect.midbottom[1])
        self.rod_page_button = TextButton((self.ui_sprites, self.button_sprites), copy.deepcopy(self.button_image),
                                          pos, 'Boat', play_animation=self.play_animation)

        pos = (self.rod_page_button.rect.left - self.button_image.width // 2 - button_gap, self.rect.midbottom[1])
        self.boat_page_button = TextButton((self.ui_sprites, self.button_sprites), copy.deepcopy(self.button_image),
                                           pos, 'Rod', play_animation=self.play_animation)

    def check_buttons(self):
        if self.exit_button.pressed:
            self.merchant_island_frontend.button_pressed('exit')
        if self.market_button.pressed:
            self.merchant_island_frontend.button_pressed('market')
        if self.port_button.pressed:
            self.merchant_island_frontend.button_pressed('port')

        for tile in self.tile_sprites:
            if tile.pressed and tile != self.current_displayed_tile:
                self.create_item_card(tile)
                self.current_displayed_tile.unstick()
                tile.stick()
