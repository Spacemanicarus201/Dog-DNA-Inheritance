import itertools
import random
from collections import Counter

from genome_library import TRAIT_TO_GENOTYPE, BREED_DEFAULTS

class GeneticCalculator:
    def __init__(self):
        # reverse lookup: (locus, alleles_sorted) -> [trait_names...]
        self.reverse = {}
        for trait, mapping in TRAIT_TO_GENOTYPE.items():
            for locus, alleles in mapping.items():
                key = (locus, tuple(sorted(alleles)))
                self.reverse.setdefault(key, []).append(trait)

    def combine_defaults_with_overrides(self, defaults, overrides):
        merged = {}
        if defaults:
            merged.update({k: tuple(v) for k,v in defaults.items()})
        if overrides:
            merged.update({k: tuple(v) for k,v in overrides.items()})
        return merged

    def genotype_to_readable(self, genotype):
        out = {}
        for locus, alleles in genotype.items():
            key = (locus, tuple(sorted(alleles)))
            out[locus] = self.reverse.get(key, [None])[0]
        return out

    def punnett_square(self, parent1, parent2):
        results = {}
        for locus in parent1.keys():
            if locus not in parent2:
                continue
            a = parent1[locus]
            b = parent2[locus]
            combos = list(itertools.product(a, b))  # keep all combinations
            counts = Counter(combos)
            total = sum(counts.values())
            locus_res = {}
            for geno, cnt in counts.items():
                prob = cnt / total
                key = (locus, tuple(sorted(geno)))  # sort only for trait lookup
                trait = self.reverse.get(key, [None])[0]
                locus_res["/".join(geno)] = {"probability": f"{prob*100:.0f}%", "trait": trait or "Unknown"}
            results[locus] = locus_res
        return results

    def monte_carlo(self, parent1, parent2, samples=6):
        children = []
        loci = [l for l in parent1.keys() if l in parent2]
        for _ in range(samples):
            child = {}
            for locus in loci:
                a = random.choice(parent1[locus])
                b = random.choice(parent2[locus])
                child[locus] = tuple(sorted((a,b)))
            children.append(child)
        return children

    def genotype_child_to_readable_phenotype(self, child_genotype):
        order = ["E", "K", "A", "B", "D", "M", "H"]
        parts = []
        for locus in order:
            if locus in child_genotype:
                key = (locus, tuple(sorted(child_genotype[locus])))
                trait = self.reverse.get(key, [None])[0]
                if trait:
                    parts.append(trait)
        if parts:
            return ", ".join(parts)
        return ", ".join([f"{l}:{'/'.join(child_genotype[l])}" for l in child_genotype])

    def generate_summary(self, father_genes, mother_genes, samples=6):
        punnett = self.punnett_square(father_genes, mother_genes)
        monte_genos = self.monte_carlo(father_genes, mother_genes, samples=samples)
        monte_readables = [self.genotype_child_to_readable_phenotype(g) for g in monte_genos]
        return punnett, monte_genos, monte_readables
