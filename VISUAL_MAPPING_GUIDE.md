# Visual Mapping - Complete Guide

## Overview
This document shows how each genetic option affects the dog's visual appearance in the 3D model.

## Visual Parameters

The dog model uses these visual parameters:
- `body_color` - Main body color (RGB 0-1)
- `head_color` - Head color (RGB 0-1)
- `leg_color` - Leg and ear color (RGB 0-1)
- `leg_scale` - Leg length multiplier (1.0 = normal, 1.15 = long)
- `ear_scale` - Ear size multiplier
- `snout_forward` - Snout length (0.06 = short, 0.12 = long)
- `spotted` - Boolean for white patches
- `spot_pattern` - Type: 'si', 'sp', 'sw'
- `merle` - Boolean for merle patches

---

## E Locus (Extension) - Coat Color

### e/e - Recessive Red/Golden
- **Body**: Golden (0.92, 0.7, 0.2)
- **Head**: Slightly lighter golden
- **Effect**: Overrides all other color genes!

### E/e or E/E - Black Extension
- **Body**: Allows other genes to show
- **Effect**: Normal pigment production

### Em/Em, Em/E, Em/e - Masked Face
- **Body**: Allows other genes to show
- **Effect**: Dark facial mask (currently same as E)

---

## K Locus (Dominance) - Pattern Control

### Kb/Kb or Kb/ky - Dominant Black
- **Body**: Solid black (0.05, 0.05, 0.05)
- **Head**: Solid black
- **Effect**: Overrides A locus patterns

### kbr/kbr or kbr/ky - Brindle
- **Body**: Brown-golden mix (0.58, 0.43, 0.22)
- **Head**: Same as body
- **Effect**: Striped pattern (shown as mixed color)

### ky/ky - Allows Agouti
- **Body**: A locus patterns show through
- **Effect**: Normal pattern expression

---

## A Locus (Agouti) - Pattern Type
*(Only visible if K locus allows it)*

### Ay/Ay or Ay/? - Sable/Fawn
- **Body**: Golden-brown mix (0.73, 0.55, 0.23)
- **Legs**: Darker brown
- **Snout**: Normal length (0.12)

### aw/aw or aw/? - Wolf Sable
- **Body**: Gray-brown mix (0.53, 0.43, 0.33)
- **Legs**: Grizzled gray
- **Snout**: Medium length (0.10)

### at/at or at/? - Tan Points
- **Body**: Black
- **Legs**: Tan/wheat color (0.94, 0.79, 0.60)
- **Snout**: Short (0.06)
- **Effect**: Black body with tan "points"

### a/a - Recessive Black
- **Body**: Solid black
- **Legs**: Same as body (uniform)
- **Snout**: Normal (0.12)

---

## B Locus (Brown) - Pigment Color

### B/B or B/b - Black Eumelanin
- **Effect**: Normal black pigment
- **No change**: Uses colors from other genes

### b/b - Brown/Liver
- **Effect**: Converts black → brown (0.45, 0.25, 0.07)
- **Example**: Black dog becomes brown

---

## D Locus (Dilution) - Color Intensity

### D/D or D/d - Full Color
- **Effect**: Normal color intensity
- **No change**: Uses colors from other genes

### d/d - Diluted
- **Black** → **Blue/Gray** (0.35, 0.4, 0.5)
- **Brown** → **Isabella/Lilac** (0.55, 0.45, 0.4)
- **Golden** → **Cream** (lighter golden)

---

## M Locus (Merle) - Pattern Modifier

### m/m - Non-Merle
- **Effect**: No merle pattern
- **No change**: Normal solid color

### M/m - Merle
- **Body**: Lightened by 25% (mixed with white)
- **Effect**: Patchy, mottled appearance
- **Flag**: `merle = True`

### M/M - Double Merle
- **Body**: Lightened by 40% (very pale)
- **Head**: Also lightened by 40%
- **Effect**: Mostly white with health risks
- **Flag**: `merle = True`

---

## S Locus (Spotting) - White Patches

### S/S - Solid Coat
- **Effect**: No white patches
- **No change**: Normal color

### si/si or S/si - Irish Spotting
- **Body**: Lightened by 15%
- **Pattern**: 'si'
- **Effect**: Small white patches (chest, paws)

### sp/sp or S/sp - Piebald
- **Body**: Lightened by 40%
- **Pattern**: 'sp'
- **Effect**: Large white patches

### sw/sw or S/sw - Extreme White
- **Body**: White (0.95, 0.95, 0.95)
- **Head**: White
- **Pattern**: 'sw'
- **Effect**: Mostly white coat

---

## L Locus (Coat Length) - Fur Length

### L/L - Short Coat
- **Legs**: Darker (mixed with brown 20%)
- **Leg scale**: 1.0 (normal)
- **Effect**: Sleek, short fur

### L/l - Medium Coat (Carrier)
- **Legs**: Slightly lighter (mixed with wheat 15%)
- **Leg scale**: 1.08 (slightly longer)
- **Ear scale**: 1.08
- **Effect**: Medium-length fur

### l/l - Long Coat
- **Legs**: Much lighter (mixed with wheat 30%)
- **Leg scale**: 1.15 (noticeably longer)
- **Ear scale**: 1.15
- **Effect**: Fluffy, long fur appearance

---

## Color Palettes

```python
'golden':   (0.92, 0.7, 0.2)   # Bright golden/yellow
'brown':    (0.45, 0.25, 0.07) # Dark brown/liver
'black':    (0.05, 0.05, 0.05) # Very dark gray (almost black)
'white':    (0.95, 0.95, 0.95) # Off-white
'gray':     (0.6, 0.6, 0.65)   # Medium gray
'wheat':    (0.96, 0.87, 0.7)  # Tan/wheat color
'blue':     (0.35, 0.4, 0.5)   # Diluted black (blue-gray)
'isabella': (0.55, 0.45, 0.4)  # Diluted brown (lilac)
```

---

## Example Combinations

### Golden Retriever
```
E: e/e, K: ky/ky, A: Ay/Ay, B: B/B, D: D/D, M: m/m, S: S/S, L: l/l
→ Golden body, lighter legs (fluffy), long coat
```

### German Shepherd
```
E: E/E, K: ky/ky, A: at/at, B: B/B, D: D/D, M: m/m, S: S/S, L: L/L
→ Black body, tan legs, short snout, short coat
```

### Labrador (Black)
```
E: E/E, K: Kb/Kb, A: Ay/Ay, B: B/B, D: D/D, M: m/m, S: S/S, L: L/L
→ Solid black body and legs, short coat
```

### Labrador (Chocolate)
```
E: E/E, K: Kb/Kb, A: Ay/Ay, B: b/b, D: D/D, M: m/m, S: S/S, L: L/L
→ Solid brown body and legs, short coat
```

### Blue Merle Border Collie
```
E: E/E, K: ky/ky, A: at/at, B: B/B, D: d/d, M: M/m, S: S/S, L: L/L
→ Blue-gray body (diluted + merle), tan legs, short coat
```

### Dalmatian
```
E: E/E, K: ky/ky, A: Ay/Ay, B: B/B, D: D/D, M: m/m, S: sp/sp, L: L/L
→ White body with piebald pattern, short coat
```

---

## Visual Changes Summary

| Gene | Affects | Visibility |
|------|---------|-----------|
| **E** | Body/head color | ⭐⭐⭐ High |
| **K** | Body/head color | ⭐⭐⭐ High |
| **A** | Leg color, snout | ⭐⭐ Medium |
| **B** | Pigment color | ⭐⭐⭐ High |
| **D** | Color intensity | ⭐⭐⭐ High |
| **M** | Body lightness | ⭐⭐ Medium |
| **S** | Body lightness | ⭐⭐ Medium |
| **L** | Leg color, scale | ⭐⭐ Medium |

---

## All Options Have Visual Effects! ✅

Every genetic option now changes the dog's appearance:
- **Colors**: E, K, A, B, D all affect body/leg colors
- **Patterns**: M, S add lightening/patches
- **Structure**: L changes leg color and scale
- **Details**: A affects snout length

The visual differences are now more noticeable, especially for coat length!
