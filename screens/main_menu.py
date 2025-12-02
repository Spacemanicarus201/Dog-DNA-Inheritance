import pygame
from ui.button import Button
from screens.trait_selection import TraitSelection


class MainMenu:
    def __init__(self, app):
        self.app = app

        self.font_title = pygame.font.SysFont(None, 42)
        self.font_normal = pygame.font.SysFont(None, 30)

        # Added "Great Dane" and "Weimaraner" based on the new dataset
        self.breeds = [
            "Golden Retriever", "Husky", "German Shepherd",
            "Chihuahua", "Toy Poodle", "Dachshund",
            "Great Dane", "Weimaraner"
        ]

        self.father = None
        self.mother = None

        self.father_buttons = []
        self.mother_buttons = []

        self.next_button = Button(
            (self.app.WIDTH // 2 - 75, self.app.HEIGHT - 80, 150, 50),
            "Next",
            self.font_normal,
            self.go_next
        )

        self.resize(self.app.WIDTH, self.app.HEIGHT)

    # ---------------------------------------------------------
    # RESIZING UI
    # ---------------------------------------------------------
    def resize(self, w, h):
        self.father_buttons = []
        self.mother_buttons = []

        y = 180
        gap = 65

        for breed in self.breeds:
            # LEFT column (Father)
            self.father_buttons.append(
                Button((80, y, 260, 50), breed, self.font_normal,
                       lambda b=breed: self.set_father(b))
            )

            # RIGHT column (Mother)
            self.mother_buttons.append(
                Button((w - 340, y, 260, 50), breed, self.font_normal,
                       lambda b=breed: self.set_mother(b))
            )

            y += gap

        self.next_button.rect.x = w // 2 - 75
        self.next_button.rect.y = h - 80

    # ---------------------------------------------------------
    # SET SELECTED BREEDS
    # ---------------------------------------------------------
    def set_father(self, breed):
        self.father = breed

    def set_mother(self, breed):
        self.mother = breed

    # ---------------------------------------------------------
    # CONTINUE BUTTON
    # ---------------------------------------------------------
    def go_next(self):
        if self.father and self.mother:
            self.app.current_screen = TraitSelection(self.app, self.father, self.mother)

    # ---------------------------------------------------------
    # HANDLE EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        for b in self.father_buttons:
            b.handle_event(event)
        for b in self.mother_buttons:
            b.handle_event(event)
        self.next_button.handle_event(event)

    # ---------------------------------------------------------
    # DRAW UI
    # ---------------------------------------------------------
    def draw(self, screen):
        screen.fill((25, 25, 25))

        title = self.font_title.render("Choose Parent Breeds", True, (255, 255, 255))
        screen.blit(title, (self.app.WIDTH//2 - title.get_width()//2, 40))

        # Display selected choices
        father_label = self.font_normal.render(
            f"Father: {self.father if self.father else 'None'}",
            True, (200, 200, 255)
        )
        mother_label = self.font_normal.render(
            f"Mother: {self.mother if self.mother else 'None'}",
            True, (255, 200, 200)
        )

        screen.blit(father_label, (80, 120))
        screen.blit(mother_label, (self.app.WIDTH - 340, 120))

        # Draw selectable buttons with highlight
        for b in self.father_buttons:
            if b.text == self.father:
                pygame.draw.rect(screen, (80, 140, 250), b.rect, border_radius=12)
            b.draw(screen)

        for b in self.mother_buttons:
            if b.text == self.mother:
                pygame.draw.rect(screen, (250, 120, 120), b.rect, border_radius=12)
            b.draw(screen)

        self.next_button.draw(screen)