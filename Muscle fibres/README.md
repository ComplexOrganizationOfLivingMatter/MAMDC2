# MAMDC2 myotubes culturing analysis. Myotubes features extraction pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Matlab](https://img.shields.io/badge/MATLAB-R2023b+-blue.svg)](https://www.mathworks.com/products/matlab.html)
[![BiaPy](https://img.shields.io/badge/BiaPy-DeepLearning-green.svg)](https://biapy.readthedocs.io/)

This repository provides a complete, step-by-step pipeline for myofibre analysis, from raw microscopy data preparation to high-content morphological feature extraction.

## 🔗 Project Resources

**Contents include:**
* **Custom Fiji Scripts:** For data preparation, preprocessing and preliminary segmentation.
* **BiaPy Training:** `.yaml` configuration files and trained ResU-Net weights.
* **Nuclei Inference:** Python and Bash code for Cellpose-SAM application.
* **Morphological Extraction:** MATLAB R2023b scripts for features extraction.

---

## 🛠 Step-by-Step Pipeline [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Matlab](https://img.shields.io/badge/MATLAB-R2023b+-blue.svg)](https://www.mathworks.com/products/matlab.html)
[![BiaPy](https://img.shields.io/badge/BiaPy-DeepLearning-green.svg)](https://biapy.readthedocs.io/)

This repository provides a complete, step-by-step pipeline for myofibre analysis, from raw microscopy data preparation to high-content morphological feature extraction.

## 🔗 Project Resources
All assets for this project are hosted at:  
👉 **[MAMDC2 - Muscle Fibres Repository](https://github.com/ComplexOrganizationOfLivingMatter/MAMDC2/tree/main/Muscle%20fibres)**

**Contents include:**
* **Custom Fiji Scripts:** For preprocessing and annotation data prep.
* **BiaPy Training:** `.yaml` configuration files and trained ResU-Net weights.
* **Nuclei Inference:** Python for Cellpose-SAM execution.
* **Morphological Extraction:** The MATLAB R2023b post-processing suite.

---

## 🛠 Step-by-Step Pipeline Workflow

### Phase 1: Preprocessing & Annotation
* **Data Prep:** Custom Fiji scripts to prepare raw microscopy stacks for annotation. Image cropping and preliminary segmentation.

* **Annotation:** Preliminary segmentation were manually refined in  [Napari](https://napari.org/stable/getting_started/installation.html#napari-installation) to generate ground truth datasets for DL-based segmentation. 

### Phase 2.1: Training of semantic segmentation model and inference of myotubes (BiaPy)
* [Biapy installation](https://biapy.readthedocs.io/en/latest/get_started/installation.html)
* **Configuration:** Use the provided `.yaml` files in the `/biapy` folder to replicate the configuration and hyperparameters.
* **Weights:** Pre-trained model weights are provided for direct inference on similar myotube datasets.

### Phase 2.2: Inference of nuclei through Cellpose-SAM pretrained model
* [Cellpose-SAM installation](https://github.com/mouseland/cellpose) 
* Python script to run default inference.

### Phase 3: Post-Processing & Feature Extraction (MATLAB)
Once inference is complete, the MATLAB pipeline handles the biological quantification:
1. **Refinement:** Binarization and morphological cleaning.
2. **Skeletonization:** Conversion of fibres to medial axes for length and branching analysis.
3. **Diameter Mapping:** Sampling the Euclidean Distance Transform at equidistant skeleton points to ensure non-biased width measurement.
4. **Nuclei Integration:** Calculating the **Myogenic Fusion Index** and clustering nuclei based on spatial proximity.

---



🚀 Getting Started
Prerequisites
MATLAB (Tested on R2023b or later)

Python 3.x (For Cellpose-SAM inference)
Fiji/ImageJ (For pre-processing scripts)




