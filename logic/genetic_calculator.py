import itertools
import random
from collections import Counter
from genome_library import TRAIT_TO_GENOTYPE, BREED_DEFAULTS
from utils.debug import debug


class GeneticCalculator:
    def __init__(self):
        debug("\n=== GeneticCalculator INIT ===")
        self.reverse = {}
        for trait, mapping in TRAIT_TO_GENOTYPE.items():
            for locus, alleles in mapping.items():
                key = (locus, tuple(sorted(alleles)))
                self.reverse.setdefault(key, []).append(trait)
        debug("Reverse lookup table generated:", self.reverse)

    # ----------------------------------------------------------------------
    # Fills missing genotype loci based on BREED_DEFAULTS so screens don't crash
    # ----------------------------------------------------------------------
    def complete_genotype(self, defaults: dict):
        """
        If a breed has only some of the loci defined, fill the rest with AA by default.
        This prevents UI crashes when dataset updates are incomplete.
        """
        debug("\n--- Completing genotype from defaults ---")
        final = {}

        # fill defined traits first
        for locus, alleles in defaults.items():
            final[locus] = tuple(alleles)

        # auto-fill missing loci (prevent crashes)
        for trait, mapping in TRAIT_TO_GENOTYPE.items():
            for locus, alleles in mapping.items():
                if locus not in final:
                    final[locus] = ("A", "A")   # safe neutral placeholder
                    debug(f" auto-filled missing locus {locus} → ('A','A')")

        debug("→ Completed genotype:", final)
        return final

    # ----------------------------------------------------------------------
    # Combine default breed genotype + manual overrides
    # ----------------------------------------------------------------------
    def combine_defaults_with_overrides(self, defaults, overrides):
        debug("\n--- Combining defaults + overrides ---")
        merged = {}
        if defaults:
            merged.update({k: tuple(v) for k, v in defaults.items()})
        if overrides:
            merged.update({k: tuple(v) for k, v in overrides.items()})
        debug("→ Final merged:", merged)
        return merged

    # ----------------------------------------------------------------------
    # Genotype → readable phenotype
    # ----------------------------------------------------------------------
    def genotype_to_readable(self, genotype):
        debug("\n--- Converting genotype to readable phenotype ---")
        result = {}
        for locus, alleles in genotype.items():
            key = (locus, tuple(sorted(alleles)))
            readable = self.reverse.get(key, [None])[0]
            result[locus] = readable
            debug(f"  Locus {locus}: {alleles} → {readable}")
        return result

    def phenotype_string(self, genotype):
        data = self.genotype_to_readable(genotype)
        traits = [t for t in data.values() if t]
        return ", ".join(traits) if traits else ", ".join(f"{l}:{'/'.join(genotype[l])}" for l in genotype)

    # ----------------------------------------------------------------------
    # Punnett Square
    # ----------------------------------------------------------------------
    def punnett_square(self, parent1, parent2):
        debug("\n=== Punnett Square Generation ===")
        punnett = {}
        for locus in parent1.keys():
            if locus not in parent2:
                continue

            a, b = parent1[locus], parent2[locus]
            combos = list(itertools.product(a, b))
            count = Counter(combos)
            total = sum(count.values())
            punnett[locus] = []

            for geno, qty in count.items():
                child_geno = tuple(sorted(geno))
                trait = self.reverse.get((locus, child_geno), ["Unknown"])[0]
                prob = (qty / total) * 100
                punnett[locus].append({
                    "genotype": f"{child_geno[0]}{child_geno[1]}",
                    "probability": f"{prob:.0f}%",
                    "trait": trait
                })

        return punnett

    # ----------------------------------------------------------------------
    # Monte-Carlo Simulation
    # ----------------------------------------------------------------------
    def monte_carlo(self, parent1, parent2, samples=6):
        debug("\n=== Monte Carlo Simulation ===")
        children = []
        loci = [l for l in parent1.keys() if l in parent2]

        for _ in range(samples):
            geno = {}
            for locus in loci:
                a = random.choice(parent1[locus])
                b = random.choice(parent2[locus])
                geno[locus] = tuple(sorted((a, b)))
            phenotype = self.phenotype_string(geno)
            children.append({"genotype": geno, "phenotype": phenotype})
        return children

    # ----------------------------------------------------------------------
    # Bayesian phenotype probability
    # ----------------------------------------------------------------------
    def bayesian_probability(self, phenotype, punnett):
        posterior = {}
        total = 0

        for locus, options in punnett.items():
            for item in options:
                if item["trait"] == phenotype:
                    prob = int(item["probability"].replace("%", ""))
                    posterior[locus] = posterior.get(locus, 0) + prob
                    total += prob

        if not posterior or total == 0:
            return {}

        return {locus: f"{(v / total) * 100:.0f}%" for locus, v in posterior.items()}

    # ----------------------------------------------------------------------
    # Similarity scoring
    # ----------------------------------------------------------------------
    def similarity(self, phenotype_a, phenotype_b):
        set_a = set(phenotype_a.split(", "))
        set_b = set(phenotype_b.split(", "))
        inter = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return inter / union if union else 0

    # ----------------------------------------------------------------------
    # Unified system report
    # ----------------------------------------------------------------------
    def generate_summary(self, father_genes, mother_genes, samples=6):
        punnett = self.punnett_square(father_genes, mother_genes)
        monte = self.monte_carlo(father_genes, mother_genes, samples)

        father_str = ", ".join(self.genotype_to_readable(father_genes).values())
        mother_str = ", ".join(self.genotype_to_readable(mother_genes).values())

        for child in monte:
            child["similarity"] = {
                "father": self.similarity(child["phenotype"], father_str),
                "mother": self.similarity(child["phenotype"], mother_str),
                "bayesian": self.bayesian_probability(child["phenotype"], punnett)
            }

        return punnett, monte, [c["phenotype"] for c in monte]
