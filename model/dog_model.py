# dog_model/dog_model.py
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# --- Helper Functions ---
def draw_cylinder(p0, p1, radius=0.05, slices=12):
    """Draw a cylinder from p0 to p1."""
    v = np.array(p1) - np.array(p0)
    length = np.linalg.norm(v)
    if length < 1e-6:
        return
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(*p0)
    v_unit = v / length
    axis = np.cross([0,0,1], v_unit)
    angle = np.degrees(np.arccos(np.clip(np.dot([0,0,1], v_unit), -1, 1)))
    if np.linalg.norm(axis) > 0.0001:
        glRotatef(angle, *axis)
    gluCylinder(quad, radius, radius, length, slices, 1)
    glPopMatrix()

def draw_sphere(center, radius=0.1, slices=12, stacks=12):
    """Draw a sphere at a given center."""
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(*center)
    gluSphere(quad, radius, slices, stacks)
    glPopMatrix()

def draw_ellipsoid(center, rx=0.2, ry=0.18, rz=0.14, slices=16, stacks=16):
    """Draw an ellipsoid (scaled sphere) for dog head cranium."""
    glPushMatrix()
    glTranslatef(*center)
    glScalef(rx, ry, rz)
    quad = gluNewQuadric()
    gluSphere(quad, 1.0, slices, stacks)
    glPopMatrix()

# --- Dog Model Class ---
class DogModel:
    def __init__(self, points, body_color=(1,0.8,0), leg_color=(0.5,0.3,0), head_color=(1,1,0.8), spotted=False, spot_pattern=None, merle=False):
        """
        points: dict containing all the body, head, leg, tail points
        body_color, leg_color, head_color: RGB tuples (0-1)
        """
        self.points = points
        self.body_color = body_color
        self.leg_color = leg_color
        self.head_color = head_color
        # Spotting/merle flags (optional visual overlays)
        self.spotted = spotted
        self.spot_pattern = spot_pattern
        self.merle = merle

    def draw(self):
        # --- Body ---
        glColor3f(*self.body_color)
        draw_cylinder(self.points['body_back'], self.points['body_mid'], radius=0.3)
        draw_cylinder(self.points['body_front'], self.points['body_mid'], radius=0.3)
        draw_sphere(self.points['body_mid'], radius=0.35)

        # --- Head: Better dog face with prominent snout ---
        glColor3f(*self.head_color)
        
        # Position head further forward for better face visibility
        head_center = self.points.get('head_center', (1.5, 0, 0.3))
        
        # Broad ellipsoid cranium (skull/brain area)
        draw_ellipsoid(head_center, rx=0.26, ry=0.22, rz=0.20, slices=18, stacks=18)
        
        # Neck connection (smooth bridge from body to head)
        neck_mid = (self.points['body_front'][0] + 0.15, self.points['body_front'][1], self.points['body_front'][2] + 0.08)
        draw_cylinder(self.points['body_front'], neck_mid, radius=0.23)
        draw_sphere(neck_mid, radius=0.18)
        draw_cylinder(neck_mid, head_center, radius=0.19)
        
        # --- SNOUT: More prominent, forward-facing ---
        # Muzzle base (where snout starts, closer to head)
        muzzle_base = (head_center[0] + 0.12, head_center[1], head_center[2] - 0.03)
        draw_sphere(muzzle_base, radius=0.10)
        
        # Snout bridge (longer tapered cone from muzzle base forward)
        snout_mid = (head_center[0] + 0.38, head_center[1], head_center[2] - 0.05)
        draw_cylinder(muzzle_base, snout_mid, radius=0.085)
        
        # Nose tip (prominent, forward)
        nose_tip = (head_center[0] + 0.55, head_center[1], head_center[2] - 0.06)
        draw_sphere(nose_tip, radius=0.038)
        
        # Nostrils on the nose tip (very visible, small dark dots)
        glColor3f(0, 0, 0)
        nostril_l = (nose_tip[0] - 0.008, nose_tip[1] + 0.026, nose_tip[2] + 0.012)
        nostril_r = (nose_tip[0] - 0.008, nose_tip[1] - 0.026, nose_tip[2] + 0.012)
        draw_sphere(nostril_l, radius=0.017)
        draw_sphere(nostril_r, radius=0.017)
        
        # --- Eyes (larger, more visible) ---
        glColor3f(0, 0, 0)
        eye_l = (head_center[0] - 0.04, head_center[1] + 0.14, head_center[2] + 0.05)
        eye_r = (head_center[0] - 0.04, head_center[1] - 0.14, head_center[2] + 0.05)
        draw_sphere(eye_l, radius=0.040)
        draw_sphere(eye_r, radius=0.040)
        
        # --- Ears (positioned on top/back of head) ---
        glColor3f(*self.leg_color)
        ear_base_l = (head_center[0] - 0.08, head_center[1] + 0.20, head_center[2] + 0.16)
        ear_tip_l = (head_center[0] - 0.05, head_center[1] + 0.32, head_center[2] + 0.42)
        draw_cylinder(ear_base_l, ear_tip_l, radius=0.050)
        
        ear_base_r = (head_center[0] - 0.08, head_center[1] - 0.20, head_center[2] + 0.16)
        ear_tip_r = (head_center[0] - 0.05, head_center[1] - 0.32, head_center[2] + 0.42)
        draw_cylinder(ear_base_r, ear_tip_r, radius=0.050)

        # --- Legs ---
        glColor3f(*self.leg_color)
        for prefix in ['fl','fr','bl','br']:
            paw = self.points[f'paw_{prefix}']
            body_attach = self.points['body_front'] if prefix in ['fl','fr'] else self.points['body_back']
            draw_cylinder(body_attach, paw, radius=0.08)
            draw_sphere(paw, radius=0.05)

        # --- Tail ---
        glColor3f(*self.body_color)
        draw_cylinder(self.points['body_back'], self.points['tail_tip'], radius=0.07)

        # --- Overlays: spotted / merle simple patches ---
        # Draw a few white/gray patches on the body/head based on flags.
        if getattr(self, 'spotted', False) or getattr(self, 'merle', False):
            # Determine patch colors
            patches = []
            if self.spot_pattern == 'sp':
                # Piebald: larger white patches on flank and shoulder
                patches = [
                    (self.points['body_mid'][0] - 0.2, self.points['body_mid'][1] + 0.25, self.points['body_mid'][2] + 0.05, 0.18),
                    (self.points['body_front'][0] + 0.05, self.points['body_front'][1] - 0.18, self.points['body_front'][2] + 0.02, 0.16),
                ]
                patch_color = (1, 1, 1)
            elif self.spot_pattern == 'si':
                # Irish: small white on chest, paws, muzzle
                patches = [
                    (self.points['body_front'][0] + 0.05, 0, self.points['body_front'][2] - 0.05, 0.08),
                    (self.points['paw_fl'][0], self.points['paw_fl'][1], self.points['paw_fl'][2] + 0.02, 0.06),
                    (self.points['paw_fr'][0], self.points['paw_fr'][1], self.points['paw_fr'][2] + 0.02, 0.06),
                ]
                patch_color = (1, 1, 1)
            elif self.spot_pattern == 'sw':
                # Extreme white -> mostly white already, small dark patches for contrast
                patches = [
                    (self.points['body_mid'][0], self.points['body_mid'][1] + 0.18, self.points['body_mid'][2], 0.12),
                ]
                patch_color = (0.9, 0.9, 0.95)
            else:
                # Merle: small irregular gray/white splotches
                patches = [
                    (self.points['body_mid'][0] - 0.15, self.points['body_mid'][1] + 0.12, self.points['body_mid'][2] + 0.03, 0.09),
                    (self.points['body_mid'][0] + 0.12, self.points['body_mid'][1] - 0.18, self.points['body_mid'][2] + 0.02, 0.07),
                    (self.points['body_front'][0] - 0.05, self.points['body_front'][1] + 0.14, self.points['body_front'][2] + 0.01, 0.06),
                ]
                patch_color = (0.85, 0.85, 0.9)

            # Draw patches as small spheres (overlay on top of body geometry)
            glColor3f(*patch_color)
            for cx, cy, cz, r in patches:
                draw_sphere((cx, cy, cz), radius=r)
