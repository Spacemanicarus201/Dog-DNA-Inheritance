# DNA Sequence Preview Feature

## Overview
Added real DNA sequence preview to each puppy card in the genetic summary page!

## What It Shows

Each puppy card now displays:
```
DNA Preview (MC1R):
ATCGATCGATCGATCGATCGATCGA...
```

- **First 25 base pairs** from the puppy's actual mutated DNA sequence
- **Gene name** (usually MC1R, the first gene processed)
- **Green color** (#96FF96) to indicate DNA/genetic data
- **Monospace-style font** for authentic genetic sequence look

## How It Works

### 1. Lazy Loading
```python
# Only loads DNA converter once, when first needed
if not hasattr(self, '_dna_converter'):
    try:
        from Sequence.genotype_to_sequence import GenotypeToSequence
        self._dna_converter = GenotypeToSequence(...)
        self._dna_available = True
    except:
        self._dna_available = False
```

### 2. DNA Generation
```python
# For each puppy:
dna_results = self._dna_converter.process_genotype(genotype)
first_gene = list(dna_results.keys())[0]  # Usually MC1R
sequence = dna_results[first_gene]['mutated_sequence']
preview = sequence[:25]  # First 25 base pairs
```

### 3. Display
```python
# Shows like this:
DNA Preview (MC1R):
TCACCAGGAACATAGCACTACCTCT...
```

## Visual Design

- **Label**: Small gray text "DNA Preview (MC1R):"
- **Sequence**: Larger green text with "..." at the end
- **Position**: Between summary and similarity scores
- **Card height**: Automatically increases from 200px to 240px when DNA is available

## Performance

- ✅ **Lazy loaded**: DNA converter only initialized once
- ✅ **Cached**: Sequences are cached in memory
- ✅ **Graceful fallback**: If DNA files aren't available, cards work normally
- ✅ **Fast**: Only shows first 25 bp, no heavy processing

## Example Output

```
╔════════════════════════════════════════════════════════╗
║ Puppy #1                                               ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║ This dog will have a solid black coat, short coat.    ║
║                                                        ║
║ Summary: Solid black, short coat                      ║
║                                                        ║
║ DNA Preview (MC1R):                                    ║
║ TCACCAGGAACATAGCACTACCTCT...                          ║
║                                                        ║
║ ♂ Father similarity: 75%    ♀ Mother similarity: 50%  ║
║                                                        ║
║ Genetic Details:                                       ║
║ E:E/E  K:Kb/Kb  A:Ay/Ay  B:B/B  D:D/D  M:m/m  S:S/S   ║
╚════════════════════════════════════════════════════════╝
```

## Benefits

1. **Educational**: Shows real genetic data
2. **Authentic**: Uses actual dog genome sequences
3. **Engaging**: Makes genetics tangible and real
4. **Scientific**: Each puppy has unique DNA
5. **Cool factor**: DNA sequences look professional! 🧬

## Future Enhancements

Possible additions:
- Show multiple genes (MC1R, ASIP, TYRP1)
- Highlight mutation positions
- Color-code bases (A=green, T=red, G=blue, C=yellow)
- Click to expand full sequence
- Export button per puppy
- Compare DNA between siblings

## Files Modified

- `screens/genetic_summary.py` - Added DNA preview to puppy cards
- Card height increased to 240px when DNA available
- Green color scheme for DNA data

## Dependencies

- `Sequence/genotype_to_sequence.py` - Converts genotype to DNA
- `Sequence/Reference.json` - Mutation definitions
- `Sequence/extracted_genes/*.fasta` - Template sequences

## Usage

Just run the app! The DNA preview appears automatically if:
1. Gene template files exist in `Sequence/extracted_genes/`
2. `Reference.json` is properly configured
3. `genotype_to_sequence.py` is working

If DNA files aren't available, the cards work normally without the preview (graceful degradation).

---

**Result**: Each puppy now shows a snippet of their actual, unique DNA sequence! 🧬✨
