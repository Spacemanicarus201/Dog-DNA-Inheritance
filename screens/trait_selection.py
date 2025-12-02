import pygame
from ui.dropdown import Dropdown
from ui.button import Button
from genome_library import TRAIT_CATEGORIES, TRAIT_TO_GENOTYPE, BREED_DEFAULTS


class TraitSelection:
    def __init__(self, app, father_breed, mother_breed):
        self.app = app
        self.father_breed = father_breed
        self.mother_breed = mother_breed

        self.font_title = pygame.font.SysFont(None, 28)
        self.font_normal = pygame.font.SysFont(None, 20)

        # Convert breed default genotypes -> readable trait names
        self.father_init = self._defaults_to_readable(BREED_DEFAULTS.get(father_breed, {}))
        self.mother_init = self._defaults_to_readable(BREED_DEFAULTS.get(mother_breed, {}))

        # Dropdown storage
        self.f_dropdowns = {}
        self.m_dropdowns = {}
        self.dropdown_order = []

        # ---------- FIXED SPACING ----------
        top = 140
        gap = 90            # <-- increased spacing
        dropdown_height = 44
        dropdown_width = 260

        left_x = 40
        right_x = self.app.WIDTH - (dropdown_width + 40)

        # Create dropdowns for each trait
        for i, (category, options) in enumerate(TRAIT_CATEGORIES.items()):
            y = top + i * gap

            father_default = self.father_init.get(category, options[0])
            mother_default = self.mother_init.get(category, options[0])

            d_f = Dropdown(left_x, y, dropdown_width, dropdown_height, options, font=self.font_normal)
            d_f.selected = father_default

            d_m = Dropdown(right_x, y, dropdown_width, dropdown_height, options, font=self.font_normal)
            d_m.selected = mother_default

            self.f_dropdowns[category] = d_f
            self.m_dropdowns[category] = d_m
            self.dropdown_order.append((d_f, d_m))

        # Buttons
        self.back_button = Button(
            (self.app.WIDTH//2 - 180, self.app.HEIGHT - 70, 150, 46),
            "<- Back",
            self.font_normal,
            self._go_back
        )

        self.next_button = Button(
            (self.app.WIDTH//2 + 30, self.app.HEIGHT - 70, 150, 46),
            "Next ->",
            self.font_normal,
            self._go_next
        )

    # ---------------------------------------------------------
    # Convert default genotypes -> human trait names
    # ---------------------------------------------------------
    def _defaults_to_readable(self, genotype_map):
        readable = {}
        for trait_name, mapping in TRAIT_TO_GENOTYPE.items():
            for locus, alleles in mapping.items():
                if locus in genotype_map and tuple(genotype_map[locus]) == tuple(alleles):
                    for category, options in TRAIT_CATEGORIES.items():
                        if trait_name in options:
                            readable[category] = trait_name
        return readable

    # Convert user-selected readable traits -> genotype overrides
    def _selections_to_overrides(self, selections):
        overrides = {}
        for category, trait in selections.items():
            if trait in TRAIT_TO_GENOTYPE:
                for locus, alleles in TRAIT_TO_GENOTYPE[trait].items():
                    overrides[locus] = tuple(alleles)
        return overrides

    # Navigation
    def _go_back(self):
        from screens.main_menu import MainMenu
        self.app.current_screen = MainMenu(self.app)

    def _go_next(self):
        father_sel = {cat: dd.selected for cat, dd in self.f_dropdowns.items()}
        mother_sel = {cat: dd.selected for cat, dd in self.m_dropdowns.items()}

        father_over = self._selections_to_overrides(father_sel)
        mother_over = self._selections_to_overrides(mother_sel)

        father_defaults = BREED_DEFAULTS.get(self.father_breed, {})
        mother_defaults = BREED_DEFAULTS.get(self.mother_breed, {})

        from screens.genetic_summary import GeneticSummary
        self.app.current_screen = GeneticSummary(
            self.app,
            father_readable=father_sel,
            mother_readable=mother_sel,
            father_defaults=father_defaults,
            mother_defaults=mother_defaults,
            father_overrides=father_over,
            mother_overrides=mother_over
        )

    # Event handler
    def handle_event(self, event):
        for df, dm in self.dropdown_order:
            df.handle_event(event)
            dm.handle_event(event)
        self.back_button.handle_event(event)
        self.next_button.handle_event(event)

    # Drawing
    def draw(self, screen):
        screen.fill((26, 26, 26))

        title = self.font_title.render("Select Parent Traits", True, (230, 230, 230))
        screen.blit(title, (self.app.WIDTH//2 - title.get_width()//2, 30))

        # Pass 1: closed boxes
        for df, dm in self.dropdown_order:
            df.draw(screen)
            dm.draw(screen)

        self.back_button.draw(screen)
        self.next_button.draw(screen)

        # Pass 2: open menus (top layer)
        for df, dm in self.dropdown_order:
            df.draw_open_menu(screen)
            dm.draw_open_menu(screen)