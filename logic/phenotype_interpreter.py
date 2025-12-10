"""phenotype_interpreter.py

Converts dog genotype to human-readable phenotype descriptions.
"""

from typing import Dict, Tuple


class PhenotypeInterpreter:
    """Interprets dog genotype into natural language descriptions."""
    
    @staticmethod
    def interpret_coat_color(genotype: Dict[str, Tuple[str, str]]) -> str:
        """
        Determine the coat color based on E, K, A, B, D loci.
        
        Epistasis hierarchy:
        1. E locus (extension) - if e/e, dog is red/cream regardless of other loci
        2. K locus (dominance) - if Kb present, solid color (ignores A locus)
        3. A locus (agouti) - pattern if K allows
        4. B locus (brown) - modifies black to brown
        5. D locus (dilution) - dilutes the color
        """
        E = genotype.get("E", ("E", "E"))
        K = genotype.get("K", ("ky", "ky"))
        A = genotype.get("A", ("Ay", "Ay"))
        B = genotype.get("B", ("B", "B"))
        D = genotype.get("D", ("D", "D"))
        
        # E locus check - recessive red overrides everything
        if E == ("e", "e"):
            base_color = "golden/red"
        else:
            # Determine base pigment color
            if "B" in B:
                base_pigment = "black"
            else:  # b/b
                base_pigment = "brown/liver"
            
            # K locus - dominant black
            if "Kb" in K:
                base_color = f"solid {base_pigment}"
            elif "kbr" in K and K != ("ky", "ky"):
                base_color = f"brindle ({base_pigment} stripes)"
            else:  # ky/ky - A locus expressed
                # A locus patterns
                if "Ay" in A:
                    base_color = f"sable/fawn ({base_pigment} tips)"
                elif "aw" in A:
                    base_color = f"wolf sable ({base_pigment} banding)"
                elif "at" in A:
                    base_color = f"{base_pigment} with tan points"
                elif A == ("a", "a"):
                    base_color = f"recessive {base_pigment}"
                else:
                    base_color = base_pigment
        
        # D locus - dilution
        if D == ("d", "d"):
            if "black" in base_color:
                base_color = base_color.replace("black", "blue/gray")
            elif "brown" in base_color or "liver" in base_color:
                base_color = base_color.replace("brown", "isabella/lilac").replace("liver", "isabella/lilac")
            elif "golden" in base_color or "red" in base_color:
                base_color = base_color.replace("golden", "cream").replace("red", "cream")
        
        return base_color
    
    @staticmethod
    def interpret_pattern(genotype: Dict[str, Tuple[str, str]]) -> str:
        """Determine white spotting pattern from S locus."""
        S = genotype.get("S", ("S", "S"))
        M = genotype.get("M", ("m", "m"))
        
        patterns = []
        
        # Merle pattern
        if "M" in M:
            if M == ("M", "M"):
                patterns.append("double merle (extensive white, health risks)")
            else:
                patterns.append("merle patches")
        
        # White spotting
        if S == ("S", "S"):
            patterns.append("solid (no white)")
        elif "si" in S:
            patterns.append("Irish spotting (white chest/feet)")
        elif "sp" in S:
            patterns.append("piebald (significant white patches)")
        elif "sw" in S:
            patterns.append("extreme white (mostly white)")
        
        return ", ".join(patterns) if patterns else "solid (no white)"
    
    @staticmethod
    def interpret_coat_length(genotype: Dict[str, Tuple[str, str]]) -> str:
        """Determine coat length from L locus."""
        L = genotype.get("L", ("L", "L"))
        
        if L == ("l", "l"):
            return "long/fluffy coat"
        elif "l" in L:
            return "short coat (carries long)"
        else:
            return "short coat"
    
    @staticmethod
    def interpret_mask(genotype: Dict[str, Tuple[str, str]]) -> str:
        """Determine if dog has facial mask from E locus."""
        E = genotype.get("E", ("E", "E"))
        
        if "Em" in E:
            return "dark facial mask"
        return None
    
    @staticmethod
    def get_full_description(genotype: Dict[str, Tuple[str, str]]) -> str:
        """
        Generate a complete, natural language description of the dog's appearance.
        
        Example: "This dog will have a solid black body with short coat and dark facial mask"
        """
        parts = []
        
        # Coat color
        color = PhenotypeInterpreter.interpret_coat_color(genotype)
        parts.append(f"{color} coat")
        
        # Pattern
        pattern = PhenotypeInterpreter.interpret_pattern(genotype)
        if pattern and pattern != "solid (no white)":
            parts.append(f"with {pattern}")
        
        # Coat length
        length = PhenotypeInterpreter.interpret_coat_length(genotype)
        parts.append(length)
        
        # Mask
        mask = PhenotypeInterpreter.interpret_mask(genotype)
        if mask:
            parts.append(f"and {mask}")
        
        # Combine into sentence
        description = "This dog will have a " + ", ".join(parts[:-1])
        if len(parts) > 1:
            description += f", {parts[-1]}"
        else:
            description += parts[0]
        
        description += "."
        
        return description
    
    @staticmethod
    def get_simple_description(genotype: Dict[str, Tuple[str, str]]) -> str:
        """
        Generate a shorter description focusing on main features.
        
        Example: "Solid black, short coat"
        """
        color = PhenotypeInterpreter.interpret_coat_color(genotype)
        length = PhenotypeInterpreter.interpret_coat_length(genotype)
        
        # Simplify length
        if "long" in length:
            length_simple = "long coat"
        else:
            length_simple = "short coat"
        
        return f"{color.capitalize()}, {length_simple}"


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_genotypes = [
        {
            "name": "Classic Labrador",
            "genotype": {
                "E": ("E", "E"),
                "K": ("Kb", "Kb"),
                "A": ("Ay", "Ay"),
                "B": ("B", "B"),
                "D": ("D", "D"),
                "M": ("m", "m"),
                "S": ("S", "S"),
                "L": ("L", "L")
            }
        },
        {
            "name": "Golden Retriever",
            "genotype": {
                "E": ("e", "e"),
                "K": ("ky", "ky"),
                "A": ("Ay", "Ay"),
                "B": ("B", "B"),
                "D": ("D", "D"),
                "M": ("m", "m"),
                "S": ("S", "S"),
                "L": ("l", "l")
            }
        },
        {
            "name": "German Shepherd",
            "genotype": {
                "E": ("E", "E"),
                "K": ("ky", "ky"),
                "A": ("at", "at"),
                "B": ("B", "B"),
                "D": ("D", "D"),
                "M": ("m", "m"),
                "S": ("S", "S"),
                "L": ("L", "L")
            }
        },
        {
            "name": "Blue Merle Border Collie",
            "genotype": {
                "E": ("E", "E"),
                "K": ("ky", "ky"),
                "A": ("at", "at"),
                "B": ("B", "B"),
                "D": ("D", "D"),
                "M": ("M", "m"),
                "S": ("S", "S"),
                "L": ("L", "L")
            }
        }
    ]
    
    interpreter = PhenotypeInterpreter()
    
    print("=" * 70)
    print("Dog Phenotype Interpreter - Test Cases")
    print("=" * 70)
    
    for test in test_genotypes:
        print(f"\n{test['name']}:")
        print(f"  Full: {interpreter.get_full_description(test['genotype'])}")
        print(f"  Simple: {interpreter.get_simple_description(test['genotype'])}")
