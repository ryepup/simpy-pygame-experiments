from functools import wraps
import pygame
import simpy
from simpy.rt import RealtimeEnvironment
from math import floor


def trace(env, pre_step, post_step):
    def get_wrapper(step, pre_step, post_step):
        @wraps(step)
        def tracing_step():
            head_event = None
            if len(env._queue):
                head_event = env._queue[0]

            pre_step()
            result = step()
            post_step(head_event)
            return result
        return tracing_step

    env.step = get_wrapper(env.step, pre_step, post_step)


def after(fn, post):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        post()
        return result
    return wrapper


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


class PyGameMonitor(object):

    def __init__(self, env, on_close, screen):
        self.env = env
        self.on_close = on_close
        self.screen = screen

    def pre_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_close()

    def post_step(self, head_event):
        txt = 'T: %s' % (self.env.now,)
        pygame.display.set_caption(txt)
        pygame.display.flip()


class DrawableContainer(simpy.Container):

    def __init__(self, screen, color, center, *args, **kwargs):
        self.base = super(DrawableContainer, self)
        self.base.__init__(*args, **kwargs)
        self.color = color
        self.center = center
        self.screen = screen
        self.get = after(self.get, self.draw)
        self.put = after(self.put, self.draw)

    def draw(self):
        pygame.draw.circle(self.screen, BLACK, self.center, 20, 0)
        pct = self.level / float(self.capacity)
        pygame.draw.circle(self.screen, self.color,
                           self.center, int(20 * pct), 0)


class Generator(object):

    def __init__(self, env, screen, color, center, tank, battery):
        self.screen = screen
        self.center = center
        self.tank = tank
        self.battery = battery
        self.env = env
        self.color = color

    def run(self):
        self.draw()
        while True:
            if self.battery.level < self.battery.capacity / 3:
                self.draw(on=True)
                yield self.tank.get(1)
                yield self.env.timeout(120)
                self.draw(on=False)
                yield self.battery.put(400)

            yield self.env.timeout(20)

    def draw(self, on=False):
        color = dim_color(self.color, 1 if on else 0.25)

        pygame.draw.line(self.screen, color, self.center,
                         self.battery.center, 2)
        pygame.draw.line(self.screen, color, self.center, self.tank.center, 2)
        pygame.draw.circle(self.screen, color, self.center, 20, 0)


class Radio(object):

    def __init__(self, env, screen, color, center, battery):
        self.screen = screen
        self.center = center
        self.battery = battery
        self.env = env
        self.color = color

    def run(self):
        self.draw()
        while True:
            power = battery.get(10)
            result = yield power | self.env.timeout(2)
            if power not in result:
                self.draw(on=False)
                yield power

            bolt = Lightning(self.env, self.screen,
                             self.center, self.battery.center)
            self.env.process(bolt.run())

            self.draw(on=True)
            yield self.env.timeout(20)

    def draw(self, on=False):
        color = dim_color(self.color, 1 if on else 0.25)

#        pygame.draw.line(self.screen, color, self.center,
#                         self.battery.center, 2)
        pygame.draw.circle(self.screen, color, self.center, 20, 0)


class Lightning(object):

    def __init__(self, env, screen, source, dest):
        self.screen = screen
        self.source = source
        self.dest = dest
        self.env = env
        self.color = BLUE

    def run(self):
        print('firing lightning')
        for i in xrange(0, 10):
            self.draw()
            yield self.env.timeout(0.5)

    def draw(self):
        pygame.draw.lines(self.screen, self.color, True,
                          [self.source, self.dest], 3)

pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)

env = RealtimeEnvironment(factor=0.01, strict=False)
on_closed = env.event()
fuel = DrawableContainer(screen, RED, (20, 20), env, init=1000, capacity=1000)
battery = DrawableContainer(screen, BLUE, (20, 80),
                            env, init=500, capacity=1000)
generator = Generator(env, screen, GREEN, (80, 80), fuel, battery)
radio = Radio(env, screen, YELLOW, (20, 160), battery)

for x in [generator, radio]:
    env.process(x.run())

monitor = PyGameMonitor(env, on_closed.succeed, screen)
trace(env, monitor.pre_step, monitor.post_step)

screen.fill(BLACK)
for x in [fuel, battery]:
    x.draw()

env.run(until=on_closed)
