from settings import *


class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = -duration
        self.finished = True

    def start(self):
        self.finished = False
        self.start_time = pygame.time.get_ticks()

    def check_time(self):
        self.finished = pygame.time.get_ticks() - self.start_time > self.duration

    def update(self):
        self.check_time()
