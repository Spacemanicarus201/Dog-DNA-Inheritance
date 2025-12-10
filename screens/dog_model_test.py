import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from model.dog_model import DogModel
from ui.button import Button
from ui.dropdown import Dropdown
from genome_library import TRAIT_CATEGORIES, TRAIT_TO_GENOTYPE
from logic.genetic_calculator import GeneticCalculator
from model.visual_mapping import compute_visual_params
import random
import json


class DogModelTest:
    def __init__(self, app):
        self.app = app

        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        # Switch to an OpenGL-capable display and store it on the app
        self.app.SCREEN = pygame.display.set_mode((app.WIDTH, app.HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)

        glEnable(GL_DEPTH_TEST)
        # Basic OpenGL state for visible rendering
        glClearColor(0.18, 0.18, 0.18, 1.0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        # Texture for UI overlay
        self.ui_texture = glGenTextures(1)

        # Initialize viewport/projection for the current window size
        self.resize(app.WIDTH, app.HEIGHT)

        # Default model points
        self.points = {
            "body_back":  (-1, 0, 0),
            "body_mid":   (0, 0, 0),
            "body_front": (1, 0, 0),

            # Proper dog head anatomy
            "head_center": (1.5, 0, 0.3),
            "head_base":   (1.5, 0, 0.3),  # fallback for compatibility

            "paw_fl": (0.6,  0.5, -1),
            "paw_fr": (0.6, -0.5, -1),
            "paw_bl": (-0.6, 0.5, -1),
            "paw_br": (-0.6, -0.5, -1),

            "tail_tip": (-1.5, 0, 0.5)
        }

        self.model = DogModel(self.points)
        # Apply any visual params from TraitSelection (if available)
        vis = getattr(self.app, 'current_visual_params', None)
        if vis:
            # update colors and pattern flags
            body_col = vis.get('body_color')
            head_col = vis.get('head_color')
            spotted = vis.get('spotted', False)
            spot_pattern = vis.get('spot_pattern', None)
            merle = vis.get('merle', False)
            self.model = DogModel(self.points,
                                  body_color=body_col if body_col else (1,0.8,0),
                                  leg_color=(0.45,0.25,0.07),
                                  head_color=head_col if head_col else (1,1,0.8),
                                  spotted=spotted,
                                  spot_pattern=spot_pattern,
                                  merle=merle)
            # apply simple geometric params: leg scale and snout offset
            leg_scale = vis.get('leg_scale', 1.0)
            if leg_scale != 1.0:
                for p in ['paw_fl','paw_fr','paw_bl','paw_br']:
                    x,y,z = self.points[p]
                    self.points[p] = (x, y, z * leg_scale)
            snout_off = vis.get('snout_forward', 0.0)
            if snout_off:
                # move head and nose forward
                if 'head_center' in self.points:
                    x,y,z = self.points['head_center']
                    self.points['head_center'] = (x + snout_off, y, z)
                if 'head_base' in self.points:
                    x,y,z = self.points['head_base']
                    self.points['head_base'] = (x + snout_off, y, z)
                # bump tail slightly back for balance
                if 'tail_tip' in self.points:
                    x,y,z = self.points['tail_tip']
                    self.points['tail_tip'] = (x - snout_off*0.2, y, z)

        # Simple buttons
        font = pygame.font.SysFont(None, 26)
        self.btn_back = Button((20, 20, 150, 50), "Back", font, callback=self._go_back)

        # Example test buttons (later: change traits)
        self.btn_raise_tail = Button((20, 90, 180, 50), "Raise Tail", font, callback=self._raise_tail)
        self.btn_lower_tail = Button((20, 150, 180, 50), "Lower Tail", font, callback=self._lower_tail)

        # Trait-selection-like utility buttons
        self.btn_reset = Button((20, 210, 180, 50), "Reset Model", font, callback=self._reset_model)
        self.btn_randomize = Button((20, 270, 180, 50), "Randomize Visuals", font, callback=self._randomize_visuals)
        self.btn_open_traits = Button((20, 330, 220, 50), "Open Trait Selection", font, callback=self._open_trait_selection)

        self.rotation = 0

        # --- Dropdowns for independent trait testing (single model)
        self.calc = GeneticCalculator()
        self.dropdowns = []
        self.dropdown_map = {}

        dd_w = 260
        dd_h = 44
        right_x = self.app.WIDTH - (dd_w + 40)
        top = 80
        gap = 70

        for i, (category, options) in enumerate(TRAIT_CATEGORIES.items()):
            y = top + i * gap
            d = Dropdown(right_x, y, dd_w, dd_h, options, font=font)
            d.base_y = y
            self.dropdowns.append((category, d))
            self.dropdown_map[category] = d

        # for change detection
        self._last_visual = None

    def resize(self, w, h):
        # Update the display surface for OpenGL and update viewport/projection
        self.app.SCREEN = pygame.display.set_mode((w, h), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        glViewport(0, 0, w, h)

        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(w) / float(h) if h != 0 else 1.0
        gluPerspective(45, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def handle_event(self, event):
        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        # Use update() pattern (consistent with UI elsewhere)
        self.btn_back.update(mouse, pos)
        self.btn_raise_tail.update(mouse, pos)
        self.btn_lower_tail.update(mouse, pos)
        self.btn_reset.update(mouse, pos)
        self.btn_randomize.update(mouse, pos)
        self.btn_open_traits.update(mouse, pos)

        # Tail adjustments (keep for convenience)
        # (also allow keyboard arrow controls if desired)
        # Pass event to dropdowns
        # Handle single-model dropdown events
        for category, d in self.dropdowns:
            d.handle_event(event)

        # Recompute visuals from current dropdown selections and apply live
        selections = {cat: d.selected for cat, d in self.dropdowns}

        def _selections_to_overrides(selections):
            overrides = {}
            for category, trait_name in selections.items():
                mapping = TRAIT_TO_GENOTYPE.get(trait_name)
                if mapping:
                    for locus, alleles in mapping.items():
                        overrides[locus] = tuple(alleles)
            return overrides

        overrides = _selections_to_overrides(selections)

        # Use generic defaults for testing independent model traits
        defaults = self.calc.complete_genotype({})
        final = self.calc.combine_defaults_with_overrides(defaults, overrides)

        vis = compute_visual_params(final, final)

        # Always apply visuals (remove change detection - force recreation every frame)
        body_col = vis.get('body_color', (1, 0.8, 0))
        head_col = vis.get('head_color', (1, 1, 0.8))
        spotted = vis.get('spotted', False)
        spot_pattern = vis.get('spot_pattern', None)
        merle = vis.get('merle', False)

        # Recreate model with new colors every time and pass pattern flags
        self.model = DogModel(self.points,
                      body_color=body_col,
                      leg_color=(0.45, 0.25, 0.07),
                      head_color=head_col,
                      spotted=spotted,
                      spot_pattern=spot_pattern,
                      merle=merle)
        
        # Debug: print selected traits and resulting colors
        print(f"Selections: {selections}")
        print(f"Final genotype: {final}")
        print(f"Body color: {body_col}, Head color: {head_col}")

    def draw(self, screen):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 0, 1)

        self.rotation += self.app.time_delta * 20
        glRotatef(self.rotation, 0, 0, 1)

        self.model.draw()

        # Draw UI in 2D
        self.draw_ui()

    # --------------------
    # Button callbacks
    # --------------------
    def _go_back(self):
        from screens.main_menu import MainMenu
        self.app.change_screen(MainMenu)

    def _raise_tail(self):
        x, y, z = self.points.get("tail_tip", (0,0,0))
        self.points["tail_tip"] = (x, y, z + 0.3)

    def _lower_tail(self):
        x, y, z = self.points.get("tail_tip", (0,0,0))
        self.points["tail_tip"] = (x, y, z - 0.3)

    def _reset_model(self):
        # Reset key points to sensible defaults
        self.points.update({
            "body_back":  (-1, 0, 0),
            "body_mid":   (0, 0, 0),
            "body_front": (1, 0, 0),
            "head_center": (1.5, 0, 0.3),
            "head_base":   (1.5, 0, 0.3),
            "paw_fl": (0.6,  0.5, -1),
            "paw_fr": (0.6, -0.5, -1),
            "paw_bl": (-0.6, 0.5, -1),
            "paw_br": (-0.6, -0.5, -1),
            "tail_tip": (-1.5, 0, 0.5)
        })
        # Recreate model with default colors
        self.model = DogModel(self.points)

    def _randomize_visuals(self):
        # Random simple visual params (color/leg length/snout)
        import random
        def rand_color():
            return (random.random()*0.8+0.1, random.random()*0.6+0.1, random.random()*0.6+0.1)

        body_col = rand_color()
        head_col = rand_color()
        leg_scale = random.choice([0.9, 1.0, 1.1, 1.2])
        snout = random.choice([0.0, 0.06, 0.12])

        # Apply to model and points
        self.model = DogModel(self.points, body_color=body_col, head_color=head_col)
        for p in ['paw_fl','paw_fr','paw_bl','paw_br']:
            x,y,z = self.points[p]
            self.points[p] = (x, y, z * leg_scale)
        if 'head_center' in self.points:
            x,y,z = self.points['head_center']
            self.points['head_center'] = (x + snout, y, z)

    def _open_trait_selection(self):
        # Safely open TraitSelection with reasonable defaults to avoid crashes
        try:
            from screens.trait_selection import TraitSelection
            from genome_library import BREED_DEFAULTS

            breeds = list(BREED_DEFAULTS.keys())
            if len(breeds) >= 2:
                father_default, mother_default = breeds[0], breeds[1]
            elif len(breeds) == 1:
                father_default = mother_default = breeds[0]
            else:
                father_default = 'Labrador Retriever'
                mother_default = 'Golden Retriever'

            # If the app previously stored selected breeds, prefer those
            father = getattr(self.app, 'selected_father', None) or father_default
            mother = getattr(self.app, 'selected_mother', None) or mother_default

            # Use the same pattern as other screens: pass a callable that returns the screen
            self.app.change_screen(lambda app: TraitSelection(app, father, mother))

        except Exception as e:
            # Prevent crash and print debug info
            print("Failed to open TraitSelection:", e)

    def draw_ui(self):
        """Render Pygame UI into a texture and draw as an OpenGL quad."""
        w, h = self.app.WIDTH, self.app.HEIGHT

        # Draw UI to an offscreen Pygame surface
        ui_surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        ui_surf = ui_surf.convert_alpha()

        # Let buttons render into the offscreen surface (stacked like TraitSelection)
        self.btn_back.draw(ui_surf)
        self.btn_raise_tail.draw(ui_surf)
        self.btn_lower_tail.draw(ui_surf)
        self.btn_reset.draw(ui_surf)
        self.btn_randomize.draw(ui_surf)
        self.btn_open_traits.draw(ui_surf)
        
        # Draw dropdowns onto the UI surface
        for category, d in self.dropdowns:
            # ensure rect y follows base_y (in case resized or moved)
            d.rect.y = d.base_y
            d.draw(ui_surf)

        # Draw any open dropdown menus last so they overlay correctly
        for category, d in self.dropdowns:
            d.draw_open_menu(ui_surf)

        # Upload surface to GL texture
        data = pygame.image.tostring(ui_surf, "RGBA", True)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        # Draw textured quad in orthographic projection
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)
        glTexCoord2f(1, 1); glVertex2f(w, 0)
        glTexCoord2f(1, 0); glVertex2f(w, h)
        glTexCoord2f(0, 0); glVertex2f(0, h)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
