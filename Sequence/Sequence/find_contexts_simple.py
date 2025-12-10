#!/usr/bin/env python3
"""find_mutation_contexts_simple.py

Simple script to find mutation contexts without Biopython.
"""

import os


def load_fasta_sequence(filepath):
    """Load sequence from FASTA file."""
    sequence_lines = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('>'):
                sequence_lines.append(line)
    return ''.join(sequence_lines)


# Known mutations from literature
mutations = {
    "MC1R": {
        "file": "MC1R_template.fasta",
        "contexts": ["GTGTGCAGCTA"]
    },
    "TYRP1": {
        "file": "TYRP1_template.fasta",
        "contexts": ["CCTCCCAGTTA"]
    },
    "FGF5": {
        "file": "FGF5_template.fasta",
        "contexts": ["TTGGTGGAAAA"]
    },
    "ASIP": {
        "file": "ASIP_template.fasta",
        "contexts": ["GGGGGCAGAAG"]
    }
}


def main():
    sequence_dir = "extracted_genes"
    
    print("Searching for Mutation Contexts")
    print("=" * 60)
    
    for gene_name, gene_info in mutations.items():
        filepath = os.path.join(sequence_dir, gene_info["file"])
        
        if not os.path.exists(filepath):
            print(f"{gene_name}: File not found")
            continue
        
        sequence = load_fasta_sequence(filepath)
        print(f"\n{gene_name} ({len(sequence)} bp)")
        
        for context in gene_info["contexts"]:
            # Try exact match
            pos = sequence.find(context)
            if pos != -1:
                print(f"  FOUND: {context} at position {pos}")
            else:
                # Try uppercase
                pos = sequence.upper().find(context.upper())
                if pos != -1:
                    actual = sequence[pos:pos+len(context)]
                    print(f"  FOUND (case): {actual} at position {pos}")
                else:
                    print(f"  NOT FOUND: {context}")
                    # Show first 100 bp to help debug
                    print(f"  First 100bp: {sequence[:100]}")


if __name__ == "__main__":
    main()
