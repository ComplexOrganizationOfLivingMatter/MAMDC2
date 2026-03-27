# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:03:04 2026

@author: pedro
"""

import os
import glob
from skimage.io import imread, imsave
from skimage.segmentation import clear_border
from skimage.morphology import remove_small_objects

# --- 1. Define paths ---
# Use 'r' before quotes so Windows reads backslashes (\) correctly
SEG_DIR = r"F:\Lab\MAMDC2\Extracellular matrix\DAPI\segmentation"
OUT_DIR = r"F:\Lab\MAMDC2\Extracellular matrix\DAPI\segmentation_filtered"

# Create the output folder if it doesn't exist
os.makedirs(OUT_DIR, exist_ok=True)

# Find all mask images (assuming .tif, change here if they are .png)
mask_files = glob.glob(os.path.join(SEG_DIR, "*.tif"))
print(f"Found {len(mask_files)} masks to process.\n")

# --- 2. Process each image ---
for filepath in mask_files:
    filename = os.path.basename(filepath)
    print(f"Filtering: {filename}...")
    
    # Read the original Cellpose mask
    mask = imread(filepath)
    
    # Step A: Remove nuclei touching the image borders
    mask_cleared = clear_border(mask)
    
    # Step B: Remove nuclei with an area smaller than 1300 pixels
    # This function preserves the original Cellpose label IDs
    mask_filtered = remove_small_objects(mask_cleared, min_size=1300)
    
    # --- 3. Save the filtered mask ---
    out_path = os.path.join(OUT_DIR, filename)
    # check_contrast=False prevents annoying warnings when saving dark label images
    imsave(out_path, mask_filtered, check_contrast=False)

print("\nFiltering completed successfully! All images are in 'segmentation_filtered'.")