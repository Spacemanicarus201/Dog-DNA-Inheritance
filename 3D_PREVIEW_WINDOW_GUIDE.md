# 3D Dog Preview Window - Feature Guide

## Overview
Added a **separate 3D preview window** that shows live dog models synchronized with trait selection!

## How It Works

### Two Windows Working Together
1. **Main Window** (Pygame) - Trait selection interface
2. **Preview Window** (OpenGL) - Two 3D dog models side-by-side

The windows are **synchronized in real-time** - when you change traits in the main window, the 3D models update instantly!

## Features

### Split-Screen 3D View
- **Left side**: Father dog (blue indicator)
- **Right side**: Mother dog (pink indicator)
- **Rotating models**: Auto-rotate at 30 FPS
- **Live updates**: Changes reflect immediately

### Toggle Control
- **Button**: "Toggle 3D Preview" (top-right of trait selection)
- **Status indicator**: Shows "3D Preview: Active" or "Off"
- **On/Off**: Click to show/hide the preview window

### Thread-Safe Updates
- Preview window runs in **separate thread**
- **Lock-based synchronization** prevents race conditions
- **Non-blocking**: Main window stays responsive

## Usage

### Automatic Start
When you open trait selection, the preview window automatically opens!

### Manual Control
- Click **"Toggle 3D Preview"** to show/hide
- Window title shows: `"Dog Preview: [Father Breed] × [Mother Breed]"`
- Close preview window with ESC or X button

### Real-Time Updates
As you select traits:
1. Dropdowns change in main window
2. Genotypes computed instantly
3. Preview window updates automatically
4. 3D models reflect new colors/features

## Technical Details

### Architecture
```
TraitSelection (Pygame)
    ↓ (creates)
DogPreviewWindow (OpenGL Thread)
    ↓ (updates via)
Threading Lock (thread-safe)
    ↓ (renders)
Two DogModel instances (father & mother)
```

### Window Specifications
- **Size**: 900×450 pixels
- **Layout**: Split-screen (450×450 per dog)
- **FPS**: 30 frames per second
- **Rotation**: Auto-rotate around Z-axis

### Synchronization
```python
# Main thread (trait selection)
preview_window.update_genotypes(father_geno, mother_geno)

# Preview thread (OpenGL)
with self.lock:
    # Thread-safe read
    father = self.father_genotype.copy()
    mother = self.mother_genotype.copy()
```

## Files Created

1. **`model/dog_preview_window.py`**
   - `DogPreviewWindow` class
   - Threading-based OpenGL window
   - Split-screen rendering

2. **`screens/trait_selection.py`** (modified)
   - Added preview window integration
   - Toggle button
   - Auto-update on trait changes
   - Cleanup on screen exit

## Controls

### Main Window
- **Dropdowns**: Select traits
- **Toggle 3D Preview**: Show/hide preview
- **All other buttons**: Work as before

### Preview Window
- **ESC**: Close window
- **X button**: Close window
- **Auto-rotate**: Models spin automatically

## Visual Indicators

### In Main Window
- **Green text**: "3D Preview: Active"
- **Gray text**: "3D Preview: Off"

### In Preview Window
- **Blue sphere**: Father's side (left)
- **Pink sphere**: Mother's side (right)

## Example Workflow

1. **Select breeds** → Preview window opens
2. **Change father's coat color** → Left dog updates
3. **Change mother's pattern** → Right dog updates
4. **Toggle preview off** → Window closes
5. **Toggle preview on** → Window reopens with current traits
6. **Click "Next"** → Preview closes, proceed to summary

## Benefits

✅ **Real-time feedback** - See changes instantly
✅ **Separate windows** - No UI conflicts
✅ **Non-blocking** - Main window stays responsive
✅ **Easy toggle** - Show/hide as needed
✅ **Automatic cleanup** - Closes when leaving screen

## Troubleshooting

### Preview window doesn't open
- Check console for errors
- OpenGL might not be available
- Try toggling off and on again

### Models don't update
- Check if window is still running
- Try closing and reopening preview
- Check console for update errors

### Window closes unexpectedly
- Normal if you press ESC or X
- Click "Toggle 3D Preview" to reopen

## Future Enhancements

Possible improvements:
- Add zoom controls
- Manual rotation (mouse drag)
- Pause auto-rotation
- Screenshot button
- Side-by-side comparison mode
- Show genotype text overlay
- Highlight changed features

---

**Enjoy your live 3D dog preview!** 🐕🐕✨
