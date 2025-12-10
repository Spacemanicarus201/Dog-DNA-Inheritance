import pygame
from ui.button import Button
from ui.search_table import SearchTable
from screens.trait_selection import TraitSelection
from screens.dog_model_test import DogModelTest
from breed_data import BREEDS


class MainMenu:
    def __init__(self, app):
        self.app = app

        # Fonts
        self.font_title = pygame.font.SysFont(None, 42)
        self.font_normal = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 24)

        # Breed list (imported from breed_data.py)
        self.breeds = BREEDS

        self.father = None
        self.mother = None

        # Search tables for breed selection
        self.father_table = None
        self.mother_table = None

        # NEXT BUTTON
        self.next_button = Button(
            (self.app.WIDTH // 2 - 75, self.app.HEIGHT - 80, 150, 50),
            "Next",
            self.font_normal,
            self.go_next
        )

        # DOG MODEL TEST BUTTON (new)
        self.test_button = Button(
            (20, self.app.HEIGHT - 80, 220, 50),
            "Test Dog Model",
            self.font_normal,
            self.go_test_model
        )

        # Create initial layout
        self.resize(self.app.WIDTH, self.app.HEIGHT)

    # ---------------------------------------------------------
    # RESIZE EVERYTHING WHEN WINDOW CHANGES
    # ---------------------------------------------------------
    def resize(self, w, h):
        # Calculate layout for two-column search tables
        padding = 20
        top_margin = 160
        bottom_margin = 100
        
        table_width = (w - 3 * padding) // 2
        table_height = h - top_margin - bottom_margin
        
        # Father table (left side)
        self.father_table = SearchTable(
            rect=(padding, top_margin, table_width, table_height),
            items=self.breeds,
            font=self.font_small,
            on_select_callback=self.set_father,
            color=(100, 150, 255)
        )
        
        # Mother table (right side)
        self.mother_table = SearchTable(
            rect=(2 * padding + table_width, top_margin, table_width, table_height),
            items=self.breeds,
            font=self.font_small,
            on_select_callback=self.set_mother,
            color=(255, 120, 150)
        )

        # Next button re-center
        self.next_button.rect.x = w // 2 - 75
        self.next_button.rect.y = h - 80

        # Test model button
        self.test_button.rect.x = 20
        self.test_button.rect.y = h - 80

    # ---------------------------------------------------------
    # BREED SETTERS
    # ---------------------------------------------------------
    def set_father(self, breed):
        self.father = breed

    def set_mother(self, breed):
        self.mother = breed

    # ---------------------------------------------------------
    # NEXT (GO TO TRAIT SELECTION)
    # ---------------------------------------------------------
    def go_next(self):
        if self.father and self.mother:
            self.app.change_screen(
                lambda app: TraitSelection(app, self.father, self.mother)
            )

    # ---------------------------------------------------------
    # GO TO 3D DOG MODEL TEST SCREEN
    # ---------------------------------------------------------
    def go_test_model(self):
        self.app.change_screen(DogModelTest)

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def handle_event(self, event):
        if self.father_table:
            self.father_table.handle_event(event)
        
        if self.mother_table:
            self.mother_table.handle_event(event)

        self.next_button.handle_event(event)
        self.test_button.handle_event(event)

    # ---------------------------------------------------------
    # DRAW EVERYTHING
    # ---------------------------------------------------------
    def draw(self, screen):
        screen.fill((25, 25, 25))

        # Title
        title = self.font_title.render("Choose Parent Breeds", True, (255, 255, 255))
        screen.blit(title, (self.app.WIDTH // 2 - title.get_width() // 2, 40))

        # Column headers with selected breeds
        father_header = self.font_normal.render(
            f"Father: {self.father if self.father else 'None'}",
            True, (200, 200, 255)
        )
        mother_header = self.font_normal.render(
            f"Mother: {self.mother if self.mother else 'None'}",
            True, (255, 200, 200)
        )

        screen.blit(father_header, (30, 100))
        screen.blit(mother_header, (self.app.WIDTH // 2 + 30, 100))

        # Draw search tables
        if self.father_table:
            self.father_table.draw(screen)
        
        if self.mother_table:
            self.mother_table.draw(screen)

        # Draw bottom buttons
        self.next_button.draw(screen)
        self.test_button.draw(screen)
