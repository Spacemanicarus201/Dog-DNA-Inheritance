#!/usr/bin/env python3
"""find_mutation_contexts.py

Helper script to find the actual mutation contexts in extracted gene sequences.
"""

import os
from Bio import SeqIO


def load_fasta_sequence(filepath):
    """Load sequence from FASTA file."""
    record = SeqIO.read(filepath, "fasta")
    return str(record.seq)


def find_context_around_position(sequence, position, window=5):
    """Extract context sequence around a position."""
    start = max(0, position - window)
    end = min(len(sequence), position + window + 1)
    return sequence[start:end]


def search_for_pattern(sequence, pattern, max_mismatches=2):
    """Search for a pattern allowing some mismatches."""
    pattern_len = len(pattern)
    best_match = None
    best_score = float('inf')
    
    for i in range(len(sequence) - pattern_len + 1):
        substr = sequence[i:i+pattern_len]
        mismatches = sum(1 for a, b in zip(pattern, substr) if a != b)
        if mismatches < best_score:
            best_score = mismatches
            best_match = (i, substr, mismatches)
    
    return best_match


# Known mutations from literature
mutations = {
    "MC1R": {
        "gene": "MC1R",
        "file": "MC1R_template.fasta",
        "mutations": [
            {"name": "e (Recessive Red)", "expected_context": "GTGTGCAGCTA", "ref": "C", "mut": "T"},
            {"name": "E (Wild Type)", "expected_context": "GTGTGCAGCTA", "ref": "C", "mut": "A"},
        ]
    },
    "TYRP1": {
        "gene": "TYRP1",
        "file": "TYRP1_template.fasta",
        "mutations": [
            {"name": "b (Brown)", "expected_context": "CCTCCCAGTTA", "ref": "C", "mut": "T"},
        ]
    },
    "FGF5": {
        "gene": "FGF5",
        "file": "FGF5_template.fasta",
        "mutations": [
            {"name": "l (Long Hair)", "expected_context": "TTGGTGGAAAA", "ref": "G", "mut": "T"},
        ]
    },
    "ASIP": {
        "gene": "ASIP",
        "file": "ASIP_template.fasta",
        "mutations": [
            {"name": "a (Recessive Black)", "expected_context": "GGGGGCAGAAG", "ref": "C", "mut": "T"},
            {"name": "at (Tan Points)", "expected_context": "GGGGGCAGAAG", "ref": "C", "mut": "A"},
            {"name": "aw (Wolf Sable)", "expected_context": "GGGGGCAGAAG", "ref": "C", "mut": "G"},
        ]
    }
}


def main():
    sequence_dir = "extracted_genes"
    
    print("=" * 70)
    print("Searching for Mutation Contexts in Extracted Genes")
    print("=" * 70)
    print()
    
    for gene_name, gene_info in mutations.items():
        filepath = os.path.join(sequence_dir, gene_info["file"])
        
        if not os.path.exists(filepath):
            print(f"❌ {gene_name}: File not found - {filepath}")
            continue
        
        sequence = load_fasta_sequence(filepath)
        print(f"\n{gene_name} ({len(sequence)} bp)")
        print("-" * 70)
        
        for mut in gene_info["mutations"]:
            expected = mut["expected_context"]
            
            # Try exact match first
            pos = sequence.find(expected)
            if pos != -1:
                print(f"✓ {mut['name']}")
                print(f"  Context: {expected}")
                print(f"  Position: {pos}")
                print(f"  Mutation: {mut['ref']} → {mut['mut']} at position {pos + len(expected)//2}")
            else:
                # Try case-insensitive
                pos = sequence.upper().find(expected.upper())
                if pos != -1:
                    actual_context = sequence[pos:pos+len(expected)]
                    print(f"⚠ {mut['name']} (case mismatch)")
                    print(f"  Expected: {expected}")
                    print(f"  Found:    {actual_context}")
                    print(f"  Position: {pos}")
                else:
                    # Try fuzzy match
                    match = search_for_pattern(sequence.upper(), expected.upper())
                    if match and match[2] <= 2:
                        pos, found_seq, mismatches = match
                        actual_context = sequence[pos:pos+len(expected)]
                        print(f"⚠ {mut['name']} (fuzzy match, {mismatches} mismatches)")
                        print(f"  Expected: {expected}")
                        print(f"  Found:    {actual_context}")
                        print(f"  Position: {pos}")
                    else:
                        print(f"❌ {mut['name']} - Context NOT FOUND")
                        print(f"  Expected: {expected}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
