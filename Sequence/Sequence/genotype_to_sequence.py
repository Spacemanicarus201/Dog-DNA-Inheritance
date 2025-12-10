#!/usr/bin/env python3
"""genotype_to_sequence.py

Integrates trait selection with DNA sequence mutation.
Converts genotype from trait_selection.py to mutated DNA sequences.
"""

import json
import os
import sys
from typing import Dict, Tuple, List


# Map locus names to allele codes in Reference.json
LOCUS_TO_ALLELE_MAP = {
    "E": {
        ("Em", "Em"): ["Em", "Em"],
        ("Em", "E"): ["Em", "E"],
        ("Em", "e"): ["Em", "e"],
        ("E", "E"): ["E", "E"],
        ("E", "e"): ["E", "e"],
        ("e", "e"): ["e", "e"],
    },
    "K": {
        ("Kb", "Kb"): ["Kb", "Kb"],
        ("Kb", "ky"): ["Kb", "ky"],
        ("Kb", "kbr"): ["Kb", "kbr"],
        ("kbr", "kbr"): ["kbr", "kbr"],
        ("kbr", "ky"): ["kbr", "ky"],
        ("ky", "ky"): ["ky", "ky"],
    },
    "A": {
        ("Ay", "Ay"): ["Ay", "Ay"],
        ("Ay", "aw"): ["Ay", "aw"],
        ("Ay", "at"): ["Ay", "at"],
        ("Ay", "a"): ["Ay", "a"],
        ("aw", "aw"): ["aw", "aw"],
        ("aw", "at"): ["aw", "at"],
        ("at", "at"): ["at", "at"],
        ("a", "a"): ["a", "a"],
    },
    "B": {
        ("B", "B"): ["B", "B"],
        ("B", "b"): ["B", "b"],
        ("b", "b"): ["b", "b"],
    },
    "D": {
        ("D", "D"): ["D", "D"],
        ("D", "d"): ["D", "d"],
        ("d", "d"): ["d", "d"],
    },
    "M": {
        ("M", "M"): ["M", "M"],
        ("M", "m"): ["M", "m"],
        ("m", "m"): ["m", "m"],
    },
    "S": {
        ("S", "S"): ["S", "S"],
        ("S", "sp"): ["S", "sp"],
        ("si", "si"): ["si", "si"],
        ("sp", "sp"): ["sp", "sp"],
        ("sw", "sw"): ["sw", "sw"],
    },
    "L": {
        ("L", "L"): ["L", "L"],
        ("L", "l"): ["L", "l"],
        ("l", "l"): ["l", "l"],
    },
}


class GenotypeToSequence:
    """Converts genotype to mutated DNA sequences."""
    
    def __init__(self, reference_json_path: str, sequence_dir: str):
        """
        Initialize converter.
        
        Args:
            reference_json_path: Path to Reference.json
            sequence_dir: Directory containing template FASTA files
        """
        self.sequence_dir = sequence_dir
        
        # Load reference
        with open(reference_json_path, 'r') as f:
            self.reference = json.load(f)
        
        # Cache for sequences
        self._sequence_cache: Dict[str, str] = {}
    
    def load_sequence(self, gene_file: str) -> str:
        """Load DNA sequence from FASTA file."""
        if gene_file in self._sequence_cache:
            return self._sequence_cache[gene_file]
        
        filepath = os.path.join(self.sequence_dir, gene_file)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Template file not found: {filepath}")
        
        sequence_lines = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('>'):
                    sequence_lines.append(line)
        
        sequence = ''.join(sequence_lines)
        self._sequence_cache[gene_file] = sequence
        return sequence
    
    def genotype_to_alleles(self, genotype: Dict[str, Tuple[str, str]]) -> List[str]:
        """
        Convert genotype dict to list of unique alleles.
        
        Args:
            genotype: e.g., {"E": ("E", "e"), "K": ("Kb", "ky"), ...}
        
        Returns:
            List of unique allele codes, e.g., ["E", "e", "Kb", "ky", ...]
        """
        alleles = set()
        for locus, (allele1, allele2) in genotype.items():
            alleles.add(allele1)
            alleles.add(allele2)
        return list(alleles)
    
    def get_gene_for_allele(self, allele: str) -> str:
        """Get the gene name for an allele."""
        if allele in self.reference:
            return self.reference[allele].get("gene", "")
        return ""
    
    def apply_mutation_to_sequence(self, sequence: str, allele_data: dict) -> Tuple[str, dict]:
        """
        Apply a single mutation to a sequence.
        
        Returns:
            Tuple of (mutated_sequence, mutation_info)
        """
        mutation_type = allele_data.get("type")
        
        if mutation_type == "REF":
            return sequence, {"type": "REF", "applied": False}
        
        context = allele_data.get("context", "")
        
        # Find context position (case-insensitive)
        context_pos = sequence.upper().find(context.upper())
        if context_pos == -1:
            return sequence, {
                "type": mutation_type,
                "applied": False,
                "error": f"Context '{context}' not found"
            }
        
        if mutation_type == "SNP":
            ref = allele_data.get("ref")
            mut = allele_data.get("mut")
            middle_offset = len(context) // 2
            mutation_pos = context_pos + middle_offset
            
            # Apply SNP
            mutated = sequence[:mutation_pos] + mut + sequence[mutation_pos + 1:]
            return mutated, {
                "type": "SNP",
                "applied": True,
                "position": mutation_pos,
                "ref": ref,
                "mut": mut
            }
        
        elif mutation_type == "DEL":
            delete_seq = allele_data.get("delete_seq", "")
            # Find delete_seq near context
            search_start = context_pos
            search_end = context_pos + len(context) + len(delete_seq) + 10
            search_region = sequence[search_start:search_end]
            
            del_pos_in_region = search_region.upper().find(delete_seq.upper())
            if del_pos_in_region == -1:
                return sequence, {
                    "type": "DEL",
                    "applied": False,
                    "error": f"Delete sequence '{delete_seq}' not found"
                }
            
            deletion_pos = search_start + del_pos_in_region
            mutated = sequence[:deletion_pos] + sequence[deletion_pos + len(delete_seq):]
            return mutated, {
                "type": "DEL",
                "applied": True,
                "position": deletion_pos,
                "deleted": delete_seq
            }
        
        elif mutation_type == "INS":
            insert_seq = allele_data.get("insert_seq", "")
            insertion_pos = context_pos + len(context)
            mutated = sequence[:insertion_pos] + insert_seq + sequence[insertion_pos:]
            return mutated, {
                "type": "INS",
                "applied": True,
                "position": insertion_pos,
                "inserted": insert_seq
            }
        
        return sequence, {"type": mutation_type, "applied": False, "error": "Unknown type"}
    
    def process_genotype(self, genotype: Dict[str, Tuple[str, str]]) -> Dict[str, dict]:
        """
        Process a complete genotype and return mutated sequences for each gene.
        
        Args:
            genotype: Dictionary mapping locus to (allele1, allele2)
        
        Returns:
            Dictionary mapping gene name to mutation results:
            {
                "MC1R": {
                    "alleles": ["E", "e"],
                    "template_file": "MC1R_template.fasta",
                    "template_sequence": "ATCG...",
                    "mutated_sequence": "ATCG...",
                    "mutations_applied": [...]
                }
            }
        """
        results = {}
        
        # Get all unique alleles
        alleles = self.genotype_to_alleles(genotype)
        
        # Group alleles by gene
        gene_alleles = {}
        for allele in alleles:
            if allele in self.reference:
                gene = self.get_gene_for_allele(allele)
                if gene:
                    if gene not in gene_alleles:
                        gene_alleles[gene] = []
                    gene_alleles[gene].append(allele)
        
        # Process each gene
        for gene, gene_allele_list in gene_alleles.items():
            # Find template file
            template_file = None
            for allele in gene_allele_list:
                if "file" in self.reference[allele]:
                    template_file = self.reference[allele]["file"]
                    break
            
            if not template_file:
                continue
            
            # Load template sequence
            try:
                template_seq = self.load_sequence(template_file)
            except FileNotFoundError:
                continue
            
            current_seq = template_seq
            mutations_applied = []
            
            # Apply mutations for each allele
            for allele in gene_allele_list:
                allele_data = self.reference[allele]
                
                if allele_data.get("type") != "REF":
                    mutated_seq, mut_info = self.apply_mutation_to_sequence(current_seq, allele_data)
                    
                    if mut_info.get("applied"):
                        current_seq = mutated_seq
                        mutations_applied.append({
                            "allele": allele,
                            "description": allele_data.get("description", ""),
                            **mut_info
                        })
            
            results[gene] = {
                "alleles": gene_allele_list,
                "template_file": template_file,
                "template_sequence": template_seq,
                "mutated_sequence": current_seq,
                "mutations_applied": mutations_applied,
                "template_length": len(template_seq),
                "mutated_length": len(current_seq)
            }
        
        return results


def main():
    """Example usage."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reference_path = os.path.join(script_dir, "Reference.json")
    sequence_dir = os.path.join(script_dir, "extracted_genes")
    
    # Create converter
    converter = GenotypeToSequence(reference_path, sequence_dir)
    
    # Example genotype (Golden Retriever)
    example_genotype = {
        "E": ("e", "e"),      # Recessive red
        "K": ("ky", "ky"),    # Allows A locus
        "A": ("Ay", "Ay"),    # Sable
        "B": ("B", "B"),      # Black pigment
        "D": ("D", "D"),      # Full color
        "L": ("l", "l"),      # Long coat
    }
    
    print("=" * 70)
    print("Genotype to Sequence Converter - Example")
    print("=" * 70)
    print(f"\nInput Genotype:")
    for locus, (a1, a2) in example_genotype.items():
        print(f"  {locus}: {a1}/{a2}")
    
    results = converter.process_genotype(example_genotype)
    
    print(f"\n\nResults for {len(results)} genes:")
    print("=" * 70)
    
    for gene, info in results.items():
        print(f"\n{gene}:")
        print(f"  Alleles: {', '.join(info['alleles'])}")
        print(f"  Template: {info['template_file']}")
        print(f"  Sequence length: {info['template_length']} bp → {info['mutated_length']} bp")
        print(f"  Mutations applied: {len(info['mutations_applied'])}")
        
        for mut in info['mutations_applied']:
            print(f"    • {mut['allele']}: {mut['description']}")
            if mut['type'] == 'SNP':
                print(f"      SNP at position {mut['position']}: {mut['ref']} → {mut['mut']}")
            elif mut['type'] == 'DEL':
                print(f"      Deletion at position {mut['position']}: {mut['deleted']}")
            elif mut['type'] == 'INS':
                print(f"      Insertion at position {mut['position']}: {mut['inserted']}")


if __name__ == "__main__":
    main()
