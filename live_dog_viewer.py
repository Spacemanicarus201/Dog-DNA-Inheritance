"""live_dog_viewer.py

Live-updating 3D dog model viewer that watches a JSON file for genotype changes.
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import json
import os
import time
from model.dog_model import DogModel
from model.visual_mapping import compute_visual_params_from_offspring


def load_genotype(filepath):
    """Load genotype from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def main():
    """Run live-updating 3D dog viewer."""
    if len(sys.argv) < 3:
        print("Usage: python live_dog_viewer.py <genotype_file> <dog_name>")
        sys.exit(1)
    
    genotype_file = sys.argv[1]
    dog_name = sys.argv[2] if len(sys.argv) > 2 else "Dog"
    
    # Initialize Pygame and OpenGL
    pygame.init()
    width, height = 600, 600
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"3D View: {dog_name} (Live)")
    
    # OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.15, 0.15, 0.15, 1.0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    
    # Set up viewport and projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = float(width) / float(height)
    gluPerspective(45, aspect, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Default dog points
    base_points = {
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
    
    # Track file modification time
    last_mtime = 0
    current_genotype = None
    model = None
    
    # Main loop
    clock = pygame.time.Clock()
    rotation = 0
    running = True
    
    print(f"✓ Live 3D Viewer opened for: {dog_name}")
    print(f"  Watching: {genotype_file}")
    print("  Controls: ESC or close window to exit")
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        # Check if genotype file has been updated
        try:
            mtime = os.path.getmtime(genotype_file)
            if mtime > last_mtime:
                last_mtime = mtime
                new_genotype = load_genotype(genotype_file)
                
                if new_genotype and new_genotype != current_genotype:
                    current_genotype = new_genotype
                    
                    # Rebuild model with new genotype
                    visual_params = compute_visual_params_from_offspring(current_genotype)
                    
                    body_color = visual_params.get('body_color', (1, 0.8, 0))
                    head_color = visual_params.get('head_color', (1, 1, 0.8))
                    leg_color = visual_params.get('leg_color', (0.45, 0.25, 0.07))
                    spotted = visual_params.get('spotted', False)
                    spot_pattern = visual_params.get('spot_pattern', None)
                    merle = visual_params.get('merle', False)
                    
                    # Apply geometric modifications
                    points = base_points.copy()
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
                    
                    # Create new model
                    model = DogModel(
                        points,
                        body_color=body_color,
                        leg_color=leg_color,
                        head_color=head_color,
                        spotted=spotted,
                        spot_pattern=spot_pattern,
                        merle=merle
                    )
                    
                    print(f"  ↻ Model updated!")
        except FileNotFoundError:
            pass  # File doesn't exist yet
        
        # Clear and render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 0, 1)
        glRotatef(rotation, 0, 0, 1)
        
        if model:
            model.draw()
        
        pygame.display.flip()
        rotation += 0.5
        clock.tick(30)
    
    print(f"✓ Live 3D Viewer closed for: {dog_name}")
    pygame.quit()


if __name__ == "__main__":
    main()
