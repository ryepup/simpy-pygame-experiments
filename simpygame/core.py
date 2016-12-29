import pygame
from simpy.rt import RealtimeEnvironment


class PyGameEnvironment(RealtimeEnvironment):
    """
    Customized version of ``simpy.rt.RealtimeEnvironment`` that attempts to
    maintain a steady framerate.

    :param renderer: what we use to draw the simulation
    :type renderer: :class:`~simpygame.core.Renderer`
    :param fps: intended frames per second
    :param args: other arguments passed blindly to ``simpy.rt.RealtimeEnvironment``
    :param kwargs: other arguments passed blindly to ``simpy.rt.RealtimeEnvironment``
    """

    def __init__(self, renderer, fps=30, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._on_pygame_quit = self.event()
        self._renderer = renderer
        self._ticks_per_frame = 1.0 / (self.factor * fps)

    def _render(self):
        while True:
            if self._pygame_quit_requested():
                self._on_pygame_quit.succeed()

            self._renderer.render()

            yield self.timeout(self._ticks_per_frame)

    def _pygame_quit_requested(self):
        quit_events = (e for e in pygame.event.get()
                       if e.type == pygame.QUIT)
        return any(quit_events)

    def run(self):
        """
        Runs the simulation until a ``pygame.QUIT`` event is received
        """
        self.process(self._render())
        super().run(until=self._on_pygame_quit)


class Renderer(object):
    """
    Renders the state of the simulation to a ``pygame`` display.

    :param screen: a ``pygame`` display that gets passed to every draw function added via :meth:`add`
    """

    def __init__(self, screen, fill_color=(0, 0, 0)):
        self._screen = screen
        self._callbacks = []
        self._fill_color = fill_color

    def render(self):
        """
        Fills the screen with black, then calls all draw functions, then updates
        the screen with ``pygame.display.flip``.
        """
        self._screen.fill(self._fill_color)
        for draw in self._callbacks:
            draw(screen=self._screen)

        pygame.display.flip()

    def add(self, callable):
        """
        add a draw function to be called on every frame
        """
        self._callbacks.append(callable)
