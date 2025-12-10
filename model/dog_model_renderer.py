"""dog_model_renderer.py

Renders 3D dog model to a 2D Pygame surface for embedding in UI screens.
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from model.dog_model import DogModel
from model.visual_mapping import compute_visual_params_from_offspring
import numpy as np


class DogModelRenderer:
    """Renders a 3D dog model to a 2D Pygame surface."""
    
    def __init__(self, width=300, height=300):
        """
        Initialize renderer.
        
        Args:
            width: Width of rendered image
            height: Height of rendered image
        """
        self.width = width
        self.height = height
        self.rotation = 0
        
        # Default dog model points
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
        
        # OpenGL context (hidden window)
        self._init_opengl()
    
    def _init_opengl(self):
        """Initialize OpenGL context."""
        # Create hidden window for OpenGL rendering
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        self.gl_surface = pygame.display.set_mode(
            (self.width, self.height),
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN
        )
        
        # OpenGL setup
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)  # Transparent background
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set up viewport and projection
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(self.width) / float(self.height)
        gluPerspective(45, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def render_to_surface(self, genotype: dict, rotation: float = 0) -> pygame.Surface:
        """
        Render dog model to a Pygame surface.
        
        Args:
            genotype: Dog genotype dict
            rotation: Rotation angle in degrees
            
        Returns:
            Pygame surface with rendered dog
        """
        # Compute visual parameters from genotype
        visual_params = compute_visual_params_from_offspring(genotype)
        
        # Create dog model
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
                x, y, z = points[p]
                points[p] = (x, y, z * leg_scale)
        
        snout_forward = visual_params.get('snout_forward', 0.12)
        if snout_forward:
            x, y, z = points['head_center']
            points['head_center'] = (x + snout_forward, y, z)
            x, y, z = points['head_base']
            points['head_base'] = (x + snout_forward, y, z)
        
        # Create model
        model = DogModel(
            points,
            body_color=body_color,
            leg_color=leg_color,
            head_color=head_color,
            spotted=spotted,
            spot_pattern=spot_pattern,
            merle=merle
        )
        
        # Render to OpenGL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 0, 1)
        glRotatef(rotation, 0, 0, 1)
        
        model.draw()
        
        # Read pixels from OpenGL
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
        
        # Convert to Pygame surface
        surface = pygame.image.fromstring(data, (self.width, self.height), 'RGBA')
        
        # Flip vertically (OpenGL coordinates are inverted)
        surface = pygame.transform.flip(surface, False, True)
        
        return surface
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        pygame.display.quit()


# Simpler approach: Pre-render static images
def create_dog_preview(genotype: dict, size=(200, 200)) -> pygame.Surface:
    """
    Create a simple 2D representation of a dog (fallback if OpenGL fails).
    
    Args:
        genotype: Dog genotype
        size: (width, height) of preview
        
    Returns:
        Pygame surface with dog silhouette
    """
    from model.visual_mapping import compute_visual_params_from_offspring
    
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent
    
    # Get colors
    visual_params = compute_visual_params_from_offspring(genotype)
    body_color = visual_params.get('body_color', (1, 0.8, 0))
    leg_color = visual_params.get('leg_color', (0.45, 0.25, 0.07))
    
    # Convert to 0-255 range
    body_rgb = tuple(int(c * 255) for c in body_color)
    leg_rgb = tuple(int(c * 255) for c in leg_color)
    
    w, h = size
    cx, cy = w // 2, h // 2
    
    # Draw simple dog silhouette
    # Body (ellipse)
    pygame.draw.ellipse(surface, body_rgb, (cx - 60, cy - 30, 120, 60))
    
    # Head (circle)
    pygame.draw.circle(surface, body_rgb, (cx + 70, cy - 10), 30)
    
    # Legs (rectangles)
    leg_width = 12
    leg_height = 40
    pygame.draw.rect(surface, leg_rgb, (cx - 40, cy + 20, leg_width, leg_height))  # Front left
    pygame.draw.rect(surface, leg_rgb, (cx - 20, cy + 20, leg_width, leg_height))  # Front right
    pygame.draw.rect(surface, leg_rgb, (cx + 10, cy + 20, leg_width, leg_height))  # Back left
    pygame.draw.rect(surface, leg_rgb, (cx + 30, cy + 20, leg_width, leg_height))  # Back right
    
    # Tail (triangle)
    tail_points = [(cx - 60, cy), (cx - 90, cy - 20), (cx - 80, cy + 10)]
    pygame.draw.polygon(surface, body_rgb, tail_points)
    
    # Ears (triangles)
    ear_l = [(cx + 55, cy - 35), (cx + 50, cy - 50), (cx + 60, cy - 40)]
    ear_r = [(cx + 80, cy - 35), (cx + 75, cy - 50), (cx + 85, cy - 40)]
    pygame.draw.polygon(surface, leg_rgb, ear_l)
    pygame.draw.polygon(surface, leg_rgb, ear_r)
    
    # Eye (small black circle)
    pygame.draw.circle(surface, (0, 0, 0), (cx + 75, cy - 15), 3)
    
    # Nose (small black circle)
    pygame.draw.circle(surface, (0, 0, 0), (cx + 95, cy - 5), 4)
    
    return surface
