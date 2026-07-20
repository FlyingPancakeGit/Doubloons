from settings import *


class AudioManager:
    def __init__(self):
        # setup
        self.sound_effects = {}
        # methods
        self.load_sound_effects()

    def load_sound_effects(self):
        for root, dirs, files in os.walk('audio'):
            for file in files:
                if file.startswith('.'):
                    continue

                volume = 0.5
                file_path = os.path.join(root, file)
                file_name = file.split('.')[0]

                if file_name == 'background_music' or file_name == 'water_crashing':
                    volume = 0.2

                self.sound_effects[file_name] = pygame.mixer.Sound(file_path)
                self.sound_effects[file_name].set_volume(volume)

    def play(self, name, loop=False, fade=False):
        if name in self.sound_effects:
            self.sound_effects[name].play(-1 if loop else 0, fade_ms=1000 if fade else 0)
            return True
        else:
            return False

    def stop(self, name):
        if name in self.sound_effects:
            self.sound_effects[name].fadeout(2000)


audio_manager = AudioManager()