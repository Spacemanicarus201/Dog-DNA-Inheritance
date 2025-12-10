#!/usr/bin/env python3
"""read_sequence.py

Small utility to read DNA sequences from FASTA (.fna/.fa) files and optionally parse GFF.
Features:
- Streaming region extraction (doesn't load whole genome) for large FASTA files
- Full FASTA parsing for small files
- Simple GFF parser that yields features
- CLI with examples
"""

from __future__ import annotations
import argparse
import glob
import gzip
import io
import os
import sys
from typing import Dict, Generator, Tuple, Optional


def open_maybe_gzip(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "r")


def parse_fasta_all(path: str) -> Dict[str, str]:
    """Parse entire FASTA file into dict {header: sequence}.
    Use for small files or when you actually need whole sequences in memory.
    """
    seqs: Dict[str, list[str]] = {}
    header: Optional[str] = None
    with open_maybe_gzip(path) as fh:
        for line in fh:
            line = line.rstrip("\n\r")
            if not line:
                continue
            if line.startswith(">"):
                header = line[1:].split()[0]
                seqs[header] = []
            else:
                if header is None:
                    raise ValueError("Found sequence data before header in FASTA")
                seqs[header].append(line.strip())
    return {h: ''.join(parts) for h, parts in seqs.items()}


def fasta_headers(path: str) -> Generator[str, None, None]:
    """Yield headers (ids) in the FASTA file (first token after '>')."""
    with open_maybe_gzip(path) as fh:
        for line in fh:
            if line.startswith(">"):
                yield line[1:].split()[0]


def extract_region_stream(path: str, seqid: Optional[str], start: int, end: int) -> str:
    """Extract subsequence [start,end] (1-based inclusive) for `seqid`.

    If `seqid` is None, the first sequence in the FASTA is used.
    This function streams the FASTA file so it can handle large genome files.
    """
    if start < 1 or end < start:
        raise ValueError("Invalid coordinates: start must be >=1 and end >= start")

    in_target = False
    current_id = None
    pos = 0  # number of bases seen so far in current sequence
    pieces: list[str] = []

    with open_maybe_gzip(path) as fh:
        for raw in fh:
            line = raw.rstrip("\n\r")
            if not line:
                continue
            if line.startswith(">"):
                # header
                header_id = line[1:].split()[0]
                if seqid is None and current_id is None:
                    # first sequence becomes target if seqid omitted
                    if header_id:
                        in_target = True
                        current_id = header_id
                    else:
                        in_target = False
                else:
                    if header_id == seqid:
                        in_target = True
                        current_id = header_id
                    else:
                        # if we already started and have collected desired region, we can stop
                        if in_target and pieces:
                            break
                        in_target = False
                        current_id = header_id
                pos = 0
                continue

            if not in_target:
                continue

            seq_line = line.strip()
            if not seq_line:
                continue
            line_len = len(seq_line)
            chunk_start = pos + 1
            chunk_end = pos + line_len

            # if the chunk is entirely before the requested region
            if chunk_end < start:
                pos += line_len
                continue

            # find overlap
            s_idx = max(0, start - pos - 1)  # 0-based index into seq_line
            e_idx = min(line_len, end - pos)  # exclusive index into seq_line
            if s_idx < e_idx:
                pieces.append(seq_line[s_idx:e_idx])

            pos += line_len

            if pos >= end:
                break

    return ''.join(pieces)


def parse_gff(path: str) -> Generator[Dict[str, str], None, None]:
    """Simple GFF parser yielding dicts with keys: seqid, source, type, start, end, score, strand, phase, attributes (parsed as dict).
    Does minimal validation; for heavy use prefer Biopython or similar.
    """
    def parse_attrs(attrstr: str) -> Dict[str, str]:
        out = {}
        for part in attrstr.split(";"):
            if not part:
                continue
            if "=" in part:
                k, v = part.split("=", 1)
            elif " " in part:
                k, v = part.split(" ", 1)
            else:
                continue
            out[k.strip()] = v.strip()
        return out

    openf = open_maybe_gzip
    with openf(path) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n\r").split("\t")
            if len(parts) < 9:
                continue
            seqid, source, typ, start, end, score, strand, phase, attrs = parts[:9]
            yield {
                "seqid": seqid,
                "source": source,
                "type": typ,
                "start": start,
                "end": end,
                "score": score,
                "strand": strand,
                "phase": phase,
                "attributes": parse_attrs(attrs),
            }


def find_gene_features_in_gff(gff_path: str, gene_names: list[str], feature_order=('gene', 'mRNA', 'CDS')) -> Dict[str, list[Dict[str, str]]]:
    """Scan GFF once and collect best-matching features for each gene name.

    Returns a dict mapping gene_name -> list of matching features (selected by feature_order).
    Matching is case-insensitive and checks common attribute keys and attribute values.
    """
    # temporary store: gene -> feature_type -> [features]
    store: Dict[str, Dict[str, list[Dict[str, str]]]] = {g: {} for g in gene_names}

    for feat in parse_gff(gff_path):
        attrs = feat.get('attributes') or {}
        attr_values = [v for v in attrs.values() if v]
        ftype = feat.get('type')
        for gene in gene_names:
            gl = gene.lower()
            matched = False
            # check attribute values for token or substring matches
            for v in attr_values:
                vl = v.lower()
                if vl == gl or gl in vl.split() or gl in vl.split(',') or gl in vl:
                    matched = True
                    break
            # check common keys
            if not matched:
                for k in ('Name', 'gene', 'ID', 'gene_name', 'locus_tag', 'gene_symbol', 'Alias'):
                    val = attrs.get(k)
                    if val and val.lower() == gl:
                        matched = True
                        break

            if matched:
                store[gene].setdefault(ftype, []).append(feat)

    # pick best feature type per gene according to priority
    out: Dict[str, list[Dict[str, str]]] = {}
    for gene in gene_names:
        picked: list[Dict[str, str]] = []
        for typ in feature_order:
            lst = store[gene].get(typ)
            if lst:
                picked = lst
                break
        out[gene] = picked

    return out


def format_fasta(header: str, seq: str, width: int = 60) -> str:
    lines = [f">"+header]
    for i in range(0, len(seq), width):
        lines.append(seq[i:i+width])
    return "\n".join(lines) + "\n"


def parse_region(s: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    # region forms supported: seqid:start-end OR start-end
    if ":" in s:
        seqid, coords = s.split(":", 1)
    else:
        seqid = None
        coords = s
    sep = "-" if "-" in coords else ":"
    if sep not in coords:
        raise argparse.ArgumentTypeError("Region must be START-END or SEQID:START-END")
    start_s, end_s = coords.split(sep, 1)
    try:
        start = int(start_s)
        end = int(end_s)
    except ValueError:
        raise argparse.ArgumentTypeError("Start and end must be integers")
    return seqid, start, end


# --- Mutation finding logic for extracted gene FASTAs ---
def find_mutation_index(filename, context_seq):
    try:
        from Bio import SeqIO
    except ImportError:
        print("Biopython is required for mutation finding.", file=sys.stderr)
        return None
    if not os.path.exists(filename):
        return None
    record = SeqIO.read(filename, "fasta")
    seq = str(record.seq)
    match_index = seq.find(context_seq)
    if match_index == -1:
        return None
    offset = len(context_seq) // 2
    exact_mutation_index = match_index + offset
    return exact_mutation_index

def print_mutation_summary(directory="extracted_genes"):
    mutations = {
        "TYRP1": { "gene": "TYRP1", "context": "CCTCCCAGTTA", "ref": "C", "mut": "T", "desc": "Brown (b) Mutation" },
        "FGF5": { "gene": "FGF5", "context": "TTGGTGGAAAA", "ref": "G", "mut": "T", "desc": "Long Hair (l) Mutation" },
        "ASIP": { "gene": "ASIP", "context": "GGGGGCAGAAG", "ref": "C", "mut": "T", "desc": "Recessive Black (a) Mutation" },
        "MC1R": { "gene": "MC1R", "context": "GTGTGCAGCTA", "ref": "C", "mut": "T", "desc": "Recessive Red (e) Mutation" }
    }
    print(f"Checking for mutations in directory: {directory}...")
    for locus, info in mutations.items():
        # Handle the _1 suffix if multiple transcripts were found, defaulting to first one found or name without suffix
        base_fname = os.path.join(directory, f"{locus}_template.fasta")
        fname_v1 = os.path.join(directory, f"{locus}_1_template.fasta")
        
        target_file = None
        if os.path.exists(base_fname):
            target_file = base_fname
        elif os.path.exists(fname_v1):
            target_file = fname_v1
            
        if target_file:
            idx = find_mutation_index(target_file, info["context"])
            if idx is not None:
                print(f"{info['desc']} ({locus}): Found at index {idx}, change {info['ref']} to {info['mut']}")
            else:
                print(f"{info['desc']} ({locus}): Context not found in {target_file}!")
        else:
             print(f"{info['desc']} ({locus}): Gene file not found in {directory}.")


def main(argv=None):
    p = argparse.ArgumentParser(description="Read DNA sequences from FASTA (streaming region extraction supported)")
    p.add_argument("-f", "--fasta", required=False, help="FASTA file (.fna/.fa). Can be gzipped (.gz). If omitted the first FASTA found in cwd will be used")
    p.add_argument("-g", "--gff", help="Optional GFF file to parse annotations")
    p.add_argument("-s", "--seqid", help="Sequence id to use (first token after '>'). If omitted and region not given, first sequence is used")
    p.add_argument("-r", "--region", help="Region to extract. Use START-END or SEQID:START-END (1-based inclusive). Example: 1000-2000 or chr1:1000-2000")
    p.add_argument("-o", "--out", help="Write output to file (default stdout)")
    p.add_argument("--fasta-output", action="store_true", help="Output in FASTA format (header will be seqid or seqid:start-end)")
    p.add_argument("--genes", help="Comma-separated list of gene names to extract (e.g. MC1R,TYRP1)")
    p.add_argument("--genes-file", help="File with one gene name per line")
    p.add_argument("--out-dir", help="Directory to write extracted gene FASTA files (default: current directory)")
    p.add_argument("--feature-type", choices=["gene", "mRNA", "CDS"], default="gene", help="Which GFF feature to match for gene coordinates")
    p.add_argument("--flank", type=int, default=0, help="Number of bases to add as flank on each side of extracted region")


    p.add_argument("--check-mutations", action="store_true", help="Check for known mutations in extracted gene files")

    args = p.parse_args(argv)

    def find_first_file(exts):
        # return first matching filename for given extensions (case-insensitive)
        for ext in exts:
            # match both lower and upper case
            for f in glob.glob(f"*{ext}") + glob.glob(f"*{ext.upper()}"):
                if os.path.isfile(f):
                    return f
        return None

    # auto-detect FASTA/GFF when omitted
    if not args.fasta:
        fasta_candidate = find_first_file([".fna", ".fa", ".fasta", ".fna.gz", ".fa.gz", ".fasta.gz"])
        if fasta_candidate:
            args.fasta = fasta_candidate
            print(f"Auto-detected FASTA: {args.fasta}", file=sys.stderr)
        else:
            print("No FASTA file provided and none found in current directory", file=sys.stderr)
            p.print_help()
            sys.exit(2)

    if not args.gff and os.path.isdir('.'):
        gff_candidate = find_first_file([".gff", ".gff3", ".gff.gz", ".gff3.gz"])
        if gff_candidate:
            # only set if user didn't explicitly request none
            args.gff = gff_candidate
            print(f"Auto-detected GFF: {args.gff}", file=sys.stderr)

    # If user requested gene extraction, do it now (before any full-FASTA dump)
    if (args.genes or args.genes_file):
        if not args.gff:
            print("Cannot extract genes: no GFF file provided or auto-detected", file=sys.stderr)
            sys.exit(2)
        out_dir = args.out_dir or os.getcwd()
        os.makedirs(out_dir, exist_ok=True)
        # build gene list
        genes: list[str] = []
        if args.genes:
            genes.extend([g.strip() for g in args.genes.split(",") if g.strip()])
        if args.genes_file:
            with open(args.genes_file, "r", encoding="utf-8") as gf:
                for line in gf:
                    line = line.strip()
                    if line:
                        genes.append(line)

        # find features matching requested genes
        matches: Dict[str, list[Dict[str, str]]] = {g: [] for g in genes}
        for feat in parse_gff(args.gff):
            # match only requested feature type
            if feat["type"] != args.feature_type:
                continue
            attrs = feat.get("attributes") or {}
            attr_values = [v for v in attrs.values()]
            for gene in genes:
                gene_low = gene.lower()
                found = False
                for v in attr_values:
                    if v.lower() == gene_low or gene_low in v.lower().split(",") or gene_low in v.lower().split(";"):
                        found = True
                        break
                if not found:
                    for k in ("Name", "gene", "ID", "gene_name", "locus_tag"):
                        val = attrs.get(k)
                        if val and val.lower() == gene_low:
                            found = True
                            break
                if found:
                    matches[gene].append(feat)

        # extract sequence(s) for each matched gene
        for gene, feats in matches.items():
            if not feats:
                print(f"Warning: gene {gene} not found in {args.gff}", file=sys.stderr)
                continue
            for i, feat in enumerate(feats, start=1):
                seqid = feat["seqid"]
                start = int(feat["start"]) - args.flank
                end = int(feat["end"]) + args.flank
                if start < 1:
                    start = 1
                subseq = extract_region_stream(args.fasta, seqid, start, end)
                if not subseq:
                    print(f"No sequence extracted for {gene} {seqid}:{start}-{end}", file=sys.stderr)
                    continue
                suffix = f"_{i}" if len(feats) > 1 else ""
                fname = os.path.join(out_dir, f"{gene}{suffix}_template.fasta")
                header = f"{gene}|{seqid}:{start}-{end}|strand={feat.get('strand','.') }"
                with open(fname, "w", encoding="utf-8") as ofh:
                    ofh.write(format_fasta(header, subseq))
                print(f"Wrote {fname}")
        
        # If check mutations is requested, do it now
        if args.check_mutations:
            print_mutation_summary(out_dir)

        # finished gene extraction — exit to avoid further stdout dumping
        return

    if args.check_mutations:
        # If run without extraction but with check-mutations
        out_dir = args.out_dir or "extracted_genes"
        print_mutation_summary(out_dir)
        return

    if args.region:
        seqid_from_region, start, end = parse_region(args.region)
        seqid = seqid_from_region or args.seqid
        subseq = extract_region_stream(args.fasta, seqid, start, end)
        if not subseq:
            print(f"No sequence found for {seqid} {start}-{end}", file=sys.stderr)
            sys.exit(1)
        header = f"{seqid or 'seq'}:{start}-{end}"
        out_text = format_fasta(header, subseq) if args.fasta_output else subseq + "\n"
    else:
        # no region: either dump full sequence for seqid or parse all
        if args.seqid:
            # warn about memory
            print("Reading full sequence into memory for seqid; may be heavy for large genomes", file=sys.stderr)
            seqs = parse_fasta_all(args.fasta)
            if args.seqid not in seqs:
                print(f"Sequence id {args.seqid} not found in {args.fasta}", file=sys.stderr)
                sys.exit(1)
            seq = seqs[args.seqid]
            out_text = format_fasta(args.seqid, seq) if args.fasta_output else seq + "\n"
        else:
            # no seqid and no region: dump the whole FASTA file (stream copy)
            if args.out:
                with open(args.out, "wb") as outfh:
                    with open_maybe_gzip(args.fasta) as infh:
                        # if infh is text-mode, read text and write bytes
                        data = infh.read()
                        outfh.write(data.encode("utf-8"))
                print(f"Wrote copy of {args.fasta} to {args.out}")
                return
            else:
                with open_maybe_gzip(args.fasta) as infh:
                    for line in infh:
                        sys.stdout.write(line)
                return

    if args.out:
        mode = "wb"
        with open(args.out, mode) as ofh:
            ofh.write(out_text.encode("utf-8"))
    else:
        sys.stdout.write(out_text)

    # optionally parse GFF and print a tiny summary
    if args.gff:
        n = 0
        for feat in parse_gff(args.gff):
            n += 1
            if n <= 5:
                # print first few features to stderr for quick check
                print(f"GFF feature: {feat['seqid']} {feat['type']} {feat['start']}-{feat['end']}", file=sys.stderr)
        print(f"Parsed {n} features from {args.gff}", file=sys.stderr)


if __name__ == "__main__":
    # If run without any arguments, automatically extract genes
    if len(sys.argv) == 1:
        # Auto mode: extract the 4 genes of interest
        genes_to_extract = ["TYRP1", "FGF5", "ASIP", "MC1R"]
        
        print("=" * 60)
        print("Dog DNA Gene Extractor - Auto Mode")
        print("=" * 60)
        print(f"Extracting genes: {', '.join(genes_to_extract)}")
        print()
        
        # Auto-detect files
        fasta_file = None
        gff_file = None
        
        for ext in [".fna", ".fa", ".fasta", ".fna.gz", ".fa.gz", ".fasta.gz"]:
            for f in glob.glob(f"*{ext}") + glob.glob(f"*{ext.upper()}"):
                if os.path.isfile(f):
                    fasta_file = f
                    break
            if fasta_file:
                break
        
        for ext in [".gff", ".gff3", ".gff.gz", ".gff3.gz"]:
            for f in glob.glob(f"*{ext}") + glob.glob(f"*{ext.upper()}"):
                if os.path.isfile(f):
                    gff_file = f
                    break
            if gff_file:
                break
        
        if not fasta_file:
            print("ERROR: No FASTA file (.fna, .fa, .fasta) found in current directory!")
            sys.exit(1)
        
        if not gff_file:
            print("ERROR: No GFF file (.gff, .gff3) found in current directory!")
            sys.exit(1)
        
        print(f"Using FASTA file: {fasta_file}")
        print(f"Using GFF file: {gff_file}")
        print()
        
        # Create output directory
        out_dir = "extracted_genes"
        os.makedirs(out_dir, exist_ok=True)
        
        # Extract genes
        matches: Dict[str, list[Dict[str, str]]] = {g: [] for g in genes_to_extract}
        for feat in parse_gff(gff_file):
            if feat["type"] != "gene":
                continue
            attrs = feat.get("attributes") or {}
            attr_values = [v for v in attrs.values()]
            for gene in genes_to_extract:
                gene_low = gene.lower()
                found = False
                for v in attr_values:
                    if v.lower() == gene_low or gene_low in v.lower().split(",") or gene_low in v.lower().split(";"):
                        found = True
                        break
                if not found:
                    for k in ("Name", "gene", "ID", "gene_name", "locus_tag"):
                        val = attrs.get(k)
                        if val and val.lower() == gene_low:
                            found = True
                            break
                if found:
                    matches[gene].append(feat)
        
        # Extract sequences
        for gene, feats in matches.items():
            if not feats:
                print(f"⚠ Warning: gene {gene} not found in {gff_file}")
                continue
            for i, feat in enumerate(feats, start=1):
                seqid = feat["seqid"]
                start = int(feat["start"])
                end = int(feat["end"])
                if start < 1:
                    start = 1
                subseq = extract_region_stream(fasta_file, seqid, start, end)
                if not subseq:
                    print(f"⚠ No sequence extracted for {gene} {seqid}:{start}-{end}")
                    continue
                suffix = f"_{i}" if len(feats) > 1 else ""
                fname = os.path.join(out_dir, f"{gene}{suffix}_template.fasta")
                header = f"{gene}|{seqid}:{start}-{end}|strand={feat.get('strand','.') }"
                with open(fname, "w", encoding="utf-8") as ofh:
                    ofh.write(format_fasta(header, subseq))
                print(f"✓ Wrote {fname}")
        
        print()
        print("Checking for known mutations...")
        print_mutation_summary(out_dir)
        print()
        print("=" * 60)
        print("Extraction complete!")
        print("=" * 60)
    else:
        # Run with command-line arguments as before
        main()
