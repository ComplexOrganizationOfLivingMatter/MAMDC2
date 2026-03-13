# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:44:18 2026

@author: pedro
"""

# main.py
import os
import glob
import multiprocessing
import concurrent.futures

# Import the individual tile processor
from tile_processor import process_single_tile

if __name__ == '__main__':
    # Required for safe execution of multiprocessing in Windows environments
    multiprocessing.freeze_support()
    
    # Enforces the 'spawn' start method to ensure clean memory states between subprocesses
    multiprocessing.set_start_method('spawn', force=True)

    # --- Directory Configuration ---
    INPUT_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\tiled_images'
    OUTPUT_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\microsa_results_tiles'
    DAPI_MASK_DIR = r'F:\Lab\MAMDC2\Extracellular matrix\DAPI\segmentation_filtered'

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    image_files = glob.glob(os.path.join(INPUT_DIR, '*.tif'))
    print(f"Discovered {len(image_files)} tiles for processing.")
    print("Initializing optimized multiprocessing engine...")
    
    # Initialize ProcessPoolExecutor. 
    # 20 workers is highly efficient for high-core count CPUs (e.g., Threadripper) 
    # provided there is sufficient RAM to handle concurrent distance transforms.
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
        # Map each image tile to an independent process
        futures = {
            executor.submit(process_single_tile, img_path, OUTPUT_DIR, DAPI_MASK_DIR): img_path 
            for img_path in image_files
        }
        
        # Yield results dynamically as independent processes complete
        for future in concurrent.futures.as_completed(futures):
            img_path = futures[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                # Catch and log critical errors (e.g., memory limits) without halting the entire pipeline
                print(f"Critical error processing {os.path.basename(img_path)}: {exc}")
            
    print("\nBatch processing completed successfully!")