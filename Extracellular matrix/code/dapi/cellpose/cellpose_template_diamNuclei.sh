#!/bin/bash
#SBATCH --job-name=cellpose
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=12:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

# Activar Conda
source /mnt/beegfs/home/pegomgal/anaconda3/etc/profile.d/conda.sh
conda activate cellpose

# Ruta de entrada
INPUT_DIR="/mnt/beegfs/home/pegomgal/MAMDC2/ECM/DAPI/raw/"
CELL_DIAMETER=90.0

# Ejecutar Python con argumentos
python cellpose_inference.py --input_dir "$INPUT_DIR" --diameter $CELL_DIAMETER

