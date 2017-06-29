from . import view
from . import window

push = view.push


class Scene(view.View):
    """A view that takes up the entire window content area."""

    def __init__(self):
        view.View.__init__(self, window.rect)

    def key_down(self, key, code):
        import pygame

        if key == pygame.K_ESCAPE:
            view.pop()

    def exited(self):
        pass

    def entered(self):
        self.stylize()
