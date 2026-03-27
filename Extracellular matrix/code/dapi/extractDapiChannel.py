# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 10:12:32 2026

@author: pedro
"""

import os
import tifffile
import numpy as np
from pathlib import Path

# 1. Definir rutas (usando r"" para evitar problemas con las barras de Windows)
source_folder = Path(r"F:\Lab\MAMDC2\Extracellular matrix\tiled_images")
# El nivel superior de la carpeta de imágenes
base_parent = source_folder.parent 

dapi_raw_path = base_parent / "DAPI" / "raw"
dapi_seg_path = base_parent / "DAPI" / "segmentation"

# 2. Crear las carpetas de destino
dapi_raw_path.mkdir(parents=True, exist_ok=True)
dapi_seg_path.mkdir(parents=True, exist_ok=True)

print(f"Buscando archivos .tif en: {source_folder}")

# 3. Procesar las imágenes
for file_path in source_folder.glob("*.tif"):
    try:
        # Leer la imagen tif
        img = tifffile.imread(str(file_path))
        
        # Extraer el tercer canal (Canal B)
        # Nota: En arrays de numpy (RGB), el índice 0=R, 1=G, 2=B.
        # Si tu imagen tiene la forma (Canales, Alto, Ancho), usa img[2, :, :]
        # Si tiene la forma (Alto, Ancho, Canales), usa img[:, :, 2]
        
        if img.ndim == 3:
            # Asumiendo formato estándar (H, W, C)
            canal_dapi = img[:, :, 2]
            
            # Guardar el canal extraído en la nueva ubicación
            save_path = dapi_raw_path / file_path.name
            tifffile.imwrite(str(save_path), canal_dapi, photometric='minisblack')
            
            print(f"Éxito: {file_path.name} -> DAPI extraído.")
        else:
            print(f"Omitido: {file_path.name} no parece tener 3 canales.")
            
    except Exception as e:
        print(f"Error procesando {file_path.name}: {e}")

print(f"\nProceso finalizado. Imágenes para segmentar en: {dapi_raw_path}")