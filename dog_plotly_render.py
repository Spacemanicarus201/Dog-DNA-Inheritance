"""
Dog 3D Plotly renderer with proper dog head proportions.
Run standalone with: python dog_plotly_render.py
"""
import numpy as np
import plotly.graph_objects as go


# --- Helper Functions for Plotly ---
def cylinder_mesh(p0, p1, radius=0.05, resolution=12):
    """Generate mesh for a cylinder from p0 to p1."""
    p0 = np.array(p0)
    p1 = np.array(p1)
    v = p1 - p0
    length = np.linalg.norm(v)
    if length < 1e-6:
        return None, None, None

    z = np.linspace(0, length, resolution)
    theta = np.linspace(0, 2*np.pi, resolution)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_grid = radius * np.cos(theta_grid)
    y_grid = radius * np.sin(theta_grid)

    v_unit = v / length
    z_axis = np.array([0, 0, 1])
    axis = np.cross(z_axis, v_unit)

    if np.linalg.norm(axis) < 1e-6:
        rot_matrix = np.eye(3) if np.dot(z_axis, v_unit) > 0 else np.array([[1,0,0],[0,-1,0],[0,0,-1]])
    else:
        axis = axis / np.linalg.norm(axis)
        angle = np.arccos(np.clip(np.dot(z_axis, v_unit), -1, 1))
        K = np.array([[0, -axis[2], axis[1]],
                      [axis[2], 0, -axis[0]],
                      [-axis[1], axis[0], 0]])
        rot_matrix = np.eye(3) + np.sin(angle)*K + (1-np.cos(angle))*(K @ K)

    xyz = np.vstack([x_grid.ravel(), y_grid.ravel(), z_grid.ravel()])
    rotated = rot_matrix @ xyz
    x_rot = rotated[0,:].reshape(x_grid.shape) + p0[0]
    y_rot = rotated[1,:].reshape(y_grid.shape) + p0[1]
    z_rot = rotated[2,:].reshape(z_grid.shape) + p0[2]

    return x_rot, y_rot, z_rot


def sphere_mesh(p, radius=0.1, resolution=12):
    """Generate mesh for a sphere."""
    p = np.array(p)
    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    uu, vv = np.meshgrid(u, v)
    x = radius * np.cos(uu) * np.sin(vv) + p[0]
    y = radius * np.sin(uu) * np.sin(vv) + p[1]
    z = radius * np.cos(vv) + p[2]
    return x, y, z


def ellipsoid_mesh(center, rx=0.2, ry=0.18, rz=0.14, resolution=18):
    """Generate mesh for an ellipsoid (for dog head cranium)."""
    center = np.array(center)
    u = np.linspace(0, 2*np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    uu, vv = np.meshgrid(u, v)
    x = rx * np.cos(uu) * np.sin(vv) + center[0]
    y = ry * np.sin(uu) * np.sin(vv) + center[1]
    z = rz * np.cos(vv) + center[2]
    return x, y, z


def tapered_cylinder_mesh(p0, p1, radius_start=0.08, radius_end=0.06, resolution=12):
    """Generate mesh for a tapered cylinder."""
    p0 = np.array(p0)
    p1 = np.array(p1)
    v = p1 - p0
    length = np.linalg.norm(v)
    if length < 1e-6:
        return None, None, None

    z = np.linspace(0, length, resolution)
    theta = np.linspace(0, 2*np.pi, resolution)
    theta_grid, z_grid = np.meshgrid(theta, z)
    radius_grid = np.linspace(radius_start, radius_end, resolution)
    radius_interp = np.interp(z_grid, z, radius_grid)
    x_grid = radius_interp * np.cos(theta_grid)
    y_grid = radius_interp * np.sin(theta_grid)

    v_unit = v / length
    z_axis = np.array([0, 0, 1])
    axis = np.cross(z_axis, v_unit)

    if np.linalg.norm(axis) < 1e-6:
        rot_matrix = np.eye(3) if np.dot(z_axis, v_unit) > 0 else np.array([[1,0,0],[0,-1,0],[0,0,-1]])
    else:
        axis = axis / np.linalg.norm(axis)
        angle = np.arccos(np.clip(np.dot(z_axis, v_unit), -1, 1))
        K = np.array([[0, -axis[2], axis[1]],
                      [axis[2], 0, -axis[0]],
                      [-axis[1], axis[0], 0]])
        rot_matrix = np.eye(3) + np.sin(angle)*K + (1-np.cos(angle))*(K @ K)

    xyz = np.vstack([x_grid.ravel(), y_grid.ravel(), z_grid.ravel()])
    rotated = rot_matrix @ xyz
    x_rot = rotated[0,:].reshape(x_grid.shape) + p0[0]
    y_rot = rotated[1,:].reshape(y_grid.shape) + p0[1]
    z_rot = rotated[2,:].reshape(z_grid.shape) + p0[2]

    return x_rot, y_rot, z_rot


# --- Dog Anatomical Points ---
points = {
    # Torso
    'body_mid': np.array([0.5, 0, 0.1]),
    'body_front': np.array([0.1, 0, 0.05]),
    'body_back': np.array([0.9, 0, 0.05]),

    # Head: broader, rounder dog head (NOT a lightbulb!)
    # Cranium center: positioned where a dog's brain/skull would be
    'head_center': np.array([-0.15, 0, 0.25]),  # wider, rounder position
    
    # Snout: SHORT and blunt (not elongated)
    'muzzle_base': np.array([-0.32, 0, 0.18]),   # start of snout taper
    'nose_tip': np.array([-0.52, 0, 0.15]),       # short, blunt nose
    
    # Ears: on sides of cranium
    'ear_l': np.array([-0.15, 0.28, 0.40]),
    'ear_r': np.array([-0.15, -0.28, 0.40]),

    # Eyes
    'eye_l': np.array([-0.25, 0.11, 0.30]),
    'eye_r': np.array([-0.25, -0.11, 0.30]),

    # Legs
    'leg_fl_top': np.array([0.15, 0.25, -0.1]),
    'paw_fl': np.array([0.15, 0.25, -0.55]),
    'leg_fr_top': np.array([0.15, -0.25, -0.1]),
    'paw_fr': np.array([0.15, -0.25, -0.55]),
    'leg_bl_top': np.array([0.85, 0.25, -0.1]),
    'paw_bl': np.array([0.85, 0.25, -0.55]),
    'leg_br_top': np.array([0.85, -0.25, -0.1]),
    'paw_br': np.array([0.85, -0.25, -0.55]),

    # Tail
    'tail_base': np.array([1.1, 0, 0.1]),
    'tail_mid': np.array([1.3, 0.1, 0.3]),
    'tail_tip': np.array([1.5, 0.15, 0.4]),
}


def create_dog(points):
    """Create a 3D dog with proper proportions."""
    fig = go.Figure()

    body_color = 'goldenrod'
    leg_color = 'saddlebrown'
    head_color = 'wheat'
    nose_color = 'black'

    # ========== TORSO ==========
    x, y, z = cylinder_mesh(points['body_back'], points['body_mid'], radius=0.32, resolution=16)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))
    
    x, y, z = cylinder_mesh(points['body_front'], points['body_mid'], radius=0.30, resolution=16)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))
    
    x, y, z = sphere_mesh(points['body_mid'], radius=0.36, resolution=16)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))

    # ========== NECK ==========
    x, y, z = cylinder_mesh(points['body_front'], points['head_center'] + np.array([0.08, 0, -0.04]), 
                           radius=0.22, resolution=14)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=head_color, opacity=1, showlegend=False))

    # ========== HEAD: BROAD ELLIPSOID CRANIUM (not a lightbulb!) ==========
    # Large, round cranium: dog head is broader and rounder than a bulb
    x, y, z = ellipsoid_mesh(points['head_center'], rx=0.28, ry=0.24, rz=0.22, resolution=20)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=head_color, opacity=1, showlegend=False))

    # ========== SNOUT: SHORT AND BLUNT ==========
    # Short taper from muzzle base to nose tip (not elongated)
    x, y, z = tapered_cylinder_mesh(points['muzzle_base'], points['nose_tip'], 
                                   radius_start=0.11, radius_end=0.065, resolution=14)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=head_color, opacity=1, showlegend=False))

    # Muzzle base sphere (smooth junction between cranium and snout)
    x, y, z = sphere_mesh(points['muzzle_base'], radius=0.10, resolution=14)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=head_color, opacity=1, showlegend=False))

    # Nose tip: SMALL dark sphere (reads as a nose, not a mouth)
    x, y, z = sphere_mesh(points['nose_tip'], radius=0.035, resolution=10)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=nose_color, opacity=1, showlegend=False))

    # Nostrils: two tiny dark spheres
    nostril_l = points['nose_tip'] + np.array([-0.02, 0.025, 0.01])
    nostril_r = points['nose_tip'] + np.array([-0.02, -0.025, 0.01])
    for npos in [nostril_l, nostril_r]:
        x, y, z = sphere_mesh(npos, radius=0.012, resolution=8)
        fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=nose_color, opacity=1, showlegend=False))

    # ========== EARS ==========
    x, y, z = cylinder_mesh(points['head_center'] + np.array([-0.05, 0.22, 0.15]), points['ear_l'], 
                           radius=0.045, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=leg_color, opacity=1, showlegend=False))
    
    x, y, z = cylinder_mesh(points['head_center'] + np.array([-0.05, -0.22, 0.15]), points['ear_r'], 
                           radius=0.045, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=leg_color, opacity=1, showlegend=False))

    # ========== EYES ==========
    x, y, z = sphere_mesh(points['eye_l'], radius=0.032, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=nose_color, opacity=1, showlegend=False))
    
    x, y, z = sphere_mesh(points['eye_r'], radius=0.032, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=nose_color, opacity=1, showlegend=False))

    # ========== TAIL ==========
    x, y, z = cylinder_mesh(points['body_back'], points['tail_base'], radius=0.16, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))
    
    x, y, z = cylinder_mesh(points['tail_base'], points['tail_mid'], radius=0.10, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))
    
    x, y, z = cylinder_mesh(points['tail_mid'], points['tail_tip'], radius=0.06, resolution=12)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))
    
    x, y, z = sphere_mesh(points['tail_tip'], radius=0.07, resolution=10)
    fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=body_color, opacity=1, showlegend=False))

    # ========== LEGS ==========
    for prefix in ['fl', 'fr', 'bl', 'br']:
        if prefix in ['fl', 'fr']:
            body_attach = points['body_front']
        else:
            body_attach = points['body_back']
        
        paw_pos = points[f'paw_{prefix}']
        x, y, z = tapered_cylinder_mesh(body_attach, paw_pos, radius_start=0.13, radius_end=0.08, resolution=14)
        fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=leg_color, opacity=1, showlegend=False))
        
        # Paw
        x, y, z = sphere_mesh(paw_pos, radius=0.05, resolution=10)
        fig.add_trace(go.Mesh3d(x=x.flatten(), y=y.flatten(), z=z.flatten(), color=nose_color, opacity=1, showlegend=False))

    # ========== LAYOUT ==========
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-0.7, 1.8]),
            yaxis=dict(range=[-0.7, 0.7]),
            zaxis=dict(range=[-0.65, 0.55]),
            aspectmode='manual',
            aspectratio=dict(x=2.5, y=1.4, z=1.2)
        ),
        title='3D Dog with Proper Head Proportions',
        showlegend=False,
        hovermode='closest',
        margin=dict(l=0, r=0, b=0, t=50)
    )

    return fig


if __name__ == "__main__":
    fig = create_dog(points)
    fig.show()
