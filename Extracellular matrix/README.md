# MAMDC2: Spatial ECM & Cell Orientation Pipeline

> **A high-throughput, multiprocessing Python pipeline for extracting topological geometry and spatial interactions between cells and the Extracellular Matrix (ECM).**

Designed for multiplexed immunofluorescence images, this tool mathematically replicates established metrics (like Microsa) to provide rigorous, publication-ready quantification of tissue anisotropy, fiber straightness, and cell-matrix contact guidance.

---

## 🔬 Core Capabilities

* **Microsa-Equivalent Geometry:** Calculates precise fiber straightness using the Chebyshev distance between lexicographically sorted endpoints, and true thickness via normalized Euclidean distance transforms.
* **Global Tissue Anisotropy:** Computes alignment scores for individual ECM fibers and cell nuclei based on the global mean angular field: Alignment = cos²(θ - θ_mean).
* **Spatial Interaction Mapping:** Utilizes highly optimized `Scipy cKDTree` spatial querying to identify local cell-ECM touching events within defined neighborhood radii.
* **High-Performance Batch Processing:** Built for modern high-core-count CPUs (e.g., AMD Threadripper), utilizing parallel processing with safe memory isolation to handle massive tiled datasets without RAM bottlenecking.

---

## 📁 Repository Structure

* **`main.py`**: The core orchestrator. Manages directory configuration and deploys the multiprocessing pool to feed image tiles into the processor concurrently.
* **`tile_processor.py`**: The single-image engine. Manages channel separation, Frangi filtering, and sequentially executes mathematical analysis for DAPI, Collagen, and Fibronectin. Exports intermediate diagnostic images and raw tile data.
* **`ecm_utils.py`**: The mathematical toolkit. Contains all strict geometric and topological algorithms, cKDTree interaction mapping, and Microsa-replicated feature extraction logic.
* **`aggregate_results.py`**: The final compilation script. Automatically parses the output directory, calculates the mean and standard deviation for all features, and outputs a single `master_aggregated_results.xlsx` ready for statistical analysis.

---

## 📊 Extracted Metrics

For every processed tile, the pipeline calculates both individual object data and aggregated tile metrics:

* **Geometry:** Length, Angle, Straightness (Chebyshev/Area), Thickness (Distance Transform).
* **Alignment:** Global tissue anisotropy score (0.0 to 1.0) for Collagen, Fibronectin, and Nuclei.
* **Interactions:** Number of neighboring fibers, touching nuclei per fiber, and average geometry of fibers touching specific cells.
* **Global Overviews:** Total fiber counts, cell counts, and ECM area density per tile.

---

## 🚀 Getting Started

### 1. Requirements
Ensure you have the required Python libraries installed:

```bash
pip install numpy pandas scikit-image scipy openpyxl
```

### 2. Directory Setup
Organize your tiled .tif images (multichannel) and DAPI segmentation masks into dedicated folders. Open main.py and update the paths to match your local file system:

```
INPUT_DIR = r'Path\to\tiled_images'
OUTPUT_DIR = r'Path\to\output_results'
DAPI_MASK_DIR = r'Path\to\dapi_masks' 
```

### 3. Run Processing
Execute the main script. The system will automatically detect available tiles and process them using your configured CPU workers.

```bash
python main.py
```

Note: Diagnostic intermediate images (binary masks, labeled skeletons) will be saved in a subfolder for each tile within the output directory so you can verify segmentation quality.

### 4. Aggregate Data
Once main.py finishes, configure the target paths in aggregate_results.py and run it to generate your final statistical dataset:

```bash
python aggregate_results.py
```