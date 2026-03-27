# ecm_utils.py
import numpy as np
import pandas as pd
from skimage.io import imsave
from skimage.color import label2rgb
from skimage.measure import regionprops
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree
from scipy.spatial.distance import chebyshev # <--- Added for Microsa straightness

def save_binary(path, img_bool):
    """Saves a boolean array as a binary image."""
    imsave(path, (img_bool * 255).astype(np.uint8), check_contrast=False)

def save_labeled(path, labeled_img):
    """Saves a labeled mask as an RGB image for visualization."""
    rgb = label2rgb(labeled_img, bg_label=0) 
    imsave(path, (rgb * 255).astype(np.uint8), check_contrast=False)

def convert_to_0_180_degrees(radians_array):
    """Converts radians to a 0-180 degree scale."""
    return np.degrees(radians_array) % 180

def extract_microsa_geometry(skel_labeled, binary_mask, channel_img, neighborhood_radius=75):
    """
    Extracts Microsa-aligned geometry using exact Microsa algorithms (Chebyshev distance).
    Utilizes cKDTree for highly optimized spatial searching to determine neighborhood interactions.
    """
    edt_map = distance_transform_edt(binary_mask)
    props = regionprops(skel_labeled)
    
    # Extract coordinates of all fiber pixels simultaneously
    skel_coords = np.column_stack(np.where(skel_labeled > 0))
    
    # Return empty DataFrame if no fibers are detected
    if len(skel_coords) == 0:
        return pd.DataFrame()
        
    skel_ids = skel_labeled[skel_coords[:, 0], skel_coords[:, 1]]
    
    # Build the spatial tree for fast neighbor querying
    tree = cKDTree(skel_coords)

    data = []
    for p in props:
        f_id = p.label
        length = p.area 
        coords = p.coords
        
        if length > 3:
            # 1:1 Microsa replication: Lexicographical sort to find endpoints
            sorted_indices = np.lexsort(coords.T)
            p1 = coords[sorted_indices[0]]
            p2 = coords[sorted_indices[-1]]
            
            # 1:1 Microsa replication: Chebyshev distance divided by area
            end_to_end_dist = chebyshev(p1, p2)
            straightness = end_to_end_dist / length
            straightness = min(straightness, 1.0) 
            
            # Angle: Calculate the vector between the endpoints
            dy = p2[0] - p1[0] 
            dx = p2[1] - p1[1] 
            angle_rad = np.arctan2(dy, dx)
            angle_deg = np.degrees(angle_rad) % 180
            
        else:
            # Fallback metrics for extremely small fibers
            straightness = 1.0
            angle_deg = convert_to_0_180_degrees(p.orientation) if hasattr(p, 'orientation') else 0

        mean_intensity = np.mean(channel_img[coords[:, 0], coords[:, 1]])
        
        # 1:1 Microsa replication: Sum of thickness matrix divided by area
        edt_vals = edt_map[coords[:, 0], coords[:, 1]]
        mean_thickness = np.sum(edt_vals) / length
        
        # Fast neighbor search using cKDTree with subsampling for computational efficiency
        f_coords_subsampled = coords[::5] 
        
        # Query the spatial tree for indices within the defined neighborhood radius
        indices_lists = tree.query_ball_point(f_coords_subsampled, r=neighborhood_radius)
        
        # Flatten the list of indices and extract unique intersecting fiber IDs
        flat_indices = np.unique(np.concatenate(indices_lists))
        overlapping_ids = np.unique(skel_ids[flat_indices])
        
        neighbors_count = len(overlapping_ids[(overlapping_ids != 0) & (overlapping_ids != f_id)])
        
        data.append({
            'number': f_id,
            'neighboring fibs': neighbors_count,
            'length': length,
            'angle': angle_deg,
            'strightness': straightness,
            'thickness': mean_thickness,
            'intensity': mean_intensity
        })
        
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Compute global alignment parameter based on angular variance
        mean_angle_rad = np.radians(df['angle'].mean())
        df['alignment'] = np.cos(np.radians(df['angle']) - mean_angle_rad)**2
        df = df[['number', 'neighboring fibs', 'length', 'angle', 'strightness', 'thickness', 'alignment', 'intensity']]
        
    return df

def calculate_interactions(nuclei_labeled, fibers_labeled, fibers_df, prefix, interaction_radius=75):
    """
    Calculates nucleus-fiber intersections using cKDTree spatial mapping.
    """
    interactions = []
    n_regions = regionprops(nuclei_labeled)
    
    # Extract fiber coordinates and build the spatial tree
    skel_coords = np.column_stack(np.where(fibers_labeled > 0))
    
    # Return appropriately structured empty DataFrames if no fibers exist
    if len(skel_coords) == 0:
        nuclei_stats = pd.DataFrame({'cell_ID': [prop.label for prop in n_regions]})
        for col in [f'{prefix}_touching_fibers_count', f'{prefix}_avg_fiber_length', f'{prefix}_std_fiber_length', f'{prefix}_avg_fiber_angle', f'{prefix}_std_fiber_angle']:
            nuclei_stats[col] = 0 if 'count' in col else np.nan
        return nuclei_stats, fibers_df

    skel_ids = fibers_labeled[skel_coords[:, 0], skel_coords[:, 1]]
    tree = cKDTree(skel_coords)
    
    for prop in n_regions:
        cell_id = prop.label
        centroid = prop.centroid  
        
        # Query the spatial tree for all fiber pixels within the interaction radius of the centroid
        indices = tree.query_ball_point(centroid, r=interaction_radius)
        
        if len(indices) > 0:
            unique_f_ids = np.unique(skel_ids[indices])
            for f_id in unique_f_ids[unique_f_ids != 0]:
                interactions.append({'cell_ID': cell_id, 'number': f_id})
            
    interactions_df = pd.DataFrame(interactions)
    nuclei_stats = pd.DataFrame({'cell_ID': [prop.label for prop in n_regions]})
    
    if not interactions_df.empty:
        # Calculate the number of distinct nuclei touching each fiber
        fiber_counts = interactions_df.groupby('number')['cell_ID'].nunique().reset_index()
        fiber_counts.rename(columns={'cell_ID': 'touching_nuclei_count'}, inplace=True)
        fibers_df = pd.merge(fibers_df, fiber_counts, on='number', how='left')
    
    fibers_df['touching_nuclei_count'] = fibers_df.get('touching_nuclei_count', pd.Series(dtype=float)).fillna(0).astype(int)

    if not interactions_df.empty and not fibers_df.empty:
        details = pd.merge(interactions_df, fibers_df[['number', 'length', 'angle']], on='number', how='left')
        
        stats = details.groupby('cell_ID').agg(
            touching_count=('number', 'nunique'),
            avg_length=('length', 'mean'),
            std_length=('length', 'std'),
            avg_angle=('angle', 'mean'),
            std_angle=('angle', 'std')
        ).reset_index()
        
        stats.rename(columns={
            'touching_count': f'{prefix}_touching_fibers_count',
            'avg_length': f'{prefix}_avg_fiber_length',
            'std_length': f'{prefix}_std_fiber_length',
            'avg_angle': f'{prefix}_avg_fiber_angle',
            'std_angle': f'{prefix}_std_fiber_angle'
        }, inplace=True)
        
        nuclei_stats = pd.merge(nuclei_stats, stats, on='cell_ID', how='left')

    # Ensure all expected columns exist and handle missing values
    count_col = f'{prefix}_touching_fibers_count'
    if count_col in nuclei_stats.columns:
        nuclei_stats[count_col] = nuclei_stats[count_col].fillna(0).astype(int)
    else:
        for col in [count_col, f'{prefix}_avg_fiber_length', f'{prefix}_std_fiber_length', f'{prefix}_avg_fiber_angle', f'{prefix}_std_fiber_angle']:
            nuclei_stats[col] = 0 if 'count' in col else np.nan

    return nuclei_stats, fibers_df