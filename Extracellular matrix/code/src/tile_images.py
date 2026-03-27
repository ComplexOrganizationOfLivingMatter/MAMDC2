# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 10:27:23 2026

@author: Pedro Gomez Galvez
"""

import os
import glob
from skimage.io import imread, imsave
import numpy as np

# --- Configuration ---
INPUT_DIR = 'F:/Lab/MAMDC2/Extracellular matrix/raw images'
OUTPUT_DIR = 'F:/Lab/MAMDC2/Extracellular matrix/tiled_images'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Grid parameters
TILE_SIZE = 2500
GRID_ROWS = 4
GRID_COLS = 4
TOTAL_HEIGHT = TILE_SIZE * GRID_ROWS # 10000
TOTAL_WIDTH = TILE_SIZE * GRID_COLS  # 10000

# Get a list of all .tif files
image_files = glob.glob(os.path.join(INPUT_DIR, '*.tif'))

for img_path in image_files:
    filename = os.path.basename(img_path)
    base_name = os.path.splitext(filename)[0]
    
    print(f"Opening: {filename}...")
    img = imread(img_path)
    
    # Get image dimensions
    img_h, img_w = img.shape[0], img.shape[1]
    
    # Safety check: Ensure the image is actually large enough
    if img_h < TOTAL_HEIGHT or img_w < TOTAL_WIDTH:
        print(f"  -> WARNING: {filename} ({img_h}x{img_w}) is smaller than the requested 10000x10000 crop area. Skipping.")
        continue

    # Find the exact center pixel
    center_y = img_h // 2
    center_x = img_w // 2
    
    # Calculate the top-left starting point of the 10000x10000 box
    start_y = center_y - (TOTAL_HEIGHT // 2)
    start_x = center_x - (TOTAL_WIDTH // 2)
    
    print(f"  -> Cropping 4x4 grid from center starting at Y:{start_y}, X:{start_x}")
    
    # Loop through the grid to create and save the 16 tiles
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            # Calculate pixel coordinates for this specific tile
            y1 = start_y + (row * TILE_SIZE)
            y2 = y1 + TILE_SIZE
            x1 = start_x + (col * TILE_SIZE)
            x2 = x1 + TILE_SIZE
            
            # Crop the tile
            tile = img[y1:y2, x1:x2]
            
            # Create a naming convention: OriginalName_Row-X_Col-Y.tif
            tile_name = f"{base_name}_R{row}_C{col}.tif"
            tile_path = os.path.join(OUTPUT_DIR, tile_name)
            
            # Save the tile safely
            imsave(tile_path, tile, check_contrast=False)
            
    print(f"  -> Saved 16 tiles for {filename}\n")

print("Tiling process complete!")