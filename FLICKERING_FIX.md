# Dog Model Flickering - Fix

## Problem
The 3D dog model was **flickering** constantly when displayed.

## Root Cause
The `compute_visual_params()` function was using `random.choice()` to simulate offspring:

```python
# OLD CODE (caused flickering):
from_father = random.choice(father_alleles)  # Different every call!
from_mother = random.choice(mother_alleles)  # Different every call!
```

Since this function was called **every frame** to render the dog, it generated a **different random offspring each time**, causing the colors to flicker rapidly.

## Solution
Made the function **deterministic** by using a dominance-based selection instead of random:

```python
# NEW CODE (deterministic):
# Sort alleles by dominance order
dominance = {
    'E': ['Em', 'E', 'e'],  # Most dominant first
    'K': ['Kb', 'kbr', 'ky'],
    # ...
}

# Pick the two most dominant alleles
all_alleles.sort(key=dominance_key)
offspring[locus] = (all_alleles[0], all_alleles[1])
```

### How It Works

1. **Collect all alleles** from both parents
2. **Sort by dominance** using predefined dominance hierarchy
3. **Pick top 2** most dominant alleles
4. **Always returns same result** for same parents

### Dominance Hierarchy

```python
'E': ['Em', 'E', 'e']        # Masked > Black > Red
'K': ['Kb', 'kbr', 'ky']     # Dominant black > Brindle > Agouti
'A': ['Ay', 'aw', 'at', 'a'] # Sable > Wolf > Tan > Recessive
'B': ['B', 'b']              # Black > Brown
'D': ['D', 'd']              # Full > Dilute
'M': ['M', 'm']              # Merle > Non-merle
'S': ['S', 'si', 'sp', 'sw'] # Solid > Irish > Piebald > Extreme
'L': ['L', 'l']              # Short > Long
```

## Example

### Before (Random - Flickering)
```python
Father: E/e, Mother: E/e
Frame 1: offspring = E/E → Black dog
Frame 2: offspring = E/e → Black dog  
Frame 3: offspring = e/e → Golden dog  ← FLICKER!
Frame 4: offspring = E/e → Black dog
```

### After (Deterministic - Stable)
```python
Father: E/e, Mother: E/e
Every frame: offspring = E/E → Black dog (always picks most dominant)
```

## Trade-offs

### ✅ Pros
- **No flickering** - stable, consistent display
- **Deterministic** - same input = same output
- **Shows dominant traits** - displays most likely phenotype
- **Fast** - no random number generation

### ⚠️ Cons
- **Not random** - always shows same "offspring"
- **Biased toward dominant** - doesn't show recessive possibilities
- **Not realistic** - real offspring vary

## Better Approach (Future)

For showing actual offspring variation, use `compute_visual_params_from_offspring()` with **actual offspring genotypes** from Monte Carlo simulation:

```python
# In genetic_summary.py or similar:
from model.visual_mapping import compute_visual_params_from_offspring

for puppy in monte_carlo_puppies:
    visual_params = compute_visual_params_from_offspring(puppy["genotype"])
    # Each puppy gets its own stable, unique appearance
```

This way:
- Each puppy has a **stable** appearance (no flickering)
- Puppies show **realistic variation**
- Uses **actual Mendelian inheritance**

## Files Modified

- `model/visual_mapping.py`
  - Removed `random.choice()` calls
  - Added dominance hierarchy
  - Made `compute_visual_params()` deterministic

## Result

✅ **No more flickering!**
✅ Dog model displays **stable, consistent** colors
✅ Shows **dominant phenotype** from parent combination
✅ Backward compatible with existing code

---

**The dog model should now display smoothly without flickering!** 🐕✨
