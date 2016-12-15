import simpy
from functools import wraps

class ShipPart(object):
    '''
    Base class for parts of the ship
    '''

    def __init__(self, env, ship):
        self.env = env
        self.ship = ship

    def timeout(self, wait):
        return self.env.timeout(wait)

    def run(self):
        try:
            while True:
                for x in self.tick():
                    yield x
        except simpy.Interrupt:
            pass


class Lifesupport(ShipPart):
    '''
    Keeps crew alive
    '''

    def __init__(self, env, ship):
        super(Lifesupport, self).__init__(env, ship)

    def tick(self):
        if self.ship.battery.level < 10:
            print('Lifesupport down for too long!')
            self.ship.dead.succeed()

        yield self.ship.battery.get(10)
        yield self.timeout(20)


class Reactor(ShipPart):
    '''
    Consumes fuel to provide electricy
    '''

    def __init__(self, env, ship):
        super(Reactor, self).__init__(env, ship)

    def tick(self):
        if self.ship.battery.level < self.ship.battery.capacity / 2:
            yield self.ship.fuel_tank.get(1)
            yield self.timeout(100)
            yield self.ship.battery.put(100)

        yield self.timeout(20)


class Ship(object):
    '''
    holds everything
    '''

    def __init__(self, env, name):
        self.env = env
        self.name = name

        self.battery = simpy.Container(env, init=600, capacity=1000)
        self.fuel_tank = simpy.Container(env, init=500, capacity=1000)

        self.crew = simpy.Container(env, init=20, capacity=50)
        self.computation = simpy.Container(env, init=20, capacity=1000)

        self.dead = env.event()

        self.reactor = env.process(Reactor(env, self).run())
        self.lifesupport = env.process(Lifesupport(env, self).run())

        env.process(self.run())

    def run(self):
        dead = yield self.dead
        self.lifesupport.interrupt('dead')
        self.reactor.interrupt('dead')
        print('[%s:%s] is dead!' % (self.name, env.now))

env = simpy.Environment()
ships = [Ship(env, name) for name in ['enterprise', 'hood']]
env.run(until=1000000)
