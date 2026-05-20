# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 10:27:23 2026
@author: Pedro Gomez Galvez / Gemini
"""

import os
import glob
from skimage.io import imread, imsave
from skimage import exposure
import numpy as np

# --- Configuration ---
INPUT_DIR = 'F:/Lab/MAMDC2/Extracellular matrix/raw images/first_batch'
OUTPUT_DIR = 'F:/Lab/MAMDC2/Extracellular matrix/tiled_images/first_second_batches_enhanced/withAA'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Get a list of all .tif files
image_files = glob.glob(os.path.join(INPUT_DIR, '*.tif'))

for img_path in image_files:
    filename = os.path.basename(img_path)
    base_name = os.path.splitext(filename)[0]
    
    print(f"Opening: {filename}...")
    img = imread(img_path)
    
    # --- Step 1: Soft Contrast Enhancement (Percentile Rescaling) ---
    # This ignores the darkest 1% and brightest 1% (noise/outliers) 
    # and stretches the middle 98% to fill the full dynamic range.
    print(f"  -> Applying soft contrast stretch...")
    
    p2, p98 = np.percentile(img, (1, 99))
    img_rescaled = exposure.rescale_intensity(img, in_range=(p2, p98))
    
    # Ensure it's in 8-bit format for the output
    # (If your input is 16-bit and you want to keep it 16-bit, 
    # use .astype(np.uint16) instead)
    img_final = img_rescaled.astype(np.uint8)
    
    # Get image dimensions
    img_h, img_w = img_final.shape[0], img_final.shape[1]
    
    # --- Step 2: Dynamic Logic to determine Grid Parameters ---
    if img_h >= 10000 and img_w >= 10000:
        TILE_SIZE = 2500
        GRID_ROWS, GRID_COLS = 4, 4
    elif img_h >= 7500 and img_w >= 7500:
        TILE_SIZE = 2500
        GRID_ROWS, GRID_COLS = 3, 3
    elif img_h >= 3800 and img_w >= 3800:
        TILE_SIZE = 1900
        GRID_ROWS, GRID_COLS = 2, 2
    else:
        print(f"  -> WARNING: {filename} ({img_h}x{img_w}) is too small. Skipping.")
        continue

    # --- Step 3: Centering Logic ---
    TOTAL_HEIGHT = TILE_SIZE * GRID_ROWS
    TOTAL_WIDTH = TILE_SIZE * GRID_COLS
    start_y = (img_h - TOTAL_HEIGHT) // 2
    start_x = (img_w - TOTAL_WIDTH) // 2
    
    # --- Step 4: Tiling ---
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            y1 = start_y + (row * TILE_SIZE)
            y2 = y1 + TILE_SIZE
            x1 = start_x + (col * TILE_SIZE)
            x2 = x1 + TILE_SIZE
            
            tile = img_final[y1:y2, x1:x2]
            
            tile_name = f"{base_name}_R{row}_C{col}.tif"
            tile_path = os.path.join(OUTPUT_DIR, tile_name)
            imsave(tile_path, tile, check_contrast=False)
            
    print(f"  -> Processed and saved {GRID_ROWS * GRID_COLS} tiles for {filename}\n")

print("Soft Enhancement and Tiling process complete!")