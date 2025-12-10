# ==========================
# genome_library.py  (FIXED)
# ==========================

# 1. Trait → Genotype mapping (dropdown → alleles)
TRAIT_TO_GENOTYPE = {
    # E locus
    "Black coat (full extension)": {"E": ("E", "E")},
    "Black carries red": {"E": ("E", "e")},
    "Golden/Recessive Red": {"E": ("e", "e")},
    "Masked face": {"E": ("Em", "Em")},
    "Masked face (carrier)": {"E": ("Em", "E")},
    "Masked face (red carrier)": {"E": ("Em", "e")},

    # K locus
    "Dominant solid black": {"K": ("Kb", "Kb")},
    "Dominant black carries agouti": {"K": ("Kb", "ky")},
    "Dominant black carries brindle": {"K": ("Kb", "kbr")},
    "Brindle": {"K": ("kbr", "kbr")},
    "Brindle carries agouti": {"K": ("kbr", "ky")},
    "Allows A Locus expression": {"K": ("ky", "ky")},

    # A locus
    "Sable/Fawn": {"A": ("Ay", "Ay")},
    "Sable carries wolf sable": {"A": ("Ay", "aw")},
    "Sable carries tan-point": {"A": ("Ay", "at")},
    "Sable carries recessive black": {"A": ("Ay", "a")},
    "Wolf Sable": {"A": ("aw", "aw")},
    "Wolf Sable carries tan-point": {"A": ("aw", "at")},
    "Tan-point": {"A": ("at", "at")},
    "Recessive black": {"A": ("a", "a")},

    # B locus
    "Black eumelanin": {"B": ("B", "B")},
    "Black carries brown": {"B": ("B", "b")},
    "Brown/Liver eumelanin": {"B": ("b", "b")},

    # D locus
    "Full color": {"D": ("D", "D")},
    "Full color carries dilution": {"D": ("D", "d")},
    "Diluted color (Blue/Isabella)": {"D": ("d", "d")},

    # M locus
    "Merle": {"M": ("M", "m")},
    "Double Merle (risk)": {"M": ("M", "M")},
    "Non-merle (Solid)": {"M": ("m", "m")},

    # S locus
    "Solid coat": {"S": ("S", "S")},
    "Solid carries piebald": {"S": ("S", "sp")},
    "Irish Spotting": {"S": ("si", "si")},
    "Piebald Spotting": {"S": ("sp", "sp")},
    "Extreme White": {"S": ("sw", "sw")},

    # L locus
    "Short coat": {"L": ("L", "L")},
    "Short coat carries long": {"L": ("L", "l")},
    "Long coat": {"L": ("l", "l")},
}


# 2. Translating alleles → phenotype text
ALLELE_TRANSLATOR = {
    "E": {"Em": "Masked face", "E": "Black coat", "e": "Golden/Recessive red"},
    "K": {"Kb": "Solid black", "kbr": "Brindle", "ky": "Agouti pattern allowed"},
    "A": {"Ay": "Sable/Fawn", "aw": "Wolf sable", "at": "Tan-point", "a": "Recessive black"},
    "B": {"B": "Black eumelanin", "b": "Brown/Liver eumelanin"},
    "D": {"D": "Full color", "d": "Diluted color"},
    "M": {"M": "Merle", "m": "Non-merle"},
    "S": {"S": "Solid coat", "si": "Irish spotting", "sp": "Piebald spotting", "sw": "Extreme white"},
    "L": {"L": "Short coat", "l": "Long coat"},
}

# Used by GeneticSummary to produce readable text
def alleles_to_text(locus, a1, a2):
    table = ALLELE_TRANSLATOR.get(locus, {})
    if a1 == a2:
        return table.get(a1, a1)
    dom = table.get(a1, "Unknown")
    rec = table.get(a2, "Unknown")
    return f"{dom} (carries {rec.lower()})"


# 3. Breed defaults — fixed using lowercase-accurate alleles
BREED_DEFAULTS = {
    "Labrador Retriever": {"E": ("E","E"), "K": ("Kb","Kb"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("D","D")},
    "German Shepherd": {"E": ("E","E"), "K": ("Kb","ky"), "A": ("Ay","at"), "B": ("B","B"), "D": ("D","D")},
    "Siberian Husky": {"E": ("E","E"), "K": ("ky","ky"), "A": ("aw","aw"), "B": ("B","B"), "D": ("d","d")},
    "Golden Retriever": {"E": ("e","e"), "K": ("ky","ky"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("D","D")},
    "Rottweiler": {"E": ("E","E"), "K": ("Kb","Kb"), "A": ("at","at"), "B": ("B","B"), "D": ("D","D")},
    "Great Dane": {"E": ("E","E"), "K": ("Kb","Kb"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("d","d")},
    "French Bulldog": {"E": ("E","E"), "K": ("kbr","kbr"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("D","D")},
    "Poodle": {"E": ("e","e"), "K": ("ky","ky"), "A": ("Ay","Ay"), "B": ("b","b"), "D": ("D","D")},
    "Border Collie": {"E": ("E","E"), "K": ("ky","ky"), "A": ("at","at"), "B": ("B","B"), "D": ("D","D")},
    "Beagle": {"E": ("E","E"), "K": ("ky","ky"), "A": ("aw","aw"), "B": ("B","B"), "D": ("D","D")},
    "Doberman": {"E": ("E","E"), "K": ("Kb","Kb"), "A": ("at","at"), "B": ("b","b"), "D": ("d","d")},
    "Weimaraner": {"E": ("E","E"), "K": ("Kb","Kb"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("d","d")},
    "Dalmatian": {"E": ("E","E"), "K": ("ky","ky"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("D","D")},
    "Boxer": {"E": ("E","e"), "K": ("kbr","kbr"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("D","D")},
    "Shiba Inu": {"E": ("E","E"), "K": ("ky","ky"), "A": ("Ay","Ay"), "B": ("B","B"), "D": ("D","D")},
    "Pitbull": {"E": ("E","E"), "K": ("Kb","ky"), "A": ("at","at"), "B": ("b","b"), "D": ("d","d")},
}

# 4. Trait options for dropdowns
TRAIT_CATEGORIES = {
    "Coat Color (E locus)": [
        "Black coat (full extension)", "Black carries red", "Golden/Recessive Red",
        "Masked face", "Masked face (carrier)", "Masked face (red carrier)"
    ],
    "K Locus (Dominance)": [
        "Dominant solid black", "Dominant black carries agouti",
        "Dominant black carries brindle", "Brindle", "Brindle carries agouti",
        "Allows A Locus expression"
    ],
    "Pattern (A locus)": [
        "Sable/Fawn", "Sable carries wolf sable", "Sable carries tan-point",
        "Sable carries recessive black", "Wolf Sable", "Wolf Sable carries tan-point",
        "Tan-point", "Recessive black"
    ],
    "Pigment (B locus)": [
        "Black eumelanin", "Black carries brown", "Brown/Liver eumelanin"
    ],
    "Dilution (D locus)": [
        "Full color", "Full color carries dilution", "Diluted color (Blue/Isabella)"
    ],
    "Merle (M locus)": [
        "Merle", "Double Merle (risk)", "Non-merle (Solid)"
    ],
    "Spotting (S locus)": [
        "Solid coat", "Solid carries piebald", "Irish Spotting",
        "Piebald Spotting", "Extreme White"
    ],
    "Coat Length (L locus)": [
        "Short coat", "Short coat carries long", "Long coat"
    ],
}
