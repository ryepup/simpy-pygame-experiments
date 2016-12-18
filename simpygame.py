import pygame
from simpy.rt import RealtimeEnvironment

BLACK = pygame.Color(0, 0, 0)


class PyGameEnvironment(RealtimeEnvironment):

    def __init__(self, renderer, fps=30, *args, **kwargs):
        super(PyGameEnvironment, self).__init__(*args, **kwargs)

        self.on_pygame_quit = self.event()
        self.renderer = renderer

        self.ticks_per_frame = 1.0 / (self.factor * fps)

        self.process(self.render())

    def render(self):
        while True:
            if self.pygame_quit_requested():
                self.on_pygame_quit.succeed()

            self.renderer.render()

            yield self.timeout(self.ticks_per_frame)

    def pygame_quit_requested(self):
        quit_events = (e for e in pygame.event.get()
                       if e.type == pygame.QUIT)
        return any(quit_events)

    def run(self):
        super(PyGameEnvironment, self).run(until=self.on_pygame_quit)


class Renderer(object):

    def __init__(self, screen):
        self.screen = screen
        self.callbacks = []

    def render(self):
        self.screen.fill(BLACK)
        for draw in self.callbacks:
            draw(screen=self.screen)

        pygame.display.flip()

    def add(self, callable):
        self.callbacks.append(callable)
