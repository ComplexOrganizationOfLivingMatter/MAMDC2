# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:43:45 2026
Optimized for performance, redundancy reduction, and smart step-skipping.
@author: pedro
"""

import os
import numpy as np
import pandas as pd
from skimage.io import imread
from skimage.filters import frangi
from skimage.measure import regionprops_table, label

# Import custom toolkits
import lib.ecm_utils as eu
from lib.microsaa.fibseg import fibers_executor

def process_single_tile(img_path, output_dir, dapi_mask_dir, recovery_mode=True):
    filename = os.path.basename(img_path)
    base_name = os.path.splitext(filename)[0]
    out_file = os.path.join(output_dir, f"{base_name}_results.xlsx")
    IMG_OUT = os.path.join(output_dir, f"{base_name}_debug_images")
    
    HALO_RADIUS = 75  # in pixels
    can_recover = False
    skip_interactions = False

    # --- STEP 0: EARLY EXIT & RECOVERY DETECTION ---
    if os.path.exists(out_file):
        try:
            with pd.ExcelFile(out_file) as xls:
                sheets = xls.sheet_names
            
            # 1. Ultimate Early Exit: If completely analyzed and recovery_mode isn't forced, skip entirely
            if 'Nuclei_Data' in sheets and 'Coll_Geom' in sheets and 'Fibr_Geom' in sheets and not recovery_mode:
                return f"[{filename}] Already completely finished. Skipping!"
            
            # 2. Check if the required generated debug masks exist on disk
            masks_exist = (os.path.exists(os.path.join(IMG_OUT, '0_Collagen_binary_mask.png')) and 
                           os.path.exists(os.path.join(IMG_OUT, '0_Fibronectin_binary_mask.png')) and
                           os.path.exists(os.path.join(IMG_OUT, '1_Collagen_pruned_labeled.png')) and
                           os.path.exists(os.path.join(IMG_OUT, '2_Fibronectin_pruned_labeled.png')))
            
            # 3. Determine recovery status
            if 'Coll_Geom' in sheets and 'Fibr_Geom' in sheets and masks_exist:
                can_recover = True
                
                # If Nuclei_Data already exists, we can skip the heavy spatial interaction calculations
                if 'Nuclei_Data' in sheets:
                    skip_interactions = True
                    print(f"[{filename}] Existing fiber AND interaction data found. Activating full cache skip!")
                else:
                    print(f"[{filename}] Fiber data found, but DAPI data is missing. Activating DAPI recovery mode...")
        except Exception:
            pass  # Fall back to full processing if Excel reading fails

    try:
        # --- STEP 1: READ IMAGE DATA ---
        print(f"[{filename}] Step 1/6: Reading image data...")
        img = imread(img_path)
        dapi_ch = img[:, :, 2]
        total_pixels = dapi_ch.size
        
        # Performance save: Skip empty tile checks and channel splits if we are recovering fiber masks anyway
        if not can_recover:
            collagen_ch = img[:, :, 0]    
            fibronectin_ch = img[:, :, 1] 
            if np.max(collagen_ch) < 15 and np.max(fibronectin_ch) < 15:
                return f"[{filename}] Skipped (Blank/Empty Tile)"

        # --- STEP 2: ANALYZE NUCLEI (DAPI MASK) ---
        dapi_mask = None
        
        if skip_interactions:
            print(f"[{filename}] Step 2/6: Loading cached nuclei properties from Excel...")
            nuclei_df = pd.read_excel(out_file, sheet_name='Nuclei_Data')
        else:
            print(f"[{filename}] Step 2/6: Analyzing DAPI mask and nuclei properties from disk...")
            dapi_mask_filename = f"{base_name}.tif" 
            actual_mask_path = os.path.join(dapi_mask_dir, dapi_mask_filename)
            nuclei_df = pd.DataFrame()
            
            if os.path.exists(actual_mask_path):
                dapi_mask = imread(actual_mask_path)
                if dapi_mask.dtype == bool or dapi_mask.max() == 1:
                    dapi_mask = label(dapi_mask)
                
                # Cross-version compatibility loop for skimage regionprops
                for prop_name in ['intensity_mean', 'mean_intensity']:
                    try:
                        props = regionprops_table(dapi_mask, intensity_image=dapi_ch,
                                                  properties=('label', 'centroid', 'area', 'eccentricity', prop_name, 'orientation'))
                        col_intensity = prop_name
                        break
                    except KeyError:
                        continue
                
                nuclei_df = pd.DataFrame(props).rename(columns={
                    'label': 'cell_ID', 
                    'centroid-0': 'centroid_y', 
                    'centroid-1': 'centroid_x', 
                    col_intensity: 'mean_DAPI_intensity'
                })
                
                if not nuclei_df.empty and 'orientation' in nuclei_df.columns:
                    nuclei_df['nucleus_angle'] = eu.convert_to_0_180_degrees(nuclei_df['orientation'])
                    mean_nuc_angle_rad = np.radians(nuclei_df['nucleus_angle'].dropna().mean())
                    nuclei_df['nucleus_alignment'] = np.cos(np.radians(nuclei_df['nucleus_angle']) - mean_nuc_angle_rad)**2
                    nuclei_df.drop(columns=['orientation'], inplace=True, errors='ignore')

        # --- STEP 3 & 4: ECM FIBER PROCESSING ---
        if can_recover:
            print(f"[{filename}] Step 3&4/6: Fast-loading fiber features and masks from cache...")
            col_geom_df = pd.read_excel(out_file, sheet_name='Coll_Geom')
            fib_geom_df = pd.read_excel(out_file, sheet_name='Fibr_Geom')
            
            # Clean old interaction columns ONLY if we are forced to recalculate them
            if not skip_interactions:
                drop_cols = lambda df: [c for c in df.columns if 'touching' in c or '_x' in c or '_y' in c]
                col_geom_df.drop(columns=drop_cols(col_geom_df), inplace=True, errors='ignore')
                fib_geom_df.drop(columns=drop_cols(fib_geom_df), inplace=True, errors='ignore')
            
            # Ultra-fast mask read bypasses frangi filter and fibers_executor completely
            col_bit = imread(os.path.join(IMG_OUT, '0_Collagen_binary_mask.png')) > 0
            fib_bit = imread(os.path.join(IMG_OUT, '0_Fibronectin_binary_mask.png')) > 0
            col_labeled = imread(os.path.join(IMG_OUT, '1_Collagen_pruned_labeled.png'))
            fib_labeled = imread(os.path.join(IMG_OUT, '2_Fibronectin_pruned_labeled.png'))
            
            collagen_area_density = np.sum(col_bit) / total_pixels
            fibronectin_area_density = np.sum(fib_bit) / total_pixels
            
        else:
            # Full processing pipeline for Collagen
            print(f"[{filename}] Step 3/6: Processing Collagen fibers from raw data...")
            col_frangi = np.array(frangi(collagen_ch, sigmas=range(4, 6, 10), gamma=25, black_ridges=False))
            col_bit = ((col_frangi / 255) > 0.000000001) 
            collagen_area_density = np.sum(col_bit) / total_pixels
            
            col_exe = fibers_executor(col_bit)
            col_labeled = col_exe['skel_labels_pruned']
            col_geom_df = eu.extract_microsa_geometry(col_labeled, col_bit, collagen_ch, neighborhood_radius=HALO_RADIUS)
            
            # Full processing pipeline for Fibronectin
            print(f"[{filename}] Step 4/6: Processing Fibronectin fibers from raw data...")
            fib_frangi = np.array(frangi(fibronectin_ch, sigmas=range(4, 6, 10), gamma=25, black_ridges=False))
            fib_bit = ((fib_frangi / 255) > 0.000000001)
            fibronectin_area_density = np.sum(fib_bit) / total_pixels
            
            fib_exe = fibers_executor(fib_bit)
            fib_labeled = fib_exe['skel_labels_pruned']
            fib_geom_df = eu.extract_microsa_geometry(fib_labeled, fib_bit, fibronectin_ch, neighborhood_radius=HALO_RADIUS)

        # --- STEP 5: CALCULATE INTERACTIONS ---
        if skip_interactions:
            print(f"[{filename}] Step 5/6: Bypassing spatial calculations (Using fully cached interaction metrics)...")
        else:
            print(f"[{filename}] Step 5/6: Calculating cell-ECM spatial interactions...")
            if dapi_mask is not None and np.max(dapi_mask) > 0:
                nuc_col_stats, col_geom_df = eu.calculate_interactions(dapi_mask, col_labeled, col_geom_df, prefix='Col', interaction_radius=HALO_RADIUS)
                nuclei_df = pd.merge(nuclei_df, nuc_col_stats, on='cell_ID', how='left')
                
                nuc_fib_stats, fib_geom_df = eu.calculate_interactions(dapi_mask, fib_labeled, fib_geom_df, prefix='Fib', interaction_radius=HALO_RADIUS)
                nuclei_df = pd.merge(nuclei_df, nuc_fib_stats, on='cell_ID', how='left')

        # --- STEP 6: EXPORT RESULTS ---
        print(f"[{filename}] Step 6/6: Exporting consolidated results to Excel...")
        global_metrics = pd.DataFrame([{
            'Tile_Name': filename,
            'Total_Nuclei_Count': len(nuclei_df),
            'Total_Collagen_Fibers': len(col_geom_df),
            'Total_Fibronectin_Fibers': len(fib_geom_df),
            'Collagen_Area_Density': collagen_area_density,
            'Fibronectin_Area_Density': fibronectin_area_density
        }])
            
        os.makedirs(IMG_OUT, exist_ok=True)
        eu.save_binary(os.path.join(IMG_OUT, '0_Collagen_binary_mask.png'), col_bit)
        eu.save_binary(os.path.join(IMG_OUT, '0_Fibronectin_binary_mask.png'), fib_bit)
        eu.save_labeled(os.path.join(IMG_OUT, '1_Collagen_pruned_labeled.png'), col_labeled)
        eu.save_labeled(os.path.join(IMG_OUT, '2_Fibronectin_pruned_labeled.png'), fib_labeled)

        with pd.ExcelWriter(out_file) as writer:
            if not nuclei_df.empty:
                nuclei_df.to_excel(writer, sheet_name='Nuclei_Data', index=False)
            global_metrics.to_excel(writer, sheet_name='Global_Metrics', index=False)
            if not col_geom_df.empty:
                col_geom_df.to_excel(writer, sheet_name='Coll_Geom', index=False)
            if not fib_geom_df.empty:
                fib_geom_df.to_excel(writer, sheet_name='Fibr_Geom', index=False)

        return f"[{filename}] Successfully processed!"
        
    except Exception as e:
        return f"[{filename}] Error during processing: {str(e)}"