"""dna_exporter.py

Export puppy DNA sequences to FASTA files.
"""

import os
from datetime import datetime
from typing import Dict, Tuple


class DNAExporter:
    """Exports dog genotypes to FASTA files with mutated DNA sequences."""
    
    def __init__(self, genotype_to_sequence_converter):
        """
        Initialize exporter with a GenotypeToSequence converter.
        
        Args:
            genotype_to_sequence_converter: Instance of GenotypeToSequence
        """
        self.converter = genotype_to_sequence_converter
    
    def export_puppy_dna(self, 
                        puppy_genotype: Dict[str, Tuple[str, str]], 
                        puppy_number: int,
                        output_dir: str = "exported_dna",
                        puppy_name: str = None) -> Dict[str, str]:
        """
        Export a puppy's DNA sequences to FASTA files.
        
        Args:
            puppy_genotype: Dictionary mapping locus to (allele1, allele2)
            puppy_number: Puppy number (1, 2, 3, etc.)
            output_dir: Directory to save files
            puppy_name: Optional custom name for the puppy
            
        Returns:
            Dictionary mapping gene to output filename
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate DNA sequences
        dna_results = self.converter.process_genotype(puppy_genotype)
        
        # Prepare puppy identifier
        if puppy_name:
            puppy_id = puppy_name.replace(" ", "_")
        else:
            puppy_id = f"Puppy_{puppy_number}"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exported_files = {}
        
        # Export each gene
        for gene, data in dna_results.items():
            # Create filename
            filename = f"{puppy_id}_{gene}_{timestamp}.fasta"
            filepath = os.path.join(output_dir, filename)
            
            # Get alleles for this gene
            alleles = data.get('alleles', [])
            mutations = data.get('mutations_applied', [])
            
            # Write FASTA file
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header with metadata
                f.write(f">{puppy_id}_{gene} ")
                f.write(f"alleles={','.join(alleles)} ")
                f.write(f"length={len(data['mutated_sequence'])}bp ")
                f.write(f"mutations={len(mutations)}\n")
                
                # Add mutation details as comments
                if mutations:
                    f.write(f"# Mutations applied:\n")
                    for mut in mutations:
                        f.write(f"#   {mut['allele']}: {mut['description']} ")
                        f.write(f"({mut['type']} at position {mut['position']})\n")
                
                # Write sequence (60 characters per line)
                sequence = data['mutated_sequence']
                for i in range(0, len(sequence), 60):
                    f.write(sequence[i:i+60] + "\n")
            
            exported_files[gene] = filepath
        
        return exported_files
    
    def export_complete_genome(self,
                              puppy_genotype: Dict[str, Tuple[str, str]],
                              puppy_number: int,
                              output_dir: str = "exported_dna",
                              puppy_name: str = None) -> str:
        """
        Export all genes into a single multi-FASTA file.
        
        Args:
            puppy_genotype: Dictionary mapping locus to (allele1, allele2)
            puppy_number: Puppy number
            output_dir: Directory to save file
            puppy_name: Optional custom name
            
        Returns:
            Path to the exported file
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate DNA sequences
        dna_results = self.converter.process_genotype(puppy_genotype)
        
        # Prepare puppy identifier
        if puppy_name:
            puppy_id = puppy_name.replace(" ", "_")
        else:
            puppy_id = f"Puppy_{puppy_number}"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{puppy_id}_complete_genome_{timestamp}.fasta"
        filepath = os.path.join(output_dir, filename)
        
        # Write multi-FASTA file
        with open(filepath, 'w', encoding='utf-8') as f:
            # File header
            f.write(f"# Complete genome for {puppy_id}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Genotype: {puppy_genotype}\n")
            f.write(f"#\n")
            
            # Write each gene
            for gene, data in dna_results.items():
                alleles = data.get('alleles', [])
                mutations = data.get('mutations_applied', [])
                
                # Gene header
                f.write(f"\n>{puppy_id}_{gene} ")
                f.write(f"alleles={','.join(alleles)} ")
                f.write(f"length={len(data['mutated_sequence'])}bp ")
                f.write(f"mutations={len(mutations)}\n")
                
                # Mutation details
                if mutations:
                    for mut in mutations:
                        f.write(f"# {mut['allele']}: {mut['description']} ")
                        f.write(f"({mut['type']} at pos {mut['position']})\n")
                
                # Sequence
                sequence = data['mutated_sequence']
                for i in range(0, len(sequence), 60):
                    f.write(sequence[i:i+60] + "\n")
        
        return filepath
    
    def create_summary_report(self,
                             puppy_genotype: Dict[str, Tuple[str, str]],
                             puppy_number: int,
                             phenotype_description: str,
                             output_dir: str = "exported_dna",
                             puppy_name: str = None) -> str:
        """
        Create a human-readable summary report with genotype and phenotype.
        
        Args:
            puppy_genotype: Dictionary mapping locus to (allele1, allele2)
            puppy_number: Puppy number
            phenotype_description: Human-readable phenotype description
            output_dir: Directory to save file
            puppy_name: Optional custom name
            
        Returns:
            Path to the report file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if puppy_name:
            puppy_id = puppy_name.replace(" ", "_")
        else:
            puppy_id = f"Puppy_{puppy_number}"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{puppy_id}_genetic_report_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # Generate DNA data
        dna_results = self.converter.process_genotype(puppy_genotype)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write(f"GENETIC REPORT: {puppy_name or f'Puppy #{puppy_number}'}\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            
            # Phenotype
            f.write("PREDICTED APPEARANCE\n")
            f.write("-" * 70 + "\n")
            f.write(f"{phenotype_description}\n")
            f.write("\n")
            
            # Genotype
            f.write("GENOTYPE (Allele Pairs)\n")
            f.write("-" * 70 + "\n")
            for locus, (a1, a2) in sorted(puppy_genotype.items()):
                f.write(f"  {locus} locus: {a1}/{a2}\n")
            f.write("\n")
            
            # DNA Summary
            f.write("DNA SEQUENCE SUMMARY\n")
            f.write("-" * 70 + "\n")
            
            total_length = 0
            total_mutations = 0
            
            for gene, data in sorted(dna_results.items()):
                alleles = ', '.join(data.get('alleles', []))
                length = len(data['mutated_sequence'])
                mutations = data.get('mutations_applied', [])
                
                total_length += length
                total_mutations += len(mutations)
                
                f.write(f"\n{gene} Gene:\n")
                f.write(f"  Alleles: {alleles}\n")
                f.write(f"  Sequence length: {length:,} base pairs\n")
                f.write(f"  Mutations: {len(mutations)}\n")
                
                if mutations:
                    for mut in mutations:
                        f.write(f"    • {mut['allele']}: {mut['description']}\n")
                        f.write(f"      Type: {mut['type']}, Position: {mut['position']}\n")
            
            f.write("\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total DNA analyzed: {total_length:,} base pairs\n")
            f.write(f"Total mutations: {total_mutations}\n")
            f.write("=" * 70 + "\n")
        
        return filepath


# Example usage
if __name__ == "__main__":
    from Sequence.genotype_to_sequence import GenotypeToSequence
    from logic.phenotype_interpreter import PhenotypeInterpreter
    
    # Setup
    converter = GenotypeToSequence(
        "Sequence/Reference.json",
        "Sequence/extracted_genes"
    )
    exporter = DNAExporter(converter)
    interpreter = PhenotypeInterpreter()
    
    # Example puppy genotype
    puppy_genotype = {
        "E": ("E", "e"),
        "K": ("Kb", "ky"),
        "A": ("Ay", "at"),
        "B": ("B", "b"),
        "D": ("D", "d"),
        "M": ("m", "m"),
        "S": ("S", "S"),
        "L": ("L", "l")
    }
    
    # Get phenotype description
    description = interpreter.get_full_description(puppy_genotype)
    
    print("=" * 70)
    print("DNA Exporter - Example")
    print("=" * 70)
    print(f"\nPuppy genotype: {puppy_genotype}")
    print(f"Phenotype: {description}")
    print("\nExporting DNA...")
    
    # Export individual gene files
    files = exporter.export_puppy_dna(puppy_genotype, 1, puppy_name="Max")
    print(f"\n✓ Exported {len(files)} gene files:")
    for gene, filepath in files.items():
        print(f"  • {gene}: {filepath}")
    
    # Export complete genome
    complete_file = exporter.export_complete_genome(puppy_genotype, 1, puppy_name="Max")
    print(f"\n✓ Complete genome: {complete_file}")
    
    # Create summary report
    report_file = exporter.create_summary_report(
        puppy_genotype, 1, description, puppy_name="Max"
    )
    print(f"✓ Summary report: {report_file}")
    print("\n" + "=" * 70)
