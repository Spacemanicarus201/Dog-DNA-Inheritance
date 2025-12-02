import pygame

class Dropdown:
    """
    Two-pass dropdown:
      - draw() draws the collapsed box (first pass)
      - draw_open_menu(screen) draws the expanded options (second pass - call last)
    """
    def __init__(self, x, y, w, h, options, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options[:] if options else ["-"]
        self.selected = self.options[0]
        self.open = False
        self.font = font or pygame.font.SysFont(None, 20)

        self.item_h = h
        self.bg = (60, 60, 60)
        self.text = (255, 255, 255)
        self.hover_bg = (90, 90, 90)
        self.border = (40, 40, 40)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
            else:
                # if open and clicked on option -> select
                if self.open:
                    for i, option in enumerate(self.options):
                        item_rect = pygame.Rect(
                            self.rect.x,
                            self.rect.y + (i + 1) * self.item_h,
                            self.rect.width,
                            self.item_h
                        )
                        if item_rect.collidepoint(event.pos):
                            self.selected = option
                            break
                self.open = False

    def draw(self, screen):
        # collapsed box (first pass)
        pygame.draw.rect(screen, self.bg, self.rect)
        pygame.draw.rect(screen, self.border, self.rect, 2)
        txt = self.font.render(self.selected, True, self.text)
        screen.blit(txt, (self.rect.x + 8, self.rect.y + (self.rect.h - txt.get_height())//2))

        # draw small arrow
        arrow_x = self.rect.right - 18
        arrow_y = self.rect.y + self.rect.h//2
        pygame.draw.polygon(screen, self.text, [(arrow_x-6, arrow_y-4), (arrow_x+6, arrow_y-4), (arrow_x, arrow_y+4)])

    def draw_open_menu(self, screen):
        # MUST be called last, after all other UI draw calls
        if not self.open:
            return
        mouse = pygame.mouse.get_pos()
        for i, option in enumerate(self.options):
            item_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + (i + 1) * self.item_h,
                self.rect.width,
                self.item_h
            )
            color = self.hover_bg if item_rect.collidepoint(mouse) else self.bg
            pygame.draw.rect(screen, color, item_rect)
            pygame.draw.rect(screen, self.border, item_rect, 1)
            txt = self.font.render(option, True, self.text)
            screen.blit(txt, (item_rect.x + 8, item_rect.y + (item_rect.h - txt.get_height())//2))
