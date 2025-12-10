"""dog_preview_window.py

Separate OpenGL window that shows live 3D dog models synchronized with trait selection.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from model.dog_model import DogModel
from model.visual_mapping import compute_visual_params_from_offspring
import threading
import time


class DogPreviewWindow:
    """Separate window showing two 3D dog models (father and mother)."""
    
    def __init__(self, width=800, height=400, title="Dog Preview"):
        """
        Initialize preview window.
        
        Args:
            width: Window width
            height: Window height
            title: Window title
        """
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.thread = None
        
        # Genotypes to display
        self.father_genotype = None
        self.mother_genotype = None
        
        # Lock for thread-safe updates
        self.lock = threading.Lock()
        
        # Default dog points
        self.points = {
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
        }
        
        self.rotation = 0
    
    def update_genotypes(self, father_genotype: dict, mother_genotype: dict):
        """
        Update the genotypes to display.
        
        Args:
            father_genotype: Father's genotype dict
            mother_genotype: Mother's genotype dict
        """
        with self.lock:
            self.father_genotype = father_genotype.copy() if father_genotype else None
            self.mother_genotype = mother_genotype.copy() if mother_genotype else None
    
    def start(self):
        """Start the preview window in a separate thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_window, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the preview window."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _run_window(self):
        """Run the OpenGL window loop (in separate thread)."""
        # Initialize Pygame and OpenGL in this thread
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        
        screen = pygame.display.set_mode(
            (self.width, self.height),
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption(self.title)
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.15, 0.15, 0.15, 1.0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        
        # Set up viewport for split screen
        glViewport(0, 0, self.width, self.height)
        
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
            
            # Clear screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Get current genotypes (thread-safe)
            with self.lock:
                father_geno = self.father_genotype.copy() if self.father_genotype else None
                mother_geno = self.mother_genotype.copy() if self.mother_genotype else None
            
            # Update rotation
            self.rotation += 0.5
            
            # Draw father (left half)
            if father_geno:
                self._draw_dog_in_viewport(
                    0, 0, self.width // 2, self.height,
                    father_geno,
                    "Father",
                    self.rotation
                )
            
            # Draw mother (right half)
            if mother_geno:
                self._draw_dog_in_viewport(
                    self.width // 2, 0, self.width // 2, self.height,
                    mother_geno,
                    "Mother",
                    self.rotation
                )
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS
        
        pygame.quit()
    
    def _draw_dog_in_viewport(self, x, y, width, height, genotype, label, rotation):
        """Draw a dog in a specific viewport."""
        # Set viewport
        glViewport(x, y, width, height)
        
        # Set up projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(width) / float(height) if height > 0 else 1.0
        gluPerspective(45, aspect, 0.1, 100.0)
        
        # Set up modelview
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 0, 1)
        glRotatef(rotation, 0, 0, 1)
        
        # Create dog model from genotype
        visual_params = compute_visual_params_from_offspring(genotype)
        
        body_color = visual_params.get('body_color', (1, 0.8, 0))
        head_color = visual_params.get('head_color', (1, 1, 0.8))
        leg_color = visual_params.get('leg_color', (0.45, 0.25, 0.07))
        spotted = visual_params.get('spotted', False)
        spot_pattern = visual_params.get('spot_pattern', None)
        merle = visual_params.get('merle', False)
        
        # Apply geometric modifications
        points = self.points.copy()
        leg_scale = visual_params.get('leg_scale', 1.0)
        if leg_scale != 1.0:
            for p in ['paw_fl', 'paw_fr', 'paw_bl', 'paw_br']:
                px, py, pz = points[p]
                points[p] = (px, py, pz * leg_scale)
        
        snout_forward = visual_params.get('snout_forward', 0.12)
        if snout_forward:
            px, py, pz = points['head_center']
            points['head_center'] = (px + snout_forward, py, pz)
            px, py, pz = points['head_base']
            points['head_base'] = (px + snout_forward, py, pz)
        
        # Create and draw model
        model = DogModel(
            points,
            body_color=body_color,
            leg_color=leg_color,
            head_color=head_color,
            spotted=spotted,
            spot_pattern=spot_pattern,
            merle=merle
        )
        
        model.draw()
        
        # Draw label (simple text - would need proper text rendering)
        # For now, just draw a colored indicator
        glLoadIdentity()
        glTranslatef(0, 0, -10)
        
        # Draw a small colored sphere as indicator
        if label == "Father":
            glColor3f(0.5, 0.7, 1.0)  # Blue
        else:
            glColor3f(1.0, 0.5, 0.7)  # Pink
        
        from OpenGL.GLU import gluNewQuadric, gluSphere
        quad = gluNewQuadric()
        glPushMatrix()
        glTranslatef(-3, 3, 0)
        gluSphere(quad, 0.2, 12, 12)
        glPopMatrix()


# Example usage
if __name__ == "__main__":
    # Test the preview window
    preview = DogPreviewWindow(title="Dog Preview Test")
    
    # Example genotypes
    father = {
        "E": ("E", "E"),
        "K": ("Kb", "Kb"),
        "A": ("Ay", "Ay"),
        "B": ("B", "B"),
        "D": ("D", "D"),
        "M": ("m", "m"),
        "S": ("S", "S"),
        "L": ("L", "L")
    }
    
    mother = {
        "E": ("e", "e"),
        "K": ("ky", "ky"),
        "A": ("at", "at"),
        "B": ("b", "b"),
        "D": ("d", "d"),
        "M": ("M", "m"),
        "S": ("sp", "sp"),
        "L": ("l", "l")
    }
    
    preview.update_genotypes(father, mother)
    preview.start()
    
    # Keep main thread alive
    try:
        while preview.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        preview.stop()
