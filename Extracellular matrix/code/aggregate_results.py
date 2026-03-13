# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 17:35:28 2026

@author: pedro
"""

# aggregate_results.py
import os
import glob
import pandas as pd
import numpy as np

def calculate_sheet_statistics(df, prefix):
    """
    Extracts numerical columns from a DataFrame and calculates mean and standard deviation.
    Ignores identifier columns such as 'cell_ID' or 'number'.
    """
    stats = {}
    if df is None or df.empty:
        return stats
        
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        # Skip arbitrary ID columns as their statistical moments are biologically meaningless
        if col in ['cell_ID', 'number']:
            continue
            
        stats[f'{prefix}_{col}_mean'] = df[col].mean()
        stats[f'{prefix}_{col}_std'] = df[col].std()
        
    return stats

def compile_master_dataset(input_dir, output_filepath):
    """
    Aggregates all individual tile results into a single master Excel table.
    """
    search_pattern = os.path.join(input_dir, '*_results.xlsx')
    excel_files = glob.glob(search_pattern)
    
    if not excel_files:
        print(f"No result files found in {input_dir}. Please ensure the pipeline has finished running.")
        return

    print(f"Found {len(excel_files)} result files. Beginning aggregation...")
    
    master_data = []

    for file in excel_files:
        tile_name = os.path.basename(file).replace('_results.xlsx', '')
        tile_summary = {'Tile_Name': tile_name}
        
        try:
            # Load the entire workbook into memory once for efficiency
            xls = pd.ExcelFile(file)
            
            # 1. Extract Global Metrics (always present, exactly 1 row)
            if 'Global_Metrics' in xls.sheet_names:
                global_df = pd.read_excel(xls, sheet_name='Global_Metrics')
                if not global_df.empty:
                    # Drop the duplicate Tile_Name column from the sheet if it exists
                    global_dict = global_df.iloc[0].drop('Tile_Name', errors='ignore').to_dict()
                    tile_summary.update(global_dict)
            
            # 2. Extract and calculate Nuclei statistics
            if 'Nuclei_Data' in xls.sheet_names:
                nuclei_df = pd.read_excel(xls, sheet_name='Nuclei_Data')
                tile_summary.update(calculate_sheet_statistics(nuclei_df, prefix='Nuclei'))
                
            # 3. Extract and calculate Collagen geometry statistics
            if 'Coll_Geom' in xls.sheet_names:
                coll_df = pd.read_excel(xls, sheet_name='Coll_Geom')
                tile_summary.update(calculate_sheet_statistics(coll_df, prefix='Col'))
                
            # 4. Extract and calculate Fibronectin geometry statistics
            if 'Fibr_Geom' in xls.sheet_names:
                fibr_df = pd.read_excel(xls, sheet_name='Fibr_Geom')
                tile_summary.update(calculate_sheet_statistics(fibr_df, prefix='Fib'))
                
            master_data.append(tile_summary)
            print(f"Aggregated: {tile_name}")
            
        except Exception as e:
            print(f"Error reading {tile_name}: {str(e)}")

    # Convert the list of dictionaries into a master DataFrame
    print("\nStructuring final master dataset...")
    master_df = pd.DataFrame(master_data)
    
    # Reorder columns to ensure 'Tile_Name' is first, followed by Global Metrics
    cols = master_df.columns.tolist()
    if 'Tile_Name' in cols:
        cols.insert(0, cols.pop(cols.index('Tile_Name')))
        master_df = master_df[cols]

    # Export to Excel
    master_df.to_excel(output_filepath, index=False)
    print(f"\nSuccessfully saved master dataset to: {output_filepath}")
    print(f"Total tiles aggregated: {len(master_df)}")
    print(f"Total features calculated per tile: {len(master_df.columns) - 1}")

if __name__ == '__main__':
    # --- Directory Configuration ---
    RESULTS_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\microsa_results_tiles'
    MASTER_OUTPUT_FILE = r'F:\Lab\MAMDC2\Extracellular matrix\master_aggregated_results.xlsx'
    
    compile_master_dataset(RESULTS_DIR, MASTER_OUTPUT_FILE)