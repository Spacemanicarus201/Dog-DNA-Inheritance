"""
Simple visual mapping from genotype dict (locus -> allele tuple)
to visualization parameters for the DogModel/OpenGL renderer.

This is intentionally small and adjustable. It provides:
- body_color: (r,g,b) floats 0..1
- head_color: (r,g,b)
- leg_scale: multiplicative factor for leg length
- ear_scale: multiplicative factor for ear size
- snout_forward: additive x offset to push the snout forward
- spotted: bool for white spotting
"""

import numpy as np

# Simple palette helpers
PALETTES = {
    'golden': (0.92, 0.7, 0.2),
    'brown': (0.45, 0.25, 0.07),
    'black': (0.05, 0.05, 0.05),
    'white': (0.95, 0.95, 0.95),
    'gray': (0.6, 0.6, 0.65),
    'wheat': (0.96, 0.87, 0.7),
    'blue': (0.35, 0.4, 0.5),  # Diluted black
    'isabella': (0.55, 0.45, 0.4),  # Diluted brown
}


def mix_colors(c1, c2, t=0.5):
    return tuple((1-t)*np.array(c1) + t*np.array(c2))


def compute_visual_params_from_offspring(offspring_genotype: dict) -> dict:
    """
    Compute visualization parameters from a SINGLE offspring genotype.
    
    Input: offspring_genotype: dict mapping locus -> (allele1, allele2) tuple
    Example: {"E": ("E", "e"), "K": ("Kb", "ky"), "B": ("B", "b"), ...}
    
    Returns: dict with visual parameters for DogModel
    """
    # Default params
    params = {
        'body_color': PALETTES['golden'],
        'head_color': PALETTES['golden'],
        'leg_scale': 1.0,
        'ear_scale': 1.0,
        'snout_forward': 0.12,
        'spotted': False,
        'spot_pattern': None,  # 'si', 'sp', 'sw' or None
        'merle': False,
    }
    
    def has_allele(locus, allele_str):
        """Check if genotype has specific allele at locus."""
        if locus not in offspring_genotype:
            return False
        alleles = offspring_genotype[locus]
        if isinstance(alleles, tuple):
            return any(str(x) == allele_str for x in alleles)
        return str(alleles) == allele_str
    
    # --- COAT COLOR LOGIC (following epistasis hierarchy) ---
    
    # 1. E locus (extension) - e/e overrides everything
    E = offspring_genotype.get("E", ("E", "E"))
    if E == ("e", "e"):
        # Recessive red/golden
        params['body_color'] = PALETTES['golden']
        params['head_color'] = mix_colors(PALETTES['golden'], PALETTES['white'], 0.1)
        # Skip other color logic
    else:
        # 2. K locus (dominance) - Kb overrides A locus
        K = offspring_genotype.get("K", ("ky", "ky"))
        
        if "Kb" in K:
            # Dominant black - solid color
            base_color = PALETTES['black']
        elif "kbr" in K and K != ("ky", "ky"):
            # Brindle pattern
            base_color = mix_colors(PALETTES['brown'], PALETTES['golden'], 0.4)
        else:
            # ky/ky - A locus expressed
            A = offspring_genotype.get("A", ("Ay", "Ay"))
            
            if "Ay" in A:
                # Sable/fawn
                base_color = mix_colors(PALETTES['golden'], PALETTES['brown'], 0.3)
            elif "aw" in A:
                # Wolf sable
                base_color = mix_colors(PALETTES['gray'], PALETTES['brown'], 0.4)
            elif "at" in A:
                # Tan points
                base_color = PALETTES['black']
            elif A == ("a", "a"):
                # Recessive black
                base_color = PALETTES['black']
            else:
                base_color = PALETTES['golden']
        
        # 3. B locus (brown/liver) - modifies black to brown
        B = offspring_genotype.get("B", ("B", "B"))
        if B == ("b", "b"):
            # Homozygous brown - convert black to brown
            if base_color == PALETTES['black']:
                base_color = PALETTES['brown']
        
        # 4. D locus (dilution) - dilutes the color
        D = offspring_genotype.get("D", ("D", "D"))
        if D == ("d", "d"):
            # Diluted
            if base_color == PALETTES['black']:
                base_color = PALETTES['blue']
            elif base_color == PALETTES['brown']:
                base_color = PALETTES['isabella']
            else:
                # Dilute other colors
                base_color = mix_colors(base_color, PALETTES['gray'], 0.4)
        
        params['body_color'] = base_color
        params['head_color'] = base_color
    
    # 5. M locus (merle) - creates patches
    M = offspring_genotype.get("M", ("m", "m"))
    if "M" in M:
        params['merle'] = True
        # Lighten body color for merle effect
        params['body_color'] = mix_colors(params['body_color'], PALETTES['white'], 0.25)
        
        # Double merle - even lighter
        if M == ("M", "M"):
            params['body_color'] = mix_colors(params['body_color'], PALETTES['white'], 0.4)
            params['head_color'] = mix_colors(params['head_color'], PALETTES['white'], 0.4)
    
    # 6. S locus (white spotting)
    S = offspring_genotype.get("S", ("S", "S"))
    if S != ("S", "S"):
        params['spotted'] = True
        
        if "sw" in S:
            # Extreme white
            params['spot_pattern'] = 'sw'
            params['body_color'] = PALETTES['white']
            params['head_color'] = PALETTES['white']
        elif "sp" in S:
            # Piebald - lighten body significantly
            params['spot_pattern'] = 'sp'
            params['body_color'] = mix_colors(params['body_color'], PALETTES['white'], 0.4)
        elif "si" in S:
            # Irish spotting - subtle lightening
            params['spot_pattern'] = 'si'
            params['body_color'] = mix_colors(params['body_color'], PALETTES['white'], 0.15)
    
    # 7. L locus (coat length) - affects leg color to show "fluffiness"
    L = offspring_genotype.get("L", ("L", "L"))
    if L == ("l", "l"):
        # Long coat - lighter, "fluffier" appearance
        params['leg_scale'] = 1.15
        params['ear_scale'] = 1.15
        # Make legs lighter to simulate fluffy fur
        params['leg_color'] = mix_colors(params['body_color'], PALETTES['wheat'], 0.3)
    elif "l" in L:
        # Carrier (L/l) - medium coat
        params['leg_scale'] = 1.08
        params['ear_scale'] = 1.08
        params['leg_color'] = mix_colors(params['body_color'], PALETTES['wheat'], 0.15)
    else:
        # Short coat - darker legs
        params['leg_color'] = mix_colors(params['body_color'], PALETTES['brown'], 0.2)
    
    # 8. A locus tan-point affects snout and leg color
    A = offspring_genotype.get("A", ("Ay", "Ay"))
    if "at" in A:
        # Tan points - lighter legs and snout
        params['snout_forward'] = 0.06
        params['leg_color'] = mix_colors(PALETTES['wheat'], PALETTES['golden'], 0.5)
    elif "aw" in A:
        # Wolf sable - grizzled appearance
        params['snout_forward'] = 0.10
        params['leg_color'] = mix_colors(params['body_color'], PALETTES['gray'], 0.3)
    elif "a" in A and A == ("a", "a"):
        # Recessive black - uniform dark
        params['snout_forward'] = 0.12
        params['leg_color'] = params['body_color']
    else:
        # Sable/fawn - normal
        params['snout_forward'] = 0.12
        if 'leg_color' not in params:
            params['leg_color'] = mix_colors(params['body_color'], PALETTES['brown'], 0.2)
    
    # Ensure leg_color is always set
    if 'leg_color' not in params:
        params['leg_color'] = mix_colors(params['body_color'], PALETTES['brown'], 0.2)
    
    return params


def compute_visual_params(father_genes: dict, mother_genes: dict) -> dict:
    """
    Compute visualization from parent genotypes (for compatibility).
    
    Creates a deterministic "average" offspring by combining dominant alleles.
    This prevents flickering since it returns the same result every time.
    
    For actual offspring, use compute_visual_params_from_offspring() instead.
    """
    # Create a deterministic offspring by picking dominant alleles
    all_loci = set(father_genes.keys()) | set(mother_genes.keys())
    offspring = {}
    
    # Dominance order for common alleles (most dominant first)
    dominance = {
        'E': ['Em', 'E', 'e'],
        'K': ['Kb', 'kbr', 'ky'],
        'A': ['Ay', 'aw', 'at', 'a'],
        'B': ['B', 'b'],
        'D': ['D', 'd'],
        'M': ['M', 'm'],
        'S': ['S', 'si', 'sp', 'sw'],
        'L': ['L', 'l'],
    }
    
    for locus in all_loci:
        father_alleles = father_genes.get(locus, ('?', '?'))
        mother_alleles = mother_genes.get(locus, ('?', '?'))
        
        # Get all possible alleles
        all_alleles = []
        if isinstance(father_alleles, tuple):
            all_alleles.extend(father_alleles)
        else:
            all_alleles.append(father_alleles)
        
        if isinstance(mother_alleles, tuple):
            all_alleles.extend(mother_alleles)
        else:
            all_alleles.append(mother_alleles)
        
        # Remove duplicates and unknowns
        all_alleles = [a for a in set(all_alleles) if a != '?']
        
        if not all_alleles:
            continue
        
        # Sort by dominance if we have dominance info for this locus
        if locus in dominance:
            # Sort alleles by their position in dominance list
            def dominance_key(allele):
                try:
                    return dominance[locus].index(allele)
                except ValueError:
                    return 999  # Unknown alleles go to end
            
            all_alleles.sort(key=dominance_key)
        
        # Pick the two most dominant alleles (or same if only one)
        if len(all_alleles) >= 2:
            offspring[locus] = tuple(sorted([all_alleles[0], all_alleles[1]]))
        else:
            offspring[locus] = (all_alleles[0], all_alleles[0])
    
    return compute_visual_params_from_offspring(offspring)
