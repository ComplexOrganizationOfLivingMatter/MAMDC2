# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 11:03:26 2026

@author: Pedro Gomez Galvez
"""

import os
import glob
import numpy as np
import pandas as pd
import concurrent.futures

# Image processing libraries
from skimage.io import imread, imsave
from skimage.filters import frangi
from skimage.color import label2rgb
from skimage.measure import regionprops_table

# Microsa functions
from microsaa import fibers_executor, fibs_geom, fibs_spatial

# Helper functions to save images safely
def save_binary(path, img_bool):
    imsave(path, (img_bool * 255).astype(np.uint8), check_contrast=False)

def save_labeled(path, labeled_img):
    rgb = label2rgb(labeled_img, bg_label=0) 
    imsave(path, (rgb * 255).astype(np.uint8), check_contrast=False)

# --- Worker Function ---
# This function handles exactly ONE tile. The CPU will run many of these at once.
def process_single_tile(img_path, output_dir, dapi_mask_dir):
    filename = os.path.basename(img_path)
    base_name = os.path.splitext(filename)[0]
    
    # Define the final output file path immediately
    out_file = os.path.join(output_dir, f"{base_name}_results.xlsx")
    
    neighborhood_radius = 75 ## nuclei diameter ~100 pixels, in that way would explore 150 pixels from the centroid
    
    # ==========================================
    # "RESUME" CHECKPOINT
    # ==========================================
    if os.path.exists(out_file):
        return f"Already finished {filename}. Skipping!"    
    try:
        # 1. Read the RGB image (Matrix channels)
        img = imread(img_path)
        collagen_ch = img[:, :, 0]    
        fibronectin_ch = img[:, :, 1] 
        dapi_ch = img[:, :, 2]
        
        # Calculate total pixels for global density metrics
        total_pixels = img.shape[0] * img.shape[1]
        
        # --- BLANK TILE CHECK ---
        if np.max(collagen_ch) < 15 and np.max(fibronectin_ch) < 15:
            return f"Skipped {filename} (Blank/Empty Tile)"

        # 2. Load Segmented Nuclei        
        # Build the exact filename by adding "_mask.tif" to the base name
        dapi_mask_filename = f"{base_name}_mask.tif"
        actual_mask_path = os.path.join(dapi_mask_dir, dapi_mask_filename)
        
        cells_coords = []
        nuclei_df = pd.DataFrame()
        
        if os.path.exists(actual_mask_path):
            dapi_mask = imread(actual_mask_path)
            
            # Safety check: if the mask is purely boolean (True/False or 0/1), label it.
            # This ensures the computer counts individual cells (1, 2, 3...) instead of one giant mass.
            if dapi_mask.dtype == bool or dapi_mask.max() == 1:
                from skimage.measure import label
                dapi_mask = label(dapi_mask)
            
            # Extract region properties (Compatible with both old and new scikit-image versions)
            try:
                # Try with the NEW version property name ('intensity_mean')
                props = regionprops_table(
                    dapi_mask, 
                    intensity_image=dapi_ch,
                    properties=('label', 'centroid', 'area', 'eccentricity', 'intensity_mean')
                )
                col_intensity = 'intensity_mean'
            except KeyError:
                # If it throws a KeyError, fall back to the OLD version property name ('mean_intensity')
                props = regionprops_table(
                    dapi_mask, 
                    intensity_image=dapi_ch,
                    properties=('label', 'centroid', 'area', 'eccentricity', 'mean_intensity')
                )
                col_intensity = 'mean_intensity'
            
            nuclei_df = pd.DataFrame(props)
            
            # Rename columns dynamically to match your exact requests
            nuclei_df.rename(columns={
                'label': 'cell_ID', 
                'centroid-0': 'centroid_y', 
                'centroid-1': 'centroid_x', 
                col_intensity: 'mean_DAPI_intensity'
            }, inplace=True)
            
            # Format coordinates for Microsa spatial mapping: [(Y1, X1), (Y2, X2)...]
            #if not nuclei_df.empty:
            #    cells_coords = list(zip(nuclei_df['centroid_y'], nuclei_df['centroid_x']))
                
                
            # Format coordinates for Microsa (exchanged to X, Y!)
            if not nuclei_df.empty:
                cells_coords = list(zip(nuclei_df['centroid_x'], nuclei_df['centroid_y']))
        else:
            print(f"⚠️ WARNING: Mask file not found: {dapi_mask_filename}")
            
        
        # 3. Analyze Collagen (Red)
        col_frangi = np.array(frangi(collagen_ch, sigmas=range(4, 6, 10), gamma=25, black_ridges=False))
        col_bit = ((col_frangi / 255) > 0.000000001) 
        col_exe = fibers_executor(col_bit)
        col_geom = fibs_geom(collagen_ch, col_exe, neighborhood_radius)
        
        if cells_coords:
            col_spat = fibs_spatial(cells_coords, col_exe, neighborhood_radius, cell_type='All', cell_type_list=[])
        else:
            col_spat = pd.DataFrame() 
            
        # 4. Analyze Fibronectin (Green)
        fib_frangi = np.array(frangi(fibronectin_ch, sigmas=range(4, 6, 10), gamma=25, black_ridges=False))
        fib_bit = ((fib_frangi / 255) > 0.000000001)
        fib_exe = fibers_executor(fib_bit)
        fib_geom = fibs_geom(fibronectin_ch, fib_exe, neighborhood_radius)
        
        if cells_coords:
            fib_spat = fibs_spatial(cells_coords, fib_exe, neighborhood_radius, cell_type='All', cell_type_list=[])
        else:
            fib_spat = pd.DataFrame()
            
        # 5. Calculate Global Metrics
        nuclei_count = len(nuclei_df)
        global_metrics = pd.DataFrame([{
            'Tile_Name': filename,
            'Total_Image_Area_px': total_pixels,
            'Total_Nuclei_Count': nuclei_count,
            'Nuclei_Density': nuclei_count / total_pixels,
            'Collagen_Global_Density': np.sum(col_bit) / total_pixels,
            'Fibronectin_Global_Density': np.sum(fib_bit) / total_pixels
        }])
            
        # --- SAVE INTERMEDIATE IMAGES ---
        IMG_OUT = os.path.join(output_dir, f"{base_name}_debug_images")
        os.makedirs(IMG_OUT, exist_ok=True)
        
        save_binary(os.path.join(IMG_OUT, '1_Collagen_segmentation.png'), col_bit)
        save_binary(os.path.join(IMG_OUT, '1_Collagen_skeleton.png'), col_exe['skeleton'])
        save_labeled(os.path.join(IMG_OUT, '1_Collagen_pruned_labeled.png'), col_exe['skel_labels_pruned'])

        save_binary(os.path.join(IMG_OUT, '2_Fibronectin_segmentation.png'), fib_bit)
        save_binary(os.path.join(IMG_OUT, '2_Fibronectin_skeleton.png'), fib_exe['skeleton'])
        save_labeled(os.path.join(IMG_OUT, '2_Fibronectin_pruned_labeled.png'), fib_exe['skel_labels_pruned'])

        # --- SAVE RESULTS TO EXCEL ---
        with pd.ExcelWriter(out_file) as writer:
            # New Nuclei and Global Data
            if not nuclei_df.empty:
                nuclei_df.to_excel(writer, sheet_name='Nuclei_Data', index=False)
            global_metrics.to_excel(writer, sheet_name='Global_Metrics', index=False)
            
            # Microsa Data
            col_geom.to_excel(writer, sheet_name='Coll_Geom', index=False)
            if not col_spat.empty:
                col_spat.to_excel(writer, sheet_name='Coll_Spatial', index=False)
                
            fib_geom.to_excel(writer, sheet_name='Fibr_Geom', index=False)
            if not fib_spat.empty:
                fib_spat.to_excel(writer, sheet_name='Fibr_Spatial', index=False)

        return f"Successfully processed: {filename} (Found {nuclei_count} nuclei)"
        
    except Exception as e:
        return f"Error processing {filename}: {str(e)}"

# ==========================================
# MAIN EXECUTION BLOCK 
# ==========================================
if __name__ == '__main__':
    # --- Configuration ---
    INPUT_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\tiled_images'
    OUTPUT_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\microsa_results_tiles'
    
    # New DAPI directories
    DAPI_MASK_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\DAPI\segmentation_filtered'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    image_files = glob.glob(os.path.join(INPUT_DIR, '*.tif'))
    print(f"Found {len(image_files)} tiles. Starting multiprocessing pool...")
    
    # Using 20 workers to harness your Threadripper while leaving system resources free
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
        # Submit all tasks to the pool with the new directory arguments
        futures = {
            executor.submit(process_single_tile, img_path, OUTPUT_DIR, DAPI_MASK_DIR): img_path 
            for img_path in image_files
        }
        
        # As each tile finishes, print its result
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(result)
            
    print("\nAll processing complete!")