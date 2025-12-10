import itertools
import random
from collections import Counter
from genome_library import TRAIT_TO_GENOTYPE, BREED_DEFAULTS
from utils.debug import debug

class GeneticCalculator:
    def __init__(self):
        debug("\n=== GeneticCalculator INIT ===")
        self.reverse = {}

        # Build reverse lookup table: (Locus, tuple sorted alleles) → trait list
        for trait, mapping in TRAIT_TO_GENOTYPE.items():
            for locus, alleles in mapping.items():
                key = (locus, tuple(sorted(alleles)))
                self.reverse.setdefault(key, []).append(trait)

        debug(f"Reverse lookup table generated with {len(self.reverse)} entries")

    # ------------------------------------------------------------------
    # Complete missing loci using safe defaults
    # ------------------------------------------------------------------
    def complete_genotype(self, defaults: dict):
        debug("\n--- Completing genotype from defaults ---")
        final = {}

        # Add defined genes first
        for locus, alleles in defaults.items():
            final[locus] = tuple(alleles)

        # Add missing loci using dataset fallback
        for _, mapping in TRAIT_TO_GENOTYPE.items():
            for locus, alleles in mapping.items():
                if locus not in final:
                    # Use first allele tuple as dominant safe default
                    final[locus] = tuple(alleles)

        debug("→ Completed genotype:", final)
        return final

    # ------------------------------------------------------------------
    # Combine breed defaults + manual overrides
    # ------------------------------------------------------------------
    def combine_defaults_with_overrides(self, defaults, overrides):
        debug("\n--- Combining defaults + overrides ---")
        merged = {}

        if defaults:
            merged.update({k: tuple(v) for k, v in defaults.items()})
        if overrides:
            merged.update({k: tuple(v) for k, v in overrides.items()})

        debug("→ Final merged genotype:", merged)
        return merged

    # ------------------------------------------------------------------
    # Convert genotype to readable phenotype per locus
    # ------------------------------------------------------------------
    def genotype_to_readable(self, genotype):
        debug("\n--- Converting genotype to readable phenotype ---")
        result = {}

        for locus, alleles in genotype.items():
            key = (locus, tuple(sorted(alleles)))
            traits = self.reverse.get(key)

            if traits:
                result[locus] = traits[0]  # Pick first matching trait
            else:
                # Unknown locus → show alleles as fallback
                result[locus] = f"{alleles[0]}/{alleles[1]}"

            debug(f"  {locus}: {alleles} → {result[locus]}")

        return result

    # Full phenotype string for display
    def phenotype_string(self, genotype):
        phenomap = self.genotype_to_readable(genotype)
        traits = [t for t in phenomap.values() if t]
        return ", ".join(traits)

    # ------------------------------------------------------------------
    # Punnett square
    # ------------------------------------------------------------------
    def punnett_square(self, parent1, parent2):
        debug("\n=== Punnett Square Generation ===")
        punnett = {}

        for locus in parent1.keys():
            if locus not in parent2:
                continue

            combos = list(itertools.product(parent1[locus], parent2[locus]))
            count = Counter(combos)
            punnett[locus] = []

            for pair, qty in count.items():
                child_geno = tuple(sorted(pair))
                trait = self.reverse.get((locus, child_geno), ["Unknown"])[0]
                prob = (qty / len(combos)) * 100

                punnett[locus].append({
                    "genotype": f"{child_geno[0]}{child_geno[1]}",
                    "probability": f"{prob:.0f}%",
                    "trait": trait
                })

        return punnett

    # ------------------------------------------------------------------
    # Monte-Carlo simulation (per-locus phenotype for vertical card display)
    # ------------------------------------------------------------------
    def monte_carlo(self, parent1, parent2, samples=6):
        debug("\n=== Monte-Carlo Simulation ===")
        children = []
        loci = [l for l in parent1.keys() if l in parent2]

        for _ in range(samples):
            geno = {l: tuple(sorted((random.choice(parent1[l]), random.choice(parent2[l])))) for l in loci}
            phenomap = self.genotype_to_readable(geno)
            phenotype = ", ".join(phenomap.values())

            children.append({
                "genotype": geno,
                "phenotype": phenotype,
                "phenomap": phenomap  # for vertical card display
            })

        return children

    # ------------------------------------------------------------------
    # Bayesian probability of phenotype match using Punnett
    # ------------------------------------------------------------------
    def bayesian_probability(self, phenotype, punnett):
        posterior = {}
        total = 0

        # Convert phenotype string to set
        phenotype_set = set(phenotype.split(", "))

        for locus, options in punnett.items():
            for item in options:
                if item["trait"] in phenotype_set:
                    prob = int(item["probability"].replace("%", ""))
                    posterior[item["trait"]] = posterior.get(item["trait"], 0) + prob
                    total += prob

        if total == 0:
            return {}

        return {trait: f"{(v / total) * 100:.0f}%" for trait, v in posterior.items()}

    # ------------------------------------------------------------------
    # Similarity score between 2 phenotype strings
    # ------------------------------------------------------------------
    def similarity(self, phenotype_a, phenotype_b):
        A = set(phenotype_a.split(", "))
        B = set(phenotype_b.split(", "))
        return len(A & B) / len(A | B) if (A | B) else 0

    # ------------------------------------------------------------------
    # Full summary for GeneticSummary screen
    # ------------------------------------------------------------------
    def generate_summary(self, father_genes, mother_genes, samples=6):
        punnett = self.punnett_square(father_genes, mother_genes)
        monte = self.monte_carlo(father_genes, mother_genes, samples)

        father_str = self.phenotype_string(father_genes)
        mother_str = self.phenotype_string(mother_genes)

        for child in monte:
            child["similarity"] = {
                "father": self.similarity(child["phenotype"], father_str),
                "mother": self.similarity(child["phenotype"], mother_str),
                "bayesian": self.bayesian_probability(child["phenotype"], punnett)
            }

        return punnett, monte, [c["phenotype"] for c in monte]
