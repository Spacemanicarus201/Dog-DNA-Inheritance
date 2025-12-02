# ==============================
# Dog Genetics Dataset
# ==============================

# 1. Trait → Genotype mapping
TRAIT_TO_GENOTYPE = {
    # Coat Color (E locus)
    "Golden coat": {"E": ("e", "e")},
    "Black coat": {"E": ("E", "E")},
    "Masked face": {"E": ("Em", "Em")},

    # K locus (dominant black / brindle / yellow)
    "Dominant black": {"K": ("Kb", "Kb")},
    "Brindle": {"K": ("kbr", "kbr")},
    "Yellow/allow A locus": {"K": ("ky", "ky")},

    # A locus (pattern)
    "Sable/Fawn": {"A": ("Ay", "Ay")},
    "Tan-point": {"A": ("at", "at")},
    "Recessive black": {"A": ("a", "a")},

    # B locus (pigment)
    "Black eumelanin": {"B": ("B", "B")},
    "Brown eumelanin": {"B": ("b", "b")},

    # D locus (dilution)
    "Full color": {"D": ("D", "D")},
    "Diluted color": {"D": ("d", "d")},

    # M locus (merle)
    "Merle": {"M": ("M", "M")},
    "Non-merle": {"M": ("m", "m")},

    # H locus (hair/texture simplified)
    "Normal hair": {"H": ("H", "H")},
    "Long hair": {"H": ("h", "h")},
}

# 2. Default genotypes for each breed
BREED_DEFAULTS = {
    "Golden Retriever": {
        "E": ("e", "e"),
        "K": ("ky", "ky"),
        "A": ("Ay", "Ay"),
        "B": ("B", "B"),
        "D": ("D", "D"),
        "M": ("m", "m"),
        "H": ("H", "H"),
    },
    "Husky": {
        "E": ("E", "E"),
        "K": ("Kb", "Kb"),
        "A": ("at", "at"),
        "B": ("B", "b"),
        "D": ("d", "d"),
        "M": ("M", "M"),
        "H": ("H", "H"),
    },
    "German Shepherd": {
        "E": ("E", "E"),
        "K": ("Kb", "ky"),
        "A": ("at", "at"),
        "B": ("B", "B"),
        "D": ("D", "D"),
        "M": ("m", "m"),
        "H": ("H", "H"),
    },
    "Chihuahua": {
        "E": ("e", "e"),
        "K": ("ky", "ky"),
        "A": ("a", "a"),
        "B": ("b", "b"),
        "D": ("D", "D"),
        "M": ("m", "m"),
        "H": ("h", "h"),
    },
    "Toy Poodle": {
        "E": ("E", "E"),
        "K": ("ky", "ky"),
        "A": ("Ay", "Ay"),
        "B": ("B", "b"),
        "D": ("d", "d"),
        "M": ("m", "m"),
        "H": ("h", "h"),
    },
    "Dachshund": {
        "E": ("E", "e"),
        "K": ("ky", "ky"),
        "A": ("at", "at"),
        "B": ("B", "B"),
        "D": ("D", "D"),
        "M": ("m", "m"),
        "H": ("h", "h"),
    },
}

# 3. Categories for dropdown menus
TRAIT_CATEGORIES = {
    "Coat Color": ["Golden coat", "Black coat", "Masked face"],
    "K Locus (dominant/allow)": ["Dominant black", "Brindle", "Yellow/allow A locus"],
    "Pattern (A locus)": ["Sable/Fawn", "Tan-point", "Recessive black"],
    "Pigment (B locus)": ["Black eumelanin", "Brown eumelanin"],
    "Dilution (D locus)": ["Full color", "Diluted color"],
    "Merle (M locus)": ["Merle", "Non-merle"],
    "Hair Length (H locus)": ["Normal hair", "Long hair"],
}
