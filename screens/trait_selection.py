import pygame
import random
import sys
from ui.dropdown import Dropdown
from ui.button import Button
from genome_library import TRAIT_CATEGORIES, TRAIT_TO_GENOTYPE, BREED_DEFAULTS
from logic.genetic_calculator import GeneticCalculator
from model.visual_mapping import compute_visual_params


class TraitSelection:
    SCROLL_SPEED = 30

    def __init__(self, app, father_breed, mother_breed):
        self.app = app
        self.father_breed = father_breed
        self.mother_breed = mother_breed

        self.font_title = pygame.font.SysFont(None, 30)
        self.font_normal = pygame.font.SysFont(None, 20)

        self.calc = GeneticCalculator()

        # auto fill all loci based on breed
        self.father_defaults = self.calc.complete_genotype(BREED_DEFAULTS.get(father_breed, {}))
        self.mother_defaults = self.calc.complete_genotype(BREED_DEFAULTS.get(mother_breed, {}))

        # convert to readable dropdown values
        self.father_init = self.calc.genotype_to_readable(self.father_defaults)
        self.mother_init = self.calc.genotype_to_readable(self.mother_defaults)
        
        # Preview window disabled - causes crashes with Pygame
        # TODO: Implement in-window preview instead
        self.preview_window = None
        # self._init_preview_window()

        self.f_dropdowns = {}
        self.m_dropdowns = {}
        self.dropdown_order = []

        # scrolling
        self.scroll_y = 0

        top = 140
        gap = 90
        dd_h = 44
        dd_w = 260
        left_x = 40
        right_x = self.app.WIDTH - (dd_w + 40)

        # Create dropdowns dynamically from dataset
        for i, (category, options) in enumerate(TRAIT_CATEGORIES.items()):
            y = top + i * gap

            d_f = Dropdown(left_x, y, dd_w, dd_h, options, font=self.font_normal)
            d_m = Dropdown(right_x, y, dd_w, dd_h, options, font=self.font_normal)

            d_f.selected = self.father_init.get(category, options[0])
            d_m.selected = self.mother_init.get(category, options[0])

            d_f.base_y = y
            d_m.base_y = y

            self.f_dropdowns[category] = d_f
            self.m_dropdowns[category] = d_m
            self.dropdown_order.append((category, d_f, d_m))

        # Navigation buttons
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
        
        # Individual 3D preview buttons (top corners)
        self.view_father_button = Button(
            (20, 20, 140, 40),
            "View Father 3D", self.font_normal, self._view_father_3d
        )
        self.view_mother_button = Button(
            (self.app.WIDTH - 160, 20, 140, 40),
            "View Mother 3D", self.font_normal, self._view_mother_3d
        )

        self.max_scroll = max(0, len(self.dropdown_order) * 70)


    # ----------------------------------------------------
    def _selections_to_overrides(self, selections):
        overrides = {}
        for category, trait_name in selections.items():
            loci_map = TRAIT_TO_GENOTYPE.get(trait_name, {})
            for locus, alleles in loci_map.items():
                overrides[locus] = tuple(alleles)
        return overrides

    # ----------------------------------------------------
    def _go_back(self):
        self.cleanup()  # Close preview window
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

        # Compute final genotypes for parents
        father_final = self.calc.combine_defaults_with_overrides(self.father_defaults, father_overrides)
        mother_final = self.calc.combine_defaults_with_overrides(self.mother_defaults, mother_overrides)

        # Store visual params on the app so other screens (e.g., DogModelTest) can read them
        try:
            self.app.current_visual_params = compute_visual_params(father_final, mother_final)
        except Exception:
            self.app.current_visual_params = None
        
        # IMPORTANT: Cleanup preview window before transitioning
        self.cleanup()

        from screens.genetic_summary import GeneticSummary
        self.app.current_screen = GeneticSummary(
            self.app,
            self.father_breed,
            self.mother_breed,
            father_readable=father_sel,
            mother_readable=mother_sel,
            father_defaults=self.father_defaults,
            mother_defaults=self.mother_defaults,
            father_overrides=father_overrides,
            mother_overrides=mother_overrides
        )

    # ----------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * TraitSelection.SCROLL_SPEED
            self.scroll_y = max(-self.max_scroll, min(self.scroll_y, 100))

        for _, d_f, d_m in self.dropdown_order:
            d_f.handle_event(event)
            d_m.handle_event(event)

        self.back_button.handle_event(event)
        self.reset_button.handle_event(event)
        self.random_button.handle_event(event)
        self.next_button.handle_event(event)
        self.view_father_button.handle_event(event)
        self.view_mother_button.handle_event(event)
        
        # Update live viewers when traits change
        self._update_live_viewers()

    # ----------------------------------------------------
    def _init_preview_window(self):
        """Initialize the dog preview window."""
        try:
            from model.dog_preview_window import DogPreviewWindow
            self.preview_window = DogPreviewWindow(
                width=900,
                height=450,
                title=f"Dog Preview: {self.father_breed} × {self.mother_breed}"
            )
            # DON'T auto-start - let user click button to open
            # self.preview_window.start()
            print("✓ Preview window ready (click 'Toggle 3D Preview' to open)")
        except Exception as e:
            print(f"⚠ Could not create preview window: {e}")
            print("  (3D preview will not be available)")
            self.preview_window = None
    
    def _update_preview(self):
        """Update preview window with current trait selections."""
        if not self.preview_window or not self.preview_window.running:
            return
        
        try:
            # Get current selections
            father_sel = {cat: d_f.selected for cat, d_f, _ in self.dropdown_order}
            mother_sel = {cat: d_m.selected for cat, _, d_m in self.dropdown_order}
            
            # Convert to genotypes
            father_overrides = self._selections_to_overrides(father_sel)
            mother_overrides = self._selections_to_overrides(mother_sel)
            
            father_final = self.calc.combine_defaults_with_overrides(
                self.father_defaults, father_overrides
            )
            mother_final = self.calc.combine_defaults_with_overrides(
                self.mother_defaults, mother_overrides
            )
            
            # Update preview window
            self.preview_window.update_genotypes(father_final, mother_final)
        except Exception as e:
            print(f"⚠ Error updating preview: {e}")
    
    def _view_father_3d(self):
        """Open live 3D view for father dog."""
        try:
            import subprocess
            import json
            import os
            
            # Create temp directory for genotype files
            os.makedirs("temp_genotypes", exist_ok=True)
            
            # Get current father selections and save to file
            father_sel = {cat: d_f.selected for cat, d_f, _ in self.dropdown_order}
            father_overrides = self._selections_to_overrides(father_sel)
            father_final = self.calc.combine_defaults_with_overrides(
                self.father_defaults, father_overrides
            )
            
            # Save to file
            genotype_file = "temp_genotypes/father_genotype.json"
            with open(genotype_file, 'w') as f:
                json.dump(father_final, f)
            
            dog_name = f"Father ({self.father_breed})"
            
            # Launch live viewer as separate process
            subprocess.Popen([
                sys.executable,
                "live_dog_viewer.py",
                genotype_file,
                dog_name
            ], cwd=".")
            
            # Mark that father viewer is running
            self.father_viewer_active = True
            
            print(f"✓ Opened live 3D view for {dog_name}")
        except Exception as e:
            print(f"⚠ Error opening father 3D view: {e}")
    
    def _view_mother_3d(self):
        """Open live 3D view for mother dog."""
        try:
            import subprocess
            import json
            import os
            
            # Create temp directory for genotype files
            os.makedirs("temp_genotypes", exist_ok=True)
            
            # Get current mother selections and save to file
            mother_sel = {cat: d_m.selected for cat, _, d_m in self.dropdown_order}
            mother_overrides = self._selections_to_overrides(mother_sel)
            mother_final = self.calc.combine_defaults_with_overrides(
                self.mother_defaults, mother_overrides
            )
            
            # Save to file
            genotype_file = "temp_genotypes/mother_genotype.json"
            with open(genotype_file, 'w') as f:
                json.dump(mother_final, f)
            
            dog_name = f"Mother ({self.mother_breed})"
            
            # Launch live viewer as separate process
            subprocess.Popen([
                sys.executable,
                "live_dog_viewer.py",
                genotype_file,
                dog_name
            ], cwd=".")
            
            # Mark that mother viewer is running
            self.mother_viewer_active = True
            
            print(f"✓ Opened live 3D view for {dog_name}")
        except Exception as e:
            print(f"⚠ Error opening mother 3D view: {e}")
    
    def _update_live_viewers(self):
        """Update genotype files for live viewers."""
        try:
            import json
            import os
            
            # Update father genotype file if viewer is active
            if hasattr(self, 'father_viewer_active') and self.father_viewer_active:
                father_sel = {cat: d_f.selected for cat, d_f, _ in self.dropdown_order}
                father_overrides = self._selections_to_overrides(father_sel)
                father_final = self.calc.combine_defaults_with_overrides(
                    self.father_defaults, father_overrides
                )
                
                genotype_file = "temp_genotypes/father_genotype.json"
                with open(genotype_file, 'w') as f:
                    json.dump(father_final, f)
            
            # Update mother genotype file if viewer is active
            if hasattr(self, 'mother_viewer_active') and self.mother_viewer_active:
                mother_sel = {cat: d_m.selected for cat, _, d_m in self.dropdown_order}
                mother_overrides = self._selections_to_overrides(mother_sel)
                mother_final = self.calc.combine_defaults_with_overrides(
                    self.mother_defaults, mother_overrides
                )
                
                genotype_file = "temp_genotypes/mother_genotype.json"
                with open(genotype_file, 'w') as f:
                    json.dump(mother_final, f)
        except Exception as e:
            pass  # Silently ignore errors
    
    def cleanup(self):
        """Cleanup when leaving this screen."""
        # No preview window to clean up anymore
        pass
    
    def draw(self, screen):
        screen.fill((26, 26, 26))

        title = self.font_title.render("Select Parent Traits", True, (230, 230, 230))
        screen.blit(title, (self.app.WIDTH//2 - title.get_width()//2, 30))
        
        # No preview window status needed anymore

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
        self.view_father_button.draw(screen)
        self.view_mother_button.draw(screen)

        for _, d_f, d_m in self.dropdown_order:
            d_f.draw_open_menu(screen)
            d_m.draw_open_menu(screen)
