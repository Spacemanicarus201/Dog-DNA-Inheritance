from genome_library import TRAIT_TO_GENOTYPE

class GeneticCalculator:
    def __init__(self):
        # Gather every locus once from the database
        self.all_loci = {}
        for trait, mapping in TRAIT_TO_GENOTYPE.items():
            for locus in mapping.keys():
                self.all_loci[locus] = True
