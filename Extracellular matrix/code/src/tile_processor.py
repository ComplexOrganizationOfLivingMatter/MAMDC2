# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:43:45 2026

@author: pedro
"""

# tile_processor.py
import os
import numpy as np
import pandas as pd
from skimage.io import imread
from skimage.filters import frangi
from skimage.measure import regionprops_table, label

# Import custom toolkits and microsa
import lib.ecm_utils as eu
from microsaa import fibers_executor

def process_single_tile(img_path, output_dir, dapi_mask_dir):
    filename = os.path.basename(img_path)
    base_name = os.path.splitext(filename)[0]
    out_file = os.path.join(output_dir, f"{base_name}_results.xlsx")
    
    HALO_RADIUS = 75 # in pixels [~50 pixels is a nucleus radius in our images]
    
    if os.path.exists(out_file):
        return f"[{filename}] Already finished. Skipping!"    
        
    try:
        # 1. Read Image
        print(f"[{filename}] Step 1/6: Reading image data...")
        img = imread(img_path)
        collagen_ch = img[:, :, 0]    
        fibronectin_ch = img[:, :, 1] 
        dapi_ch = img[:, :, 2]
        
        if np.max(collagen_ch) < 15 and np.max(fibronectin_ch) < 15:
            return f"[{filename}] Skipped (Blank/Empty Tile)"

        # 2. Analyze Nuclei
        print(f"[{filename}] Step 2/6: Analyzing DAPI mask and nuclei properties...")
        dapi_mask_filename = f"{base_name}_mask.tif"
        actual_mask_path = os.path.join(dapi_mask_dir, dapi_mask_filename)
        nuclei_df = pd.DataFrame()
        dapi_mask = None
        
        if os.path.exists(actual_mask_path):
            dapi_mask = imread(actual_mask_path)
            if dapi_mask.dtype == bool or dapi_mask.max() == 1:
                dapi_mask = label(dapi_mask)
            
            try:
                props = regionprops_table(dapi_mask, intensity_image=dapi_ch,
                                          properties=('label', 'centroid', 'area', 'eccentricity', 'intensity_mean', 'orientation'))
                col_intensity = 'intensity_mean'
            except KeyError:
                props = regionprops_table(dapi_mask, intensity_image=dapi_ch,
                                          properties=('label', 'centroid', 'area', 'eccentricity', 'mean_intensity', 'orientation'))
                col_intensity = 'mean_intensity'
            
            nuclei_df = pd.DataFrame(props)
            nuclei_df.rename(columns={
                'label': 'cell_ID', 
                'centroid-0': 'centroid_y', 
                'centroid-1': 'centroid_x', 
                col_intensity: 'mean_DAPI_intensity'
            }, inplace=True)
            
            if not nuclei_df.empty:
                if 'orientation' in nuclei_df.columns:
                    nuclei_df['nucleus_angle'] = eu.convert_to_0_180_degrees(nuclei_df['orientation'])
                else:
                    nuclei_df['nucleus_angle'] = np.nan
                
                if 'nucleus_angle' in nuclei_df.columns:
                    mean_nuc_angle_rad = np.radians(nuclei_df['nucleus_angle'].dropna().mean())
                    nuclei_df['nucleus_alignment'] = np.cos(np.radians(nuclei_df['nucleus_angle']) - mean_nuc_angle_rad)**2
                    
            nuclei_df.drop(columns=['orientation'], inplace=True, errors='ignore')
            
        # 3. Analyze Collagen 
        print(f"[{filename}] Step 3/6: Processing Collagen fibers and geometry...")
        total_pixels = collagen_ch.size
        
        col_frangi = np.array(frangi(collagen_ch, sigmas=range(4, 6, 10), gamma=25, black_ridges=False))
        col_bit = ((col_frangi / 255) > 0.000000001) 
        
        collagen_area_density = np.sum(col_bit) / total_pixels
        col_exe = fibers_executor(col_bit)
        col_labeled = col_exe['skel_labels_pruned']
        
        col_geom_df = eu.extract_microsa_geometry(col_labeled, col_bit, collagen_ch, neighborhood_radius=HALO_RADIUS)
        
        # 4. Analyze Fibronectin 
        print(f"[{filename}] Step 4/6: Processing Fibronectin fibers and geometry...")
        fib_frangi = np.array(frangi(fibronectin_ch, sigmas=range(4, 6, 10), gamma=25, black_ridges=False))
        fib_bit = ((fib_frangi / 255) > 0.000000001)
        
        fibronectin_area_density = np.sum(fib_bit) / total_pixels
        fib_exe = fibers_executor(fib_bit)
        fib_labeled = fib_exe['skel_labels_pruned']
        
        fib_geom_df = eu.extract_microsa_geometry(fib_labeled, fib_bit, fibronectin_ch, neighborhood_radius=HALO_RADIUS)
        
        # 5. Calculate Interactions
        print(f"[{filename}] Step 5/6: Calculating cell-ECM spatial interactions...")
        if dapi_mask is not None and np.max(dapi_mask) > 0:
            nuc_col_stats, col_geom_df = eu.calculate_interactions(dapi_mask, col_labeled, col_geom_df, prefix='Col', interaction_radius=HALO_RADIUS)
            nuclei_df = pd.merge(nuclei_df, nuc_col_stats, on='cell_ID', how='left')
            
            nuc_fib_stats, fib_geom_df = eu.calculate_interactions(dapi_mask, fib_labeled, fib_geom_df, prefix='Fib', interaction_radius=HALO_RADIUS)
            nuclei_df = pd.merge(nuclei_df, nuc_fib_stats, on='cell_ID', how='left')

        # 6. Export Results
        print(f"[{filename}] Step 6/6: Exporting results to Excel and saving debug images...")
        global_metrics = pd.DataFrame([{
            'Tile_Name': filename,
            'Total_Nuclei_Count': len(nuclei_df),
            'Total_Collagen_Fibers': len(col_geom_df),
            'Total_Fibronectin_Fibers': len(fib_geom_df),
            'Collagen_Area_Density': collagen_area_density,
            'Fibronectin_Area_Density': fibronectin_area_density
        }])
            
        IMG_OUT = os.path.join(output_dir, f"{base_name}_debug_images")
        os.makedirs(IMG_OUT, exist_ok=True)
        
        # --- RESTORED INTERMEDIATE IMAGES ---
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