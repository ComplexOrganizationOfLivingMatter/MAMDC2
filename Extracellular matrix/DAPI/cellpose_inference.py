import os
import glob
import numpy as np
import tifffile
import argparse
from cellpose import models, io, core

def run_cellpose_on_folder(input_dir, output_subdir="masks", gpu=True, diameter=None):
    print("\n[INFO] Starting Cellpose segmentation...")
    print(f"[INFO] Input directory: {input_dir}")
    print(f"[INFO] Output subdirectory: {output_subdir}")
    print(f"[INFO] GPU requested: {gpu}")
    print(f"[INFO] Diameter: {diameter if diameter else 'Auto'}\n")

    io.logger_setup()
    if gpu and not core.use_gpu():
        print("✗ GPU requested but not available.")
        raise RuntimeError("GPU requested but not available.")

    model = models.CellposeModel(gpu=gpu)
    output_dir = os.path.join(input_dir, output_subdir)
    os.makedirs(output_dir, exist_ok=True)

    image_paths = glob.glob(os.path.join(input_dir, "*.tif"))
    if not image_paths:
        print("[WARNING] No .tif images found.")
        return

    for i, img_path in enumerate(image_paths, 1):
        try:
            name = os.path.splitext(os.path.basename(img_path))[0]
            print(f"[{i}/{len(image_paths)}] Processing: {name}")
            img = io.imread(img_path)
            masks, _, _ = model.eval(img, diameter=diameter)
            tifffile.imwrite(os.path.join(output_dir, f"{name}_mask.tif"), masks.astype(np.uint16))
        except Exception as e:
            print(f"✗ ERROR processing {img_path}: {e}")

    print("\n[INFO] Finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="Folder with .tif images")
    parser.add_argument("--diameter", type=float, default=None, help="Cell diameter (optional)")
    args = parser.parse_args()

    run_cellpose_on_folder(args.input_dir, gpu=True, diameter=args.diameter)
