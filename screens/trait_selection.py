import pygame
import random
from ui.dropdown import Dropdown
from ui.button import Button
from genome_library import TRAIT_CATEGORIES, TRAIT_TO_GENOTYPE, BREED_DEFAULTS
from logic.genetic_calculator import GeneticCalculator


class TraitSelection:
    SCROLL_SPEED = 30

    def __init__(self, app, father_breed, mother_breed):
        self.app = app
        self.father_breed = father_breed
        self.mother_breed = mother_breed

        self.font_title = pygame.font.SysFont(None, 30)
        self.font_normal = pygame.font.SysFont(None, 20)

        self.calc = GeneticCalculator()

        # Completed genotype = validated map (future dataset-proof)
        self.father_defaults = self.calc.complete_genotype(BREED_DEFAULTS.get(father_breed, {}))
        self.mother_defaults = self.calc.complete_genotype(BREED_DEFAULTS.get(mother_breed, {}))

        self.father_init = self.calc.genotype_to_readable(self.father_defaults)
        self.mother_init = self.calc.genotype_to_readable(self.mother_defaults)

        self.f_dropdowns = {}
        self.m_dropdowns = {}
        self.dropdown_order = []

        # scrolling position
        self.scroll_y = 0

        top = 140
        gap = 90
        dd_h = 44
        dd_w = 260
        left_x = 40
        right_x = self.app.WIDTH - (dd_w + 40)

        for i, (category, options) in enumerate(TRAIT_CATEGORIES.items()):
            y = top + i * gap

            d_f = Dropdown(left_x, y, dd_w, dd_h, options, font=self.font_normal)
            d_m = Dropdown(right_x, y, dd_w, dd_h, options, font=self.font_normal)

            d_f.selected = self.father_init.get(category, options[0])
            d_m.selected = self.mother_init.get(category, options[0])

            # required for scrolling — safe position memory
            d_f.base_y = y
            d_m.base_y = y

            self.f_dropdowns[category] = d_f
            self.m_dropdowns[category] = d_m
            self.dropdown_order.append((category, d_f, d_m))

        # navigation buttons
        self.back_button = Button(
            (self.app.WIDTH//2 - 240, self.app.HEIGHT - 70, 130, 46),
            "<- Back", self.font_normal, self._go_back
        )
        self.reset_button = Button(
            (self.app.WIDTH//2 - 90, self.app.HEIGHT - 70, 130, 46),
            "Reset", self.font_normal, self._reset_traits
        )
        self.random_button = Button(
            (self.app.WIDTH//2 + 60, self.app.HEIGHT - 70, 130, 46),
            "Random Both", self.font_normal, self._randomize
        )
        self.next_button = Button(
            (self.app.WIDTH//2 + 210, self.app.HEIGHT - 70, 130, 46),
            "Next ->", self.font_normal, self._go_next
        )

        # maximum scroll based on number of traits
        self.max_scroll = max(0, len(self.dropdown_order) * 70)

    # ----------------------------------------------------------------
    def _selections_to_overrides(self, selections):
        overrides = {}
        for category, trait in selections.items():
            loci = TRAIT_TO_GENOTYPE.get(trait)
            if loci:
                for locus, alleles in loci.items():
                    overrides[locus] = tuple(alleles)
        return overrides

    # ----------------------------------------------------------------
    def _go_back(self):
        from screens.main_menu import MainMenu
        self.app.current_screen = MainMenu(self.app)

    def _reset_traits(self):
        for category, d_f, d_m in self.dropdown_order:
            d_f.selected = self.father_init.get(category, d_f.options[0])
            d_m.selected = self.mother_init.get(category, d_m.options[0])

    def _randomize(self):
        for _, d_f, d_m in self.dropdown_order:
            d_f.selected = random.choice(d_f.options)
            d_m.selected = random.choice(d_m.options)

    def _go_next(self):
        father_sel = {cat: d_f.selected for cat, d_f, _ in self.dropdown_order}
        mother_sel = {cat: d_m.selected for cat, _, d_m in self.dropdown_order}

        father_overrides = self._selections_to_overrides(father_sel)
        mother_overrides = self._selections_to_overrides(mother_sel)

        from screens.genetic_summary import GeneticSummary
        self.app.current_screen = GeneticSummary(
            self.app,
            father_readable=father_sel,
            mother_readable=mother_sel,
            father_defaults=self.father_defaults,
            mother_defaults=self.mother_defaults,
            father_overrides=father_overrides,
            mother_overrides=mother_overrides
        )

    # ----------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * TraitSelection.SCROLL_SPEED

            # clamp scrolling (no over-scroll)
            self.scroll_y = max(-self.max_scroll, min(self.scroll_y, 100))

        for _, d_f, d_m in self.dropdown_order:
            d_f.handle_event(event)
            d_m.handle_event(event)

        self.back_button.handle_event(event)
        self.reset_button.handle_event(event)
        self.random_button.handle_event(event)
        self.next_button.handle_event(event)

    # ----------------------------------------------------------------
    def draw(self, screen):
        screen.fill((26, 26, 26))

        title = self.font_title.render("Select Parent Traits", True, (230, 230, 230))
        screen.blit(title, (self.app.WIDTH//2 - title.get_width()//2, 30))

        offset = self.scroll_y
        for _, d_f, d_m in self.dropdown_order:
            d_f.y = d_f.base_y + offset
            d_m.y = d_m.base_y + offset
            d_f.draw(screen)
            d_m.draw(screen)

        self.back_button.draw(screen)
        self.reset_button.draw(screen)
        self.random_button.draw(screen)
        self.next_button.draw(screen)

        for _, d_f, d_m in self.dropdown_order:
            d_f.draw_open_menu(screen)
            d_m.draw_open_menu(screen)
