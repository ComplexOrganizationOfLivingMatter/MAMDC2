# -*- coding: utf-8 -*-
"""
Adapted on Wed Mar 11 2026

@author: Pedro Gomez Galvez
"""

import os
import glob
import re
import pandas as pd

# --- Configuration ---
# Point this to where your tile results are saved
INPUT_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\microsa_results_tiles'
# Where you want the master spreadsheets saved
OUTPUT_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\microsa_master_results'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 1. Find all the individual result files
excel_files = glob.glob(os.path.join(INPUT_DIR, '*_results.xlsx'))
print(f"Found {len(excel_files)} individual tile results.")

# 2. Group the files by their original image name
file_groups = {}
for file_path in excel_files:
    filename = os.path.basename(file_path)
    
    # Extract the tile coordinates (e.g., _R0_C0) and the original image name
    match = re.search(r'(_R\d+_C\d+)_results\.xlsx$', filename)
    if match:
        tile_id = match.group(1) 
        original_name = re.sub(r'_R\d+_C\d+_results\.xlsx$', '', filename)
        
        if original_name not in file_groups:
            file_groups[original_name] = []
        
        file_groups[original_name].append({
            'path': file_path,
            'tile': tile_id.strip('_') # Cleans it up to "R0_C0"
        })

print(f"Grouped into {len(file_groups)} original images.\n")

# 3. Process each group and merge the sheets
for original_name, tiles in file_groups.items():
    print(f"Merging data for: {original_name}...")
    
    # Dictionaries to hold the combined dataframes for EVERY sheet type, 
    # PLUS the new ultimate master sheet
    master_data = {
        'Global_Metrics': [],
        'Nuclei_Data': [],
        'Coll_Geom': [],
        'Coll_Spatial': [],
        'Fibr_Geom': [],
        'Fibr_Spatial': [],
        'Single_Cell_Master': []  # <-- The new side-by-side integration!
    }
    
    # Open each tile's Excel file and scoop out the data
    for tile_info in tiles:
        try:
            # Read all sheets at once into a dictionary of DataFrames
            xls_dict = pd.read_excel(tile_info['path'], sheet_name=None)
            
            # --- STEP A: Stack individual sheets vertically ---
            for sheet_name, df in xls_dict.items():
                if sheet_name in master_data and not df.empty:
                    df = df.copy()
                    df.insert(0, 'Tile_ID', tile_info['tile'])
                    master_data[sheet_name].append(df)
            
            # --- STEP B: Build the Single-Cell Side-by-Side Table ---
            # If the tile has nuclei, we can map the matrix to them
            if 'Nuclei_Data' in xls_dict and not xls_dict['Nuclei_Data'].empty:
                nuc_df = xls_dict['Nuclei_Data'].copy()
                
                # Safely grab Collagen spatial data and add prefixes
                col_df = xls_dict.get('Coll_Spatial', pd.DataFrame())
                if not col_df.empty:
                    col_df = col_df.copy()
                    col_df.columns = [f"Coll_{c}" for c in col_df.columns]
                    
                # Safely grab Fibronectin spatial data and add prefixes
                fib_df = xls_dict.get('Fibr_Spatial', pd.DataFrame())
                if not fib_df.empty:
                    fib_df = fib_df.copy()
                    fib_df.columns = [f"Fibr_{c}" for c in fib_df.columns]
                
                # Merge them side-by-side (axis=1) because rows match exactly
                merged_cells = pd.concat([nuc_df, col_df, fib_df], axis=1)
                
                # Add our tracking column
                merged_cells.insert(0, 'Tile_ID', tile_info['tile'])
                
                # Add it to the master list
                master_data['Single_Cell_Master'].append(merged_cells)
                        
        except Exception as e:
            print(f"  -> Error reading {tile_info['tile']}: {e}")

    # 4. Save the combined data into a Master Excel file
    out_file = os.path.join(OUTPUT_DIR, f"{original_name}_MASTER.xlsx")
    
    with pd.ExcelWriter(out_file) as writer:
        for sheet_name, df_list in master_data.items():
            if df_list: # Only create the sheet if we actually have data for it
                # Concatenate all the dataframes vertically
                combined_df = pd.concat(df_list, ignore_index=True)
                combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
    print(f"  -> Saved master file for {original_name}!\n")

print("All merging is complete!")