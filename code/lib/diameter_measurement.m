function     [aveg_meanDiam, std_meanDiam, max_maxDiam, aveg_maxDiam, ....
    std_maxDiam, aveg_stdDiam, std_stdDiam,avg_diamWholeCulture, std_diamWholeCulture, listOfMeanDiam,listOfMaxDiam,listOfStdDiam] ...
 = diameter_measurement(L_skel,BW_clean,ptDistance)

    
    numSkel = max(L_skel(:));
    mean_diameter = zeros(1, numSkel);
    max_diameter = zeros(1, numSkel);
    std_diameter = zeros(1, numSkel);
    allMinDistances=[];

    for nSkel = 1:numSkel

        BW_skel=false(size(L_skel));
        BW_skel(L_skel == nSkel) = 1;
    
    
        % 1. Get skeleton coordinates
        [y_skel, x_skel] = find(BW_skel);
        skel_pts = [x_skel, y_skel];
        
        % 2. Create 3D point cloud (z=0)
        pts = [x_skel, y_skel, zeros(size(x_skel))];
        pc = pointCloud(pts);
        
        % 3. Downsample
        pc_ds = pcdownsample(pc, 'gridAverage', ptDistance);
        
        % 4. Extract 2D downsampled coordinates
        xy_ds = pc_ds.Location(:,1:2);               % [X Y] of downsampled points
    
        % 5. Snap each point to closest skeleton pixel
        idx_nearest = knnsearch(skel_pts, xy_ds);    % nearest real skeleton pixel
        snapped_pts = skel_pts(idx_nearest, :);      % [X Y] of snapped points
    
        % % 6. Plot
        % imshow(BW_skel); hold on;
        % plot(snapped_pts(:,1), snapped_pts(:,2), 'r.', 'MarkerSize', 15);
        % 
    
    
        %% Quantify equidistant diameter per fibre
        % 1. Compute distance transform: 
        % For each pixel, distance to nearest zero (background)
        D = bwdist(~BW_clean);  % D is same size as BW_clean
        
        % 2. For each point in snapped_pts, find its distance by indexing D:
        % snapped_pts = Nx2 array of [X Y]
        
        % Round coordinates to integer pixel indices:
        xq = round(snapped_pts(:,1));
        yq = round(snapped_pts(:,2));
        
        % Make sure indices are inside image bounds
        xq = max(min(xq, size(BW_clean,2)),1);
        yq = max(min(yq, size(BW_clean,1)),1);
        
        % 3. Extract distances at point locations
        min_distances = D(sub2ind(size(BW_clean), yq, xq));

        allMinDistances = [allMinDistances;min_distances];
        mean_diameter(nSkel) = mean(min_distances);
        max_diameter(nSkel) = max(min_distances);
        std_diameter(nSkel) = std(min_distances);
    end

    
    aveg_meanDiam = mean(mean_diameter);
    std_meanDiam = std(mean_diameter);
    max_maxDiam = max(max_diameter);
    aveg_maxDiam = mean(max_diameter);
    std_maxDiam = std(max_diameter);
    aveg_stdDiam = mean(std_diameter);
    std_stdDiam = std(std_diameter);
    listOfMeanDiam = mean_diameter;
    listOfMaxDiam = max_diameter;
    listOfStdDiam = std_diameter;
    avg_diamWholeCulture = mean(allMinDistances);
    std_diamWholeCulture = std(allMinDistances);

end