# read_sequence.py

Small utility to read DNA sequences from FASTA files and optionally parse GFF.

Features:
- Streaming region extraction (doesn't load whole genome into memory)
- Full FASTA parsing for small files
- Simple GFF parsing for quick checks

Usage examples (PowerShell):

# Print a region (seqid optional) in plain sequence form
python .\read_sequence.py -f .\GCF_000002285.3_CanFam3.1_genomic.fna -r chr1:100000-100099

# Print a region in FASTA format
python .\read_sequence.py -f .\GCF_000002285.3_CanFam3.1_genomic.fna -r chr1:100000-100099 --fasta-output

# Extract a whole sequence (may use a lot of memory for genomes)
python .\read_sequence.py -f .\GCF_000002285.3_CanFam3.1_genomic.fna -s chr1 --fasta-output

# Copy the entire FASTA to a new file (streamed)
python .\read_sequence.py -f .\GCF_000002285.3_CanFam3.1_genomic.fna -o .\copy.fna

# Parse GFF and show a short summary (prints a few features to stderr)
python .\read_sequence.py -f .\GCF_000002285.3_CanFam3.1_genomic.fna -g .\genomic.gff

Notes:
- Coordinates are 1-based inclusive.
- For very large genomes prefer using the `-r` region option to avoid loading entire chromosomes into memory.
- GFF parsing here is minimal; for complex annotation queries use Biopython or pybedtools.
