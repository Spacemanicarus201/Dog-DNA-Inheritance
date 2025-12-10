import pygame

BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
BUTTON_TEXT = (255, 255, 255)


class Button:
    def __init__(self, rect, text, font, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        label = self.font.render(self.text, True, BUTTON_TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                if self.callback:
                    self.callback()

    def update(self, mouse, pos):
        """Alternative update API used by some screens.

        mouse: result of `pygame.mouse.get_pressed()`
        pos: result of `pygame.mouse.get_pos()`

        Returns True if the button was pressed (left mouse) while hovered.
        If a callback is registered it will be invoked.
        """
        self.hovered = self.rect.collidepoint(pos)
        if mouse[0] and self.hovered:
            if self.callback:
                self.callback()
            return True
        return False
