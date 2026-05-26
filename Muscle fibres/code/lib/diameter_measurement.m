function [aveg_meanDiam, std_meanDiam, max_maxDiam, aveg_maxDiam, ....
    std_maxDiam, aveg_stdDiam, std_stdDiam, avg_diamWholeCulture, ...
    std_diamWholeCulture, listOfMeanDiam, listOfMaxDiam, listOfStdDiam] ...
    = diameter_measurement(L_skel, BW_clean, ptDistance)
    % DIAMETER_MEASUREMENT Calculates myofibre thickness using distance transform
    % sampling at equidistant points along the longitudinal skeleton.
    %
    % Logic: By downsampling the skeleton, we ensure diameter measurements 
    % are taken at regular spatial intervals, providing a non-biased average.

    numSkel = max(L_skel(:));
    mean_diameter = zeros(1, numSkel);
    max_diameter = zeros(1, numSkel);
    std_diameter = zeros(1, numSkel);
    allMinDistances = [];

    %% 1. Distance Transform Calculation
    % Compute the Euclidean Distance Transform (EDT). For every foreground 
    % pixel, D contains the distance to the nearest background pixel.
    % Note: This value represents the 'radius'; we multiply by 2 later or 
    % treat as half-width metrics.
    D = bwdist(~BW_clean); 

    for nSkel = 1:numSkel
        % Isolate the current individual fibre skeleton
        BW_skel = (L_skel == nSkel);
        
        % Extract pixel coordinates of the skeleton
        [y_skel, x_skel] = find(BW_skel);
        skel_pts = [x_skel, y_skel];
        
        %% 2. Equidistant Point Sampling
        % To avoid biased sampling, we treat the skeleton as a 3D point cloud 
        % and use grid-average downsampling to pick points every 'ptDistance'.
        pts = [x_skel, y_skel, zeros(size(x_skel))];
        pc = pointCloud(pts);
        pc_ds = pcdownsample(pc, 'gridAverage', ptDistance);
        
        % Extract the 2D coordinates of the downsampled points
        xy_ds = pc_ds.Location(:,1:2); 
    
        % 'Snap' downsampled points back to the nearest real skeleton pixel 
        % indices using a k-nearest neighbor search.
        idx_nearest = knnsearch(skel_pts, xy_ds);
        snapped_pts = skel_pts(idx_nearest, :);
    
        %% 3. Diameter Extraction
        % Convert [X, Y] coordinates to integer indices for matrix lookup
        xq = round(snapped_pts(:,1));
        yq = round(snapped_pts(:,2));
        
        % Boundary constraint: ensure indices remain within image dimensions
        xq = max(min(xq, size(BW_clean, 2)), 1);
        yq = max(min(yq, size(BW_clean, 1)), 1);
        
        % Sample the Distance Transform at the selected skeleton locations.
        % This represents the distance from the center (skeleton) to the edge.
        min_distances = D(sub2ind(size(BW_clean), yq, xq));

        % Store results for this specific fibre (local metrics)
        allMinDistances = [allMinDistances; min_distances];
        mean_diameter(nSkel) = mean(min_distances);
        max_diameter(nSkel) = max(min_distances);
        std_diameter(nSkel) = std(min_distances);
    end

    %% 4. Statistical Aggregation (Global Metrics)
    % Calculate population-wide statistics across all identified fibres
    aveg_meanDiam = mean(mean_diameter);    % Mean of means
    std_meanDiam  = std(mean_diameter);     % Variability between fibres
    max_maxDiam   = max(max_diameter);      % Absolute maximum thickness found
    aveg_maxDiam  = mean(max_diameter);     % Average of the maximums
    std_maxDiam   = std(max_diameter);
    aveg_stdDiam  = mean(std_diameter);     % Intra-fibre diameter regularity
    std_stdDiam   = std(std_diameter);
    
    % Export raw lists for distribution plotting (histograms)
    listOfMeanDiam = mean_diameter;
    listOfMaxDiam  = max_diameter;
    listOfStdDiam  = std_diameter;
    
    % Cumulative culture statistics (pooling every sampled point)
    avg_diamWholeCulture = mean(allMinDistances);
    std_diamWholeCulture = std(allMinDistances);

end