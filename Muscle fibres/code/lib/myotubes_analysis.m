function [params,imgNuclei_noUnder,nucleiClusters] = myotubes_analysis(BW_clean, BW_skel, imgNuclei,rawImage)

    %% 1. Myofibre Diameter Quantification
    % Define the sampling interval (pixels) for diameter measurements along the skeleton
    ptDistance = 300; 
    
    % Label connected components for both the binary masks and the skeletons
    L_fibres = bwlabel(BW_clean, 8);
    L_skel = bwlabel(BW_skel, 8);
    
    % Calculate diameter metrics (mean, std, max) based on the distance 
    % from skeleton points to the nearest background pixel.
    [params.aveg_meanDiam, params.std_meanDiam, params.max_maxDiam, params.aveg_maxDiam, ....
        params.std_maxDiam, params.aveg_stdDiam, params.std_stdDiam, params.avg_diamWholeCulture, ...
        params.std_diamWholeCulture, listOfMeanDiam, listOfMaxDiam, listOfStdDiam] ...
        = diameter_measurement(L_skel, BW_clean, ptDistance);
    
    %% 2. Morphological and Topological Analysis
    % Count total number of individual identified fibres
    params.nFibres = max(L_skel(:));
    
    % Extract length and branching complexity for each skeleton using parallel processing
    parfor nSkel = 1:params.nFibres
        individualSkel = (L_skel == nSkel);
        
        % Calculate the longest path within the skeleton (Geodesic length)
        maxLen(nSkel) = maxGeodesicSkeletonLength(individualSkel);
        
        % Identify endpoints to determine branching degree
        endpointsMask = bwmorph(individualSkel, 'endpoints');
        [yEP, xEP] = find(endpointsMask);
        nEP(nSkel) = length(yEP);
    end
    
    % Aggregate length statistics
    params.medianSkelLength = median(maxLen);
    params.meanSkelLength = mean(maxLen);
    params.stdSkelLength = std(maxLen);
    params.maxSkelLength = max(maxLen);
    
    % Branching logic: Subtract 2 endpoints (start/end) to count additional junctions/branches
    nEP = nEP - 2;
    nEP(nEP < 0) = 0; % Ensure isolated or simple fibres have 0 extra branches
    params.meanBranches = mean(nEP);
    params.totalBranches = sum(nEP);
    
    %% 3. Area and Occupancy Metrics
    % Calculate the ratio of cross-sectional area to longitudinal skeleton length
    areaFibres = regionprops(L_fibres, 'area');
    nonZeroSkel = maxLen > 0;
    ratioAreaLength = horzcat(areaFibres(nonZeroSkel).Area) ./ maxLen(nonZeroSkel);
    params.meanRatioAreaLength = mean(ratioAreaLength);
    
    % Calculate the total percentage of the image area covered by myotubes
    whitePixels = sum(logical(BW_clean(:)));
    totalPixels = numel(BW_clean);
    params.percMyoArea = 100 * whitePixels / totalPixels;
    
    %% 4. Fusion Index and Nuclei Analysis
    % Filter out segmented nuclei with outlier areas (under-segmented/artifacts)
    areaNuclei = vertcat(regionprops(imgNuclei, 'area').Area);
    id2remUnder = find(areaNuclei < (median(areaNuclei) - 2 * std(areaNuclei)));
    
    imgNuclei_noUnder = imgNuclei;
    imgNuclei_noUnder(ismember(imgNuclei, vertcat(id2remUnder))) = 0;
    areaNuclei = vertcat(regionprops(imgNuclei_noUnder, 'area').Area);
    
    % Determine Myogenic Fusion Index:
    % A nucleus is "fused" if >80% of its area overlaps with a myofibre mask
    imgNucleiInFibres = imgNuclei_noUnder;
    imgNucleiInFibres(BW_clean == 0) = 0; % Mask nuclei by fibre regions
    areaNucleiFibres = vertcat(regionprops(imgNucleiInFibres, 'area').Area);
    
    percThreshIn = 80; 
    percNucleiIn = areaNucleiFibres ./ areaNuclei(1:length(areaNucleiFibres));
    idsNucleiIn = find(percNucleiIn * 100 > percThreshIn);
    
    params.fusionIndex = length(idsNucleiIn) / sum(areaNuclei > 0);
    params.totalNuclei = sum(areaNuclei > 0);
    
    %% 5. Spatial Nuclei Distribution (Clustering)
    % Define proximity threshold for spatial clustering (e.g., 20 pixels ≈ 5 um)
    threshClusterDistance = 20; 
    nucleiInFibres_filtered = imgNucleiInFibres .* uint16(ismember(imgNucleiInFibres, idsNucleiIn)); 
    
    % Cluster fused nuclei based on centroid/outline distance
    [nucleiClusters, nNucleiPerCluster] = clusterNucleiByOutline(nucleiInFibres_filtered, threshClusterDistance);
    params.nNucleiClusters = length(nNucleiPerCluster);
    params.meanNucleiPerCluster = mean(nNucleiPerCluster);
    
    %% 6. Fluorescence and Image size
    % Quantify average signal intensity within the segmented myofibre regions
    params.meanMyoIntensity = mean(rawImage(logical(BW_clean)));
    params.areaImage = totalPixels;

end