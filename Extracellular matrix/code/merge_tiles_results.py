# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 13:18:37 2026

@author: Pedro Gomez Galvez
"""

import os
import glob
import re
import pandas as pd

# --- Configuration ---
# Point this to where your 96 tile results are saved
INPUT_DIR = 'F:/Lab/MAMDC2/Extracellular matrix/microsa_results_tiles'
# Where you want the 6 master spreadsheets saved
OUTPUT_DIR = 'F:/Lab/MAMDC2/Extracellular matrix/microsa_master_results'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 1. Find all the individual result files
excel_files = glob.glob(os.path.join(INPUT_DIR, '*_results.xlsx'))
print(f"Found {len(excel_files)} individual tile results.")

# 2. Group the files by their original image name
file_groups = {}
for file_path in excel_files:
    filename = os.path.basename(file_path)
    
    # We use regex to safely chop off the "_RX_CY_results.xlsx" tail 
    # This leaves us with the exact original image name
    match = re.search(r'(_R\d+_C\d+)_results\.xlsx$', filename)
    if match:
        tile_id = match.group(1) # Extracts exactly "_R0_C0", etc.
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
    
    # Dictionaries to hold the combined dataframes for each sheet type
    master_data = {
        'Coll_Geom': [],
        'Coll_Spatial': [],
        'Fibr_Geom': [],
        'Fibr_Spatial': []
    }
    
    # Open each tile's Excel file and scoop out the data
    for tile_info in tiles:
        try:
            # Read all sheets from the Excel file
            xls = pd.ExcelFile(tile_info['path'])
            
            for sheet_name in xls.sheet_names:
                if sheet_name in master_data:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    
                    # Add our tracking column at the very beginning
                    if not df.empty:
                        df.insert(0, 'Tile_ID', tile_info['tile'])
                        master_data[sheet_name].append(df)
                        
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
                
    print(f"  -> Saved master file!\n")

print("All merging is complete!")