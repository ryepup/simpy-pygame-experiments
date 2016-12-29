import pygame
import simpy
from simpygame.core import (PyGameEnvironment, FrameRenderer)


def dim_color(color, percent):
    h, s, v, a = color.hsva
    result = pygame.Color(color.r, color.g, color.b, color.a)
    result.hsva = (h, s, v * percent, a)
    return result


BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
YELLOW = pygame.Color(255, 255, 0)


class Generator(object):

    def __init__(self, env, color, center, tank, battery):
        self.center = center
        self.tank = tank
        self.battery = battery
        self.env = env
        self.color = color

        self.on = False

    def run(self):
        while True:
            if self.battery.level < self.battery.capacity / 3:
                self.on = True
                yield self.tank.get(10)
                for i in range(10):
                    yield self.env.timeout(12)
                    yield self.battery.put(40)

                self.on = False

            yield self.env.timeout(20)

    def __call__(self, screen):
        color = dim_color(self.color, 1 if self.on else 0.25)

        pygame.draw.line(screen, color, self.center,
                         self.battery.center, 2)
        pygame.draw.line(screen, color, self.center, self.tank.center, 2)
        pygame.draw.circle(screen, color, self.center, 20, 0)


class Radio(object):

    def __init__(self, env, color, center, battery):
        self.center = center
        self.battery = battery
        self.env = env
        self.color = color

        self.on = False

    def run(self):
        while True:
            power = battery.get(10)
            result = yield power | self.env.timeout(2)
            if power not in result:
                self.on = False
                yield power

#            bolt = Lightning(self.env, self.screen,
#                             self.center, self.battery.center)
#            self.env.process(bolt.run())

            self.on = True
            yield self.env.timeout(20)

    def __call__(self, screen):
        color = dim_color(self.color, 1 if self.on else 0.25)
        pygame.draw.circle(screen, color, self.center, 20, 0)


class Lightning(object):

    def __init__(self, env, screen, source, dest):
        self.screen = screen
        self.source = source
        self.dest = dest
        self.env = env
        self.color = BLUE

    def run(self):
        for i in range(0, 10):
            self.draw()
            yield self.env.timeout(0.5)

    def draw(self):
        pygame.draw.lines(self.screen, self.color, True,
                          [self.source, self.dest], 3)


class CircleContainerRenderer(object):

    def __init__(self, color, center, container):
        self.color = color
        self.center = center
        self.container = container

    def __call__(self, screen):
        pct = self.container.level / self.container.capacity
        pygame.draw.circle(screen, self.color, self.center, int(20 * pct), 0)


pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)
screen.fill(BLACK)

renderer = FrameRenderer(screen)

env = PyGameEnvironment(renderer, factor=0.001, strict=False)

fuel = simpy.Container(env, init=1000, capacity=1000)
fuel.center = (20, 20)
renderer.add(CircleContainerRenderer(RED, (20, 20), fuel))

battery = simpy.Container(env, init=500, capacity=1000)
battery.center = (20, 80)
renderer.add(CircleContainerRenderer(BLUE, (20, 80), battery))

generator = Generator(env, GREEN, (80, 80), fuel, battery)
radio = Radio(env, YELLOW, (20, 160), battery)


for x in [generator, radio]:
    renderer.add(x)
    env.process(x.run())

env.run()
