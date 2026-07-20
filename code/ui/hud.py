from ui.merchant_island import *
from ui.inventory import *


class HUD:
    def __init__(self, main_island_pos, player_ship):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.player_ship = player_ship

        # groups
        self.hud_sprites = pygame.sprite.Group()
        self.particle_sprites = pygame.sprite.Group()
        self.reload_bars = pygame.sprite.Group()
        self.message_sprites = pygame.sprite.Group()

        # compass
        self.main_island_pos = main_island_pos
        self.player_ship = player_ship
        self.compass = None

        # bars
        self.cannonball_bar = None

        self.last_port_cannon_can_fire_state = False
        self.last_starboard_cannon_can_fire_state = False

        self.port_reload_bar = None
        self.starboard_reload_bar = None
        self.health_bar = None

        self.fishing_bar_image = pygame.image.load('graphics/ui/bars/fishing_bar.png').convert_alpha()
        self.fishing_bar = None

        self.text_box_sub_surfs = self.create_text_box_sub_surfs()
        self.create_hud_elements()

        # docking
        self.dock_text_box = None

        # fishing
        self.casting_text_box = None

        # ui  pages
        self.large_ui_background = pygame.image.load('graphics/ui/backgrounds/large_ui_background.png').convert_alpha()
        self.item_card_image = pygame.image.load('graphics/ui/item_card.png').convert_alpha()

        # merchant islands
        self.display_merchant_island_ui = False

        self.merchant_island_backend = None
        self.merchant_island_frontend = None

        # inventory
        self.inventory = None
        self.display_inventory = False

        # messages
        self.new_messages = []

    def create_text_box_sub_surfs(self):
        sub_surfs_dict = {}

        for surf in os.listdir('graphics/ui/text_boxes'):
            sub_surfs = []
            name = surf.split('_')[0]

            text_box_surf = pygame.image.load('graphics/ui/text_boxes'+f'/{surf}').convert_alpha()

            width = text_box_surf.get_width() // 3
            height = text_box_surf.get_height() // 3

            for y in range(3):
                for x in range(3):
                    sub_surf = text_box_surf.subsurface(width * x, width * y, width, height)
                    sub_surfs.append(sub_surf)

            sub_surfs_dict[name] = sub_surfs

        return sub_surfs_dict

    def create_hud_elements(self):
        # images
        compass_image = pygame.image.load('graphics/ui/compass.png').convert_alpha()
        cannonball_bar_image = pygame.image.load('graphics/ui/bars/cannonball_bar.png').convert_alpha()

        # compass
        self.compass = Compass(self.hud_sprites, compass_image, (WINDOW_WIDTH - 75, 75), self.main_island_pos, self.player_ship)

        # bars
        y_pos = 45
        spacing = 30

        self.cannonball_bar = CountBar(self.hud_sprites, cannonball_bar_image, (120, y_pos),
                                       'Cannonballs', (250, 250, 250), self.player_ship.inventory.cannonballs)
        y_pos = self.cannonball_bar.rect.bottom + spacing
        self.port_reload_bar = ReloadBar((self.hud_sprites, self.reload_bars), (200, 30),
                                         (120, y_pos), 3000, 'Port')
        y_pos = self.port_reload_bar.rect.bottom + spacing
        self.starboard_reload_bar = ReloadBar((self.hud_sprites, self.reload_bars), (200, 30),
                                              (120, y_pos), 3000, 'Starboard')
        y_pos = self.starboard_reload_bar.rect.bottom + spacing
        self.health_bar = HealthBar(self.hud_sprites, (200, 30),(120, y_pos), self.player_ship)

    def check_reloading(self):
        if self.player_ship.inventory.cannonballs > 0:
            if not self.player_ship.can_fire_cannon[PORT] and self.last_port_cannon_can_fire_state:
                self.port_reload_bar.start_reload()
            if not self.player_ship.can_fire_cannon[STARBOARD] and self.last_starboard_cannon_can_fire_state:
                self.starboard_reload_bar.start_reload()
        else:
            self.port_reload_bar.empty = True
            self.starboard_reload_bar.empty = True

        self.last_port_cannon_can_fire_state = self.player_ship.can_fire_cannon[PORT]
        self.last_starboard_cannon_can_fire_state = self.player_ship.can_fire_cannon[STARBOARD]

    def check_fish_hooked(self):
        if self.player_ship.fishing_rod and self.player_ship.fishing_rod.hooked_fish:
            if not self.fishing_bar:
                self.fishing_bar = FishingBar(self.hud_sprites, self.fishing_bar_image, (WINDOW_WIDTH//2, WINDOW_HEIGHT-50),
                                              self.player_ship.fishing_rod.hooked_fish)
        elif self.fishing_bar:
            if self.fishing_bar.fish_caught:
                fish_rarity_colour = RARITY_COLOURS[self.fishing_bar.fish.rarity ]
                fish_name = self.fishing_bar.fish.name
                self.new_messages.append({'text': f" You caught a| {fish_name}!", 'colours': (TEXT_BOX_BLACK, fish_rarity_colour)})

            self.fishing_bar.delete()
            self.fishing_bar = None

    def display_cannon_ball_text(self):
        self.cannonball_bar.set_count(self.player_ship.inventory.cannonballs)

    def display_docking_text(self):
        if self.player_ship.can_dock and not (self.dock_text_box and self.dock_text_box.alive()):
            self.dock_text_box = TextBox(self.hud_sprites, (WINDOW_WIDTH//2, WINDOW_HEIGHT-40),
                                         self.text_box_sub_surfs['scroll'], 'Press "T" to dock')
        elif not self.player_ship.can_dock and self.dock_text_box and not self.dock_text_box.delete_animation_playing:
            self.dock_text_box.delete()
            self.dock_text_box = None

    def display_casting_text(self):
        if self.player_ship.fishing and not self.player_ship.casting and not self.casting_text_box:
            self.casting_text_box = TextBox(self.hud_sprites, (WINDOW_WIDTH//2, WINDOW_HEIGHT-40),
                                            self.text_box_sub_surfs['scroll'], 'Press "C" to cast')
        elif ((not self.player_ship.fishing or self.player_ship.casting)and self.casting_text_box
              and not self.casting_text_box.delete_animation_playing):
            self.casting_text_box.delete()
            self.casting_text_box = None

    def create_new_messages(self):
        for new_message in self.new_messages:
            new_message_sprite = TextMessage(self.hud_sprites, (20, WINDOW_HEIGHT-20),
                                             new_message['text'], new_message['colours'])

            for message in self.message_sprites:
                message.rect.centery -= new_message_sprite.rect.height + 5

            self.message_sprites.add(new_message_sprite)

        self.new_messages.clear()

    def check_display_merchant_island_ui(self):
        if self.merchant_island_frontend:
            if not (self.player_ship.docked and self.merchant_island_frontend.current_page.alive()):
                if self.merchant_island_frontend.current_page.alive():
                    self.merchant_island_frontend.current_page.delete()

                if not self.hud_sprites:
                    self.create_hud_elements()

                if not self.merchant_island_frontend.current_page.delete_animation_playing:
                    self.display_merchant_island_ui = False

                    self.merchant_island_backend = None
                    self.merchant_island_frontend = None

                self.player_ship.docked = False
            else:
                self.display_merchant_island_ui = True
        elif self.player_ship.docked:
                for sprite in self.hud_sprites:
                    sprite.delete()

                self.merchant_island_backend = MerchantIslandBackend(self.player_ship.port_docked_at,
                                                                     self.player_ship.inventory,
                                                                     self.player_ship.validate_purchase)
                self.merchant_island_frontend = MerchantIslandFrontend(self.hud_sprites, self.large_ui_background,
                                                                 self.text_box_sub_surfs, self.merchant_island_backend)

    def check_display_inventory(self):
        if self.inventory:
            if not self.player_ship.inventory_open or not self.inventory.alive():
                if self.inventory.alive():
                    self.inventory.delete()

                if not self.hud_sprites:
                    self.create_hud_elements()

                if not self.inventory.delete_animation_playing:
                    self.display_inventory = False
                    self.inventory = None

                self.player_ship.inventory_open = False
            else:
                self.display_inventory = True
        elif self.player_ship.inventory_open:
            for sprite in self.hud_sprites:
                sprite.delete()
            self.inventory = InventoryUI(self.hud_sprites, self.large_ui_background,
                                               (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
                                               self.text_box_sub_surfs, self.player_ship.inventory)

    def update(self, dt):
        self.check_fish_hooked()
        self.check_reloading()
        self.check_display_merchant_island_ui()
        self.check_display_inventory()
        self.create_new_messages()

        self.hud_sprites.update(dt)

    def draw(self):
        self.hud_sprites.draw(self.display_surface)

        if self.display_merchant_island_ui:
            self.merchant_island_frontend.current_page.draw(self.display_surface)
        elif self.display_inventory:
            self.inventory.draw(self.display_surface)
        else:
            self.compass.draw_needle()

            for reload_bar in self.reload_bars:
                reload_bar.display_reload()

            self.display_cannon_ball_text()
            self.display_docking_text()
            self.display_casting_text()

            self.health_bar.display_health()