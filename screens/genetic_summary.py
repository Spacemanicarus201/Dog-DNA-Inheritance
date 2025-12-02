import pygame
from logic.genetic_calculator import GeneticCalculator
from ui.button import Button
from utils.debug import debug   # <-- 🔥 debugging enabled


class GeneticSummary:
    def __init__(self, app,
                 father_readable, mother_readable,
                 father_defaults, mother_defaults,
                 father_overrides, mother_overrides):

        debug("\n===== OPENING GENETIC SUMMARY SCREEN =====")

        self.app = app

        # Fonts
        self.font_title = pygame.font.SysFont(None, 32)
        self.font_header = pygame.font.SysFont(None, 26)
        self.font_normal = pygame.font.SysFont(None, 20)
        self.font_small = pygame.font.SysFont(None, 18)
        self.font_tiny = pygame.font.SysFont(None, 16)

        # Store parent phenotype dicts
        self.father_readable = father_readable
        self.mother_readable = mother_readable

        # Build merged genes
        calc = GeneticCalculator()
        self.father_genes = calc.combine_defaults_with_overrides(father_defaults, father_overrides)
        self.mother_genes = calc.combine_defaults_with_overrides(mother_defaults, mother_overrides)

        debug("Father final genotype:", self.father_genes)
        debug("Mother final genotype:", self.mother_genes)

        # Run Punnett + Monte + Bayesian + Similarity
        debug("→ Running genetic engine summary…")
        self.punnett, self.monte_samples, self.monte_readables = calc.generate_summary(
            self.father_genes, self.mother_genes, samples=6
        )
        self.calc = calc

        debug("\n===== SUMMARY GENERATION DONE =====\n")

        # Scroll system
        self.scroll_y = 0
        self.scroll_speed = 50
        self.canvas_height = 3500
        self.canvas = pygame.Surface((self.app.WIDTH, self.canvas_height))

        # Tracking first-time draw logs so it logs once
        self.logged = {
            "parents": False,
            "punnett": False,
            "monte": False
        }

        # Back button
        self.back_button = Button(
            (self.app.WIDTH // 2 - 80, self.app.HEIGHT - 60, 160, 48),
            "← Back",
            self.font_normal,
            self._go_back
        )

    def _go_back(self):
        debug("← Returning to TraitSelection screen")
        from screens.trait_selection import TraitSelection
        self.app.current_screen = TraitSelection(self.app, "Father", "Mother")

    # -----------------------------------------------------
    # PARENTS
    # -----------------------------------------------------
    def draw_parents(self, surf, y):
        if not self.logged["parents"]:
            debug("Drawing parent trait table…")
            self.logged["parents"] = True

        title = self.font_header.render("Parent Traits", True, (240,240,240))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 40

        left_x = 60
        right_x = self.app.WIDTH//2 + 40

        surf.blit(self.font_normal.render("Father", True, (180,220,255)), (left_x, y))
        surf.blit(self.font_normal.render("Mother", True, (255,180,200)), (right_x, y))
        y += 28

        f_items = list(self.father_readable.items())
        m_items = list(self.mother_readable.items())
        max_rows = max(len(f_items), len(m_items))

        for i in range(max_rows):
            if i < len(f_items):
                surf.blit(self.font_small.render(f"{f_items[i][0]}: {f_items[i][1]}", True, (220,220,220)), (left_x, y))
            if i < len(m_items):
                surf.blit(self.font_small.render(f"{m_items[i][0]}: {m_items[i][1]}", True, (220,220,220)), (right_x, y))
            y += 22
        return y + 20

    # -----------------------------------------------------
    # PUNNETT
    # -----------------------------------------------------
    def draw_punnett(self, surf, y):
        if not self.logged["punnett"]:
            debug("Drawing Punnett probability table…")
            self.logged["punnett"] = True

        title = self.font_header.render("Per Locus Probability", True, (240,240,180))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 45

        table_x = 60

        for locus, rows in self.punnett.items():
            surf.blit(self.font_normal.render(f"{locus} locus", True, (255,215,0)), (table_x, y))
            y += 26

            surf.blit(self.font_small.render("Genotype", True, (200,200,200)), (table_x, y))
            surf.blit(self.font_small.render("Prob", True, (200,200,200)), (table_x + 170, y))
            surf.blit(self.font_small.render("Trait", True, (200,200,200)), (table_x + 270, y))
            y += 18

            pygame.draw.line(surf, (100,100,100), (table_x, y), (table_x + 500, y), 1)
            y += 10

            for row in rows:
                surf.blit(self.font_small.render(row["genotype"], True, (235,235,235)), (table_x, y))
                surf.blit(self.font_small.render(row["probability"], True, (235,235,235)), (table_x + 170, y))
                surf.blit(self.font_small.render(row["trait"], True, (235,235,235)), (table_x + 270, y))
                y += 22

            y += 18
        return y

    # -----------------------------------------------------
    # MONTE + BAYESIAN + SIMILARITY
    # -----------------------------------------------------
    def draw_monte(self, surf, y):
        if not self.logged["monte"]:
            debug("Drawing Monte Carlo results (with Bayesian + similarity)…")
            self.logged["monte"] = True

        title = self.font_header.render("Sample Offspring (Monte Carlo)", True, (180,255,255))
        surf.blit(title, (self.app.WIDTH//2 - title.get_width()//2, y))
        y += 45

        x = 60

        for i, child in enumerate(self.monte_samples, start=1):
            phenotype = child["phenotype"]
            sims = child["similarity"]

            surf.blit(self.font_small.render(f"Sample {i}: {phenotype}", True, (210,210,210)), (x, y))
            y += 22

            surf.blit(self.font_tiny.render(
                f"Similarity — Father: {sims['father']:.2f}   Mother: {sims['mother']:.2f}",
                True, (190, 230, 255)
            ), (x + 20, y))
            y += 18

            if sims["bayesian"]:
                bayes_text = "Bayesian → " + "  ".join([f"{k}:{v}" for k, v in sims["bayesian"].items()])
                surf.blit(self.font_tiny.render(bayes_text, True, (240, 240, 170)), (x + 20, y))
                y += 20

            y += 11
        return y

    # -----------------------------------------------------
    # Rebuild Canvas
    # -----------------------------------------------------
    def draw_canvas(self):
        self.canvas.fill((25,25,25))
        y = 30
        y = self.draw_parents(self.canvas, y) + 10
        y = self.draw_punnett(self.canvas, y) + 10
        y = self.draw_monte(self.canvas, y) + 50

    # -----------------------------------------------------
    # Scroll + Draw
    # -----------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            prev_scroll = self.scroll_y
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self.canvas_height - self.app.HEIGHT))

            if self.scroll_y != prev_scroll:
                debug(f"Scroll → {self.scroll_y}/{self.canvas_height - self.app.HEIGHT}")

        self.back_button.handle_event(event)

    def draw(self, screen):
        self.draw_canvas()
        screen.blit(self.canvas, (0, 0),
                    pygame.Rect(0, self.scroll_y, self.app.WIDTH, self.app.HEIGHT))

        bar_x = self.app.WIDTH - 12
        bar_w = 8
        view_ratio = self.app.HEIGHT / self.canvas_height
        bar_h = int(self.app.HEIGHT * view_ratio)
        max_scroll = self.canvas_height - self.app.HEIGHT
        bar_y = int((self.scroll_y / max_scroll) * (self.app.HEIGHT - bar_h)) if max_scroll > 0 else 0

        pygame.draw.rect(screen, (70,70,70), (bar_x, 6, bar_w, self.app.HEIGHT-12))
        pygame.draw.rect(screen, (160,160,160), (bar_x, 6 + bar_y, bar_w, bar_h))

        self.back_button.draw(screen)
