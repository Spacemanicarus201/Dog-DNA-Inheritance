import pygame
from logic.genetic_calculator import GeneticCalculator
from ui.button import Button


class GeneticSummary:
    def __init__(self, app,
                 father_readable, mother_readable,
                 father_defaults, mother_defaults,
                 father_overrides, mother_overrides):

        self.app = app

        # Fonts
        self.font_title = pygame.font.SysFont(None, 32)
        self.font_header = pygame.font.SysFont(None, 26)
        self.font_normal = pygame.font.SysFont(None, 20)
        self.font_small = pygame.font.SysFont(None, 18)
        self.font_tiny = pygame.font.SysFont(None, 16)

        # Store readable traits
        self.father_readable = father_readable
        self.mother_readable = mother_readable

        # Combine genotype info
        calc = GeneticCalculator()
        self.father_genes = calc.combine_defaults_with_overrides(father_defaults, father_overrides)
        self.mother_genes = calc.combine_defaults_with_overrides(mother_defaults, mother_overrides)

        # Run genetics
        self.punnett, self.monte_genos, self.monte_readables = calc.generate_summary(
            self.father_genes, self.mother_genes, samples=6
        )

        # --- SCROLL AREA ---
        self.scroll_y = 0
        self.scroll_speed = 50
        self.canvas_height = 2400
        self.canvas = pygame.Surface((self.app.WIDTH, self.canvas_height))

        # Back button
        self.back_button = Button(
            (self.app.WIDTH // 2 - 80, self.app.HEIGHT - 60, 160, 48),
            "← Back",
            self.font_normal,
            self._go_back
        )

    def _go_back(self):
        from screens.trait_selection import TraitSelection
        self.app.current_screen = TraitSelection(self.app, "Father", "Mother")

    # -----------------------------------------------------
    # DRAW PARENTS SIDE-BY-SIDE
    # -----------------------------------------------------
    def draw_parents(self, surf, y):
        title = self.font_header.render("Parent Traits", True, (240,240,240))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 40

        left_x = 60
        right_x = self.app.WIDTH//2 + 40

        # Column titles
        surf.blit(self.font_normal.render("Father", True, (180,220,255)), (left_x, y))
        surf.blit(self.font_normal.render("Mother", True, (255,180,200)), (right_x, y))
        y += 28

        # Side-by-side lists
        father_items = list(self.father_readable.items())
        mother_items = list(self.mother_readable.items())
        max_len = max(len(father_items), len(mother_items))

        for i in range(max_len):
            if i < len(father_items):
                f_line = f"{father_items[i][0]}: {father_items[i][1]}"
                surf.blit(self.font_small.render(f_line, True, (220,220,220)), (left_x, y))

            if i < len(mother_items):
                m_line = f"{mother_items[i][0]}: {mother_items[i][1]}"
                surf.blit(self.font_small.render(m_line, True, (220,220,220)), (right_x, y))

            y += 22

        return y + 20

    # -----------------------------------------------------
    # DRAW PUNNETT SQUARE SECTION
    # -----------------------------------------------------
    def draw_punnett(self, surf, y):

        title = self.font_header.render("Per Locus", True, (240,240,180))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 40

        table_x = 60

        for locus, results in self.punnett.items():
            # Locus header
            surf.blit(self.font_normal.render(f"{locus} locus", True, (255,215,0)), (table_x, y))
            y += 26

            # Table header
            surf.blit(self.font_small.render("Genotype", True, (200,200,200)), (table_x, y))
            surf.blit(self.font_small.render("Probability", True, (200,200,200)), (table_x + 200, y))
            surf.blit(self.font_small.render("Trait", True, (200,200,200)), (table_x + 350, y))
            y += 20

            pygame.draw.line(surf, (100,100,100), (table_x, y), (table_x+500, y), 1)
            y += 10

            # Rows
            for genotype, info in results.items():
                surf.blit(self.font_small.render(genotype, True, (230,230,230)), (table_x, y))
                surf.blit(self.font_small.render(info["probability"], True, (230,230,230)), (table_x + 200, y))
                surf.blit(self.font_small.render(info["trait"], True, (230,230,230)), (table_x + 350, y))
                y += 22

            y += 20

        return y

    # -----------------------------------------------------
    # DRAW MONTE CARLO SAMPLES
    # -----------------------------------------------------
    def draw_monte(self, surf, y):

        title = self.font_header.render("Sample Offspring", True, (180,255,255))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 40

        x = 60

        for i, text in enumerate(self.monte_readables, start=1):
            line = f"Sample {i}:  {text}"
            surf.blit(self.font_small.render(line, True, (210,210,210)), (x, y))
            y += 26

        return y

    # -----------------------------------------------------
    # BUILD SCROLLABLE CANVAS
    # -----------------------------------------------------
    def draw_canvas(self):
        self.canvas.fill((25,25,25))

        y = 30
        y = self.draw_parents(self.canvas, y)
        y += 20

        y = self.draw_punnett(self.canvas, y)
        y += 20

        y = self.draw_monte(self.canvas, y)
        y += 80

    # -----------------------------------------------------
    # RENDER ON SCREEN
    # -----------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self.canvas_height - self.app.HEIGHT))

        self.back_button.handle_event(event)

    def draw(self, screen):
        self.draw_canvas()

        # Blit only the visible window cut
        screen.blit(self.canvas, (0, 0),
                    pygame.Rect(0, self.scroll_y, self.app.WIDTH, self.app.HEIGHT))

        # Scrollbar
        bar_x = self.app.WIDTH - 12
        bar_w = 8
        view_ratio = self.app.HEIGHT / self.canvas_height
        bar_h = int(self.app.HEIGHT * view_ratio)
        max_scroll = self.canvas_height - self.app.HEIGHT
        bar_y = int((self.scroll_y / max_scroll) * (self.app.HEIGHT - bar_h)) if max_scroll > 0 else 0

        pygame.draw.rect(screen, (70,70,70), (bar_x, 6, bar_w, self.app.HEIGHT-12))
        pygame.draw.rect(screen, (160,160,160), (bar_x, 6 + bar_y, bar_w, bar_h))

        self.back_button.draw(screen)
