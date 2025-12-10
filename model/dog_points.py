"""
Model points and a simple trait controller.

Provides `DOG_POINTS` (a small default point cloud) and a controller
`DogTraitController` that can apply simple trait-based scaling.
"""

# Simple default points for a toy dog wireframe (x, y, z)
DOG_POINTS = [
    (-1.0, 0.0, 0.0),  # body_back
    (0.0, 0.0, 0.0),   # body_mid
    (1.0, 0.0, 0.0),   # body_front
    (1.4, 0.0, 0.3),   # head_base
    (0.6, 0.5, -1.0),  # paw_fl
    (0.6, -0.5, -1.0), # paw_fr
    (-0.6, 0.5, -1.0), # paw_bl
    (-0.6, -0.5, -1.0),# paw_br
    (-1.5, 0.0, 0.5)   # tail_tip
]


class DogTraitController:
    def __init__(self):
        self.leg_length = 1.0
        self.body_length = 1.0
        self.ear_size = 1.0

    def apply(self, points):
        # Modify your dog points based on traits
        scaled = []
        for x, y, z in points:
            scaled.append((x, y * self.leg_length, z))
        return scaled
