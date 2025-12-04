# ==============================
# Dog Genetics Dataset (FINAL TRANSLATION)
# ==============================

# 1. Trait → Genotype mapping (Includes heterozygous/carrier states)
TRAIT_TO_GENOTYPE = {
    # ------------------------------------------------------------------
    # E Locus (Extension: Em > E > e)
    # ------------------------------------------------------------------
    "Black coat (full extension)": {"E": ("E", "E")},
    "Black carries red": {"E": ("E", "e")},
    "Golden/Recessive Red": {"E": ("e", "e")},
    "Masked face": {"E": ("Em", "Em")},
    "Masked face (carrier)": {"E": ("Em", "E")},
    "Masked face (red carrier)": {"E": ("Em", "e")}, # Implies dominance order

    # ------------------------------------------------------------------
    # K Locus (Dominant Black: Kb > kbr > ky)
    # ------------------------------------------------------------------
    "Dominant solid black": {"K": ("Kb", "Kb")},
    "Dominant black carries agouti": {"K": ("Kb", "ky")},
    "Dominant black carries brindle": {"K": ("Kb", "kbr")},
    "Brindle": {"K": ("kbr", "kbr")},
    "Brindle carries agouti": {"K": ("kbr", "ky")},
    "Allows A Locus expression": {"K": ("ky", "ky")},

    # ------------------------------------------------------------------
    # A Locus (Pattern: Ay > aw > at > a)
    # ------------------------------------------------------------------
    "Sable/Fawn": {"A": ("Ay", "Ay")},
    "Sable carries wolf sable": {"A": ("Ay", "aw")},
    "Sable carries tan-point": {"A": ("Ay", "at")},
    "Sable carries recessive black": {"A": ("Ay", "a")},
    "Wolf Sable": {"A": ("aw", "aw")},
    "Wolf Sable carries tan-point": {"A": ("aw", "at")},
    "Tan-point": {"A": ("at", "at")},
    "Recessive black": {"A": ("a", "a")},

    # ------------------------------------------------------------------
    # B Locus (Pigment: B > b)
    # ------------------------------------------------------------------
    "Black eumelanin": {"B": ("B", "B")},
    "Black carries brown": {"B": ("B", "b")},
    "Brown/Liver eumelanin": {"B": ("b", "b")},

    # ------------------------------------------------------------------
    # D Locus (Dilution: D > d)
    # ------------------------------------------------------------------
    "Full color": {"D": ("D", "D")},
    "Full color carries dilution": {"D": ("D", "d")},
    "Diluted color (Blue/Isabella)": {"D": ("d", "d")},

    # ------------------------------------------------------------------
    # M Locus (Merle: M > m)
    # ------------------------------------------------------------------
    "Merle": {"M": ("M", "m")},
    "Double Merle (risk)": {"M": ("M", "M")},
    "Non-merle (Solid)": {"M": ("m", "m")},

    # ------------------------------------------------------------------
    # S Locus (Spotting: S > si > sp > sw) - NEW ALLELES
    # ------------------------------------------------------------------
    "Solid coat": {"S": ("S", "S")},
    "Solid carries piebald": {"S": ("S", "sp")},
    "Irish Spotting": {"S": ("si", "si")},
    "Piebald Spotting": {"S": ("sp", "sp")},
    "Extreme White": {"S": ("sw", "sw")},
    
    # ------------------------------------------------------------------
    # L Locus (Coat Length: L > l)
    # ------------------------------------------------------------------
    "Short coat": {"L": ("L", "L")},
    "Short coat carries long": {"L": ("L", "l")},
    "Long coat": {"L": ("l", "l")},
}

# 2. Default genotypes for each breed (L and S loci retained from previous step)
BREED_DEFAULTS = {
    "Golden Retriever": {
        "E": ("e", "e"), "K": ("ky", "ky"), "A": ("Ay", "Ay"), "B": ("B", "B"), 
        "D": ("D", "D"), "M": ("m", "m"), "S": ("S", "S"), "L": ("l", "l"),
    },
    "Husky": {
        "E": ("E", "E"), "K": ("Kb", "Kb"), "A": ("at", "at"), "B": ("B", "b"), 
        "D": ("d", "d"), "M": ("M", "M"), "S": ("S", "S"), "L": ("L", "L"),
    },
    "German Shepherd": {
        "E": ("E", "E"), "K": ("Kb", "ky"), "A": ("at", "at"), "B": ("B", "B"), 
        "D": ("D", "D"), "M": ("m", "m"), "S": ("S", "S"), "L": ("L", "L"),
    },
    "Chihuahua": {
        "E": ("e", "e"), "K": ("ky", "ky"), "A": ("a", "a"), "B": ("b", "b"), 
        "D": ("D", "D"), "M": ("m", "m"), "S": ("S", "S"), "L": ("l", "l"),
    },
    "Toy Poodle": {
        "E": ("E", "E"), "K": ("ky", "ky"), "A": ("Ay", "Ay"), "B": ("B", "b"), 
        "D": ("d", "d"), "M": ("m", "m"), "S": ("S", "S"), "L": ("l", "l"),
    },
    "Dachshund": {
        "E": ("E", "e"), "K": ("ky", "ky"), "A": ("at", "at"), "B": ("B", "B"), 
        "D": ("D", "D"), "M": ("m", "m"), "S": ("S", "S"), "L": ("l", "l"),
    },
    "Great Dane": {
        "E": ('Em', 'Em'), "K": ('KB', 'KB'), "A": ('Ay', 'Ay'), "B": ('B', 'B'), 
        "D": ('D', 'D'), "S": ('S', 'S'), "L": ('L', 'L'), "M": ('m', 'm'),
    },
    "Weimaraner": {
        "E": ('E', 'E'), "K": ('KB', 'KB'), "A": ("Ay", "Ay"), "B": ('b', 'b'), 
        "D": ('d', 'd'), "S": ('S', 'S'), "L": ('L', 'L'), "M": ('m', 'm'),
    },
}

# 3. Categories for dropdown menus (Updated to include new traits)
TRAIT_CATEGORIES = {
    "Coat Color (E locus)": ["Black coat (full extension)", "Black carries red", "Golden/Recessive Red", "Masked face"],
    "K Locus (Dominance)": ["Dominant solid black", "Dominant black carries agouti", "Brindle", "Allows A Locus expression"],
    "Pattern (A locus)": ["Sable/Fawn", "Wolf Sable", "Tan-point", "Recessive black"],
    "Pigment (B locus)": ["Black eumelanin", "Black carries brown", "Brown/Liver eumelanin"],
    "Dilution (D locus)": ["Full color", "Full color carries dilution", "Diluted color (Blue/Isabella)"],
    "Merle (M locus)": ["Merle", "Double Merle (risk)", "Non-merle (Solid)"],
    "Spotting (S locus)": ["Solid coat", "Irish Spotting", "Piebald Spotting", "Extreme White"],
    "Coat Length (L locus)": ["Short coat", "Short coat carries long", "Long coat"],
}