#!/usr/bin/env python3
"""mutation_applier.py

Applies genetic mutations to template FASTA sequences based on Reference.json.
Supports SNP, INS, DEL, and REF mutation types.
"""

import json
import os
from typing import Dict, Tuple, Optional


class MutationApplier:
    """Applies mutations to dog gene sequences based on allele selections."""
    
    def __init__(self, reference_json_path: str, sequence_dir: str):
        """
        Initialize the mutation applier.
        
        Args:
            reference_json_path: Path to Reference.json
            sequence_dir: Directory containing template FASTA files
        """
        self.sequence_dir = sequence_dir
        
        # Load reference mutations
        with open(reference_json_path, 'r') as f:
            self.reference = json.load(f)
        
        # Cache for loaded sequences
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
    
    def find_context_position(self, sequence: str, context: str) -> int:
        """
        Find the position of context sequence in the DNA.
        
        Returns:
            Index of the context start, or -1 if not found
        """
        return sequence.find(context)
    
    def apply_snp(self, sequence: str, context: str, ref: str, mut: str) -> Tuple[str, int]:
        """
        Apply a Single Nucleotide Polymorphism (SNP).
        
        Args:
            sequence: Original DNA sequence
            context: Context sequence to find
            ref: Reference base to replace
            mut: Mutation base to insert
            
        Returns:
            Tuple of (mutated_sequence, mutation_position)
        """
        context_pos = self.find_context_position(sequence, context)
        if context_pos == -1:
            raise ValueError(f"Context '{context}' not found in sequence")
        
        # Find the ref base within the context (usually in the middle)
        middle_offset = len(context) // 2
        mutation_pos = context_pos + middle_offset
        
        # Verify the reference base matches
        if sequence[mutation_pos] != ref:
            raise ValueError(
                f"Reference mismatch at position {mutation_pos}: "
                f"expected '{ref}', found '{sequence[mutation_pos]}'"
            )
        
        # Apply the mutation
        mutated = sequence[:mutation_pos] + mut + sequence[mutation_pos + 1:]
        return mutated, mutation_pos
    
    def apply_deletion(self, sequence: str, context: str, delete_seq: str) -> Tuple[str, int]:
        """
        Apply a deletion mutation.
        
        Args:
            sequence: Original DNA sequence
            context: Context sequence to find
            delete_seq: Sequence to delete
            
        Returns:
            Tuple of (mutated_sequence, deletion_position)
        """
        context_pos = self.find_context_position(sequence, context)
        if context_pos == -1:
            raise ValueError(f"Context '{context}' not found in sequence")
        
        # Look for delete_seq near the context
        search_start = context_pos
        search_end = context_pos + len(context) + len(delete_seq)
        search_region = sequence[search_start:search_end]
        
        del_pos_in_region = search_region.find(delete_seq)
        if del_pos_in_region == -1:
            raise ValueError(f"Deletion sequence '{delete_seq}' not found near context")
        
        deletion_pos = search_start + del_pos_in_region
        
        # Apply the deletion
        mutated = sequence[:deletion_pos] + sequence[deletion_pos + len(delete_seq):]
        return mutated, deletion_pos
    
    def apply_insertion(self, sequence: str, context: str, insert_seq: str) -> Tuple[str, int]:
        """
        Apply an insertion mutation.
        
        Args:
            sequence: Original DNA sequence
            context: Context sequence to find
            insert_seq: Sequence to insert after context
            
        Returns:
            Tuple of (mutated_sequence, insertion_position)
        """
        context_pos = self.find_context_position(sequence, context)
        if context_pos == -1:
            raise ValueError(f"Context '{context}' not found in sequence")
        
        # Insert after the context
        insertion_pos = context_pos + len(context)
        mutated = sequence[:insertion_pos] + insert_seq + sequence[insertion_pos:]
        return mutated, insertion_pos
    
    def apply_allele_mutation(self, allele: str) -> Optional[Tuple[str, str, int]]:
        """
        Apply mutation for a given allele.
        
        Args:
            allele: Allele code (e.g., "e", "Kb", "a", "b", "l")
            
        Returns:
            Tuple of (gene_name, mutated_sequence, mutation_position) or None if REF
        """
        if allele not in self.reference:
            raise ValueError(f"Allele '{allele}' not found in reference")
        
        allele_data = self.reference[allele]
        mutation_type = allele_data.get("type")
        gene = allele_data.get("gene")
        
        # REF means no mutation needed
        if mutation_type == "REF":
            return None
        
        # Load the template sequence
        gene_file = allele_data.get("file")
        if not gene_file:
            raise ValueError(f"No file specified for allele '{allele}'")
        
        sequence = self.load_sequence(gene_file)
        context = allele_data.get("context", "")
        
        # Apply the appropriate mutation type
        if mutation_type == "SNP":
            ref = allele_data.get("ref")
            mut = allele_data.get("mut")
            mutated_seq, pos = self.apply_snp(sequence, context, ref, mut)
            
        elif mutation_type == "DEL":
            delete_seq = allele_data.get("delete_seq")
            mutated_seq, pos = self.apply_deletion(sequence, context, delete_seq)
            
        elif mutation_type == "INS":
            insert_seq = allele_data.get("insert_seq")
            mutated_seq, pos = self.apply_insertion(sequence, context, insert_seq)
            
        else:
            raise ValueError(f"Unknown mutation type: {mutation_type}")
        
        return gene, mutated_seq, pos
    
    def apply_genotype(self, genotype: Dict[str, Tuple[str, str]]) -> Dict[str, Dict[str, any]]:
        """
        Apply mutations for a complete genotype.
        
        Args:
            genotype: Dictionary mapping locus to (allele1, allele2)
                     e.g., {"E": ("E", "e"), "K": ("Kb", "ky"), ...}
        
        Returns:
            Dictionary mapping gene to mutation info:
            {
                "MC1R": {
                    "alleles": ["E", "e"],
                    "mutations": [
                        {"allele": "e", "position": 123, "type": "SNP", "description": "..."}
                    ],
                    "sequence": "ATCG...",  # Final mutated sequence
                    "template": "ATCG..."   # Original template
                }
            }
        """
        results = {}
        
        # Collect all unique alleles
        all_alleles = set()
        for allele1, allele2 in genotype.values():
            all_alleles.add(allele1)
            all_alleles.add(allele2)
        
        # Group alleles by gene
        gene_alleles = {}
        for allele in all_alleles:
            if allele in self.reference:
                gene = self.reference[allele].get("gene")
                if gene:
                    if gene not in gene_alleles:
                        gene_alleles[gene] = []
                    gene_alleles[gene].append(allele)
        
        # Apply mutations for each gene
        for gene, alleles in gene_alleles.items():
            # Find the template file from any allele
            template_file = None
            for allele in alleles:
                if "file" in self.reference[allele]:
                    template_file = self.reference[allele]["file"]
                    break
            
            if not template_file:
                continue
            
            # Load original template
            template_seq = self.load_sequence(template_file)
            current_seq = template_seq
            mutations_applied = []
            
            # Apply each mutation
            for allele in alleles:
                allele_data = self.reference[allele]
                if allele_data.get("type") == "REF":
                    continue
                
                try:
                    result = self.apply_allele_mutation(allele)
                    if result:
                        _, mutated_seq, pos = result
                        current_seq = mutated_seq
                        
                        mutations_applied.append({
                            "allele": allele,
                            "position": pos,
                            "type": allele_data.get("type"),
                            "description": allele_data.get("description")
                        })
                except Exception as e:
                    print(f"Warning: Could not apply mutation for {allele}: {e}")
            
            results[gene] = {
                "alleles": alleles,
                "mutations": mutations_applied,
                "sequence": current_seq,
                "template": template_seq
            }
        
        return results


def main():
    """Example usage and testing."""
    import sys
    
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reference_path = os.path.join(script_dir, "Reference.json")
    sequence_dir = os.path.join(script_dir, "extracted_genes")
    
    # Create applier
    applier = MutationApplier(reference_path, sequence_dir)
    
    # Example: Apply mutations for a Golden Retriever genotype
    example_genotype = {
        "E": ("e", "e"),      # Recessive red
        "K": ("ky", "ky"),    # Allows A locus
        "A": ("Ay", "Ay"),    # Sable
        "B": ("B", "B"),      # Black pigment
        "D": ("D", "D"),      # Full color
        "L": ("l", "l"),      # Long coat
    }
    
    print("=" * 60)
    print("Dog DNA Mutation Applier - Example")
    print("=" * 60)
    print(f"Genotype: {example_genotype}")
    print()
    
    results = applier.apply_genotype(example_genotype)
    
    for gene, info in results.items():
        print(f"\n{gene} Gene:")
        print(f"  Alleles: {', '.join(info['alleles'])}")
        print(f"  Mutations applied: {len(info['mutations'])}")
        for mut in info['mutations']:
            print(f"    - {mut['allele']}: {mut['description']} at position {mut['position']}")
        print(f"  Template length: {len(info['template'])} bp")
        print(f"  Final sequence length: {len(info['sequence'])} bp")


if __name__ == "__main__":
    main()
