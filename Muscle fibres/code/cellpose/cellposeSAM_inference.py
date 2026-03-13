import os
import glob
import numpy as np
import tifffile
from pathlib import Path
import matplotlib.pyplot as plt
from tqdm import trange
from cellpose import models, core, io

# ----------------------------
# Setup
# ----------------------------

# Print Cellpose logs
io.logger_setup()

# Ensure GPU is available
if not core.use_gpu():
    raise RuntimeError("No GPU access detected. Check your environment or install CUDA properly.")

# Initialize Cellpose model (this uses SAM if installed via cellpose-sam)
model = models.CellposeModel(gpu=True)

# ----------------------------
# Paths
# ----------------------------

input_dir = "F:/Lab/MAMDC2/raw images/tifs/rawNucleiProjection05/"  # <-- CHANGE THIS
output_dir = os.path.join(input_dir, "masks")
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Process all .tif files
# ----------------------------

image_paths = glob.glob(os.path.join(input_dir, "*.tif"))
print(f"Found {len(image_paths)} images in {input_dir}")

for img_path in image_paths:
    # Load image
    img_2D = io.imread(img_path)

    # Run Cellpose
    masks, flows, styles = model.eval(img_2D, 
                                       diameter=None,    # or set a fixed value if known
                                       niter=1000, 
                                       channels=[0,0],    # set channels appropriately
                                       progress=True)

    # Save mask
    base = os.path.basename(img_path)
    name = os.path.splitext(base)[0]
    mask_path = os.path.join(output_dir, f"{name}_mask.tif")
    tifffile.imwrite(mask_path, masks.astype(np.uint16))
    print(f"Saved mask: {mask_path}")
