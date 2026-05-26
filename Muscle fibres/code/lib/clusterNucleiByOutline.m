function [nucleiClusters, nNucleiPerCluster_largerThan1] = clusterNucleiByOutline(labelledNuclei, distanceThreshold)
    % CLUSTERNUCLEIBYOUTLINE Groups individual nuclei into clusters based on 
    % their spatial proximity to one another.
    %
    % Logic: Nuclei are considered part of the same cluster if the distance 
    % between their boundaries is less than or equal to the distanceThreshold.
    
    % 1. Create a binary mask of all nuclei
    BW_nuclei = labelledNuclei > 0;

    %% 2. Proximity Grouping via Morphological Dilation
    % Dilate each nucleus by half the threshold distance. If two nuclei are 
    % closer than the threshold, their dilated boundaries will merge.
    dilatedNuclei = imdilate(BW_nuclei, strel('disk', round(distanceThreshold/2)));

    % Label the merged regions as distinct clusters
    nucleiClusters = bwlabel(dilatedNuclei, 8);
    
    % Mask the clusters back to the original nuclei shapes (remove the dilation area)
    % so that 'nucleiClusters' only contains pixels belonging to actual nuclei.
    nucleiClusters(labelledNuclei == 0) = 0;

    %% 3. Cluster Quantification
    totalClusters = max(nucleiClusters(:));
    nNucleiPerCluster = zeros(1, totalClusters);
    
    for nCluster = 1:totalClusters
        % Identify which unique nucleus IDs from the original label image 
        % fall within the current cluster boundaries.
        unqNuclei = labelledNuclei(nucleiClusters == nCluster);
        
        % Filter out background (0) and count the number of unique nuclei
        unqNuclei(unqNuclei == 0) = [];
        if ~isempty(unqNuclei)
            nNucleiPerCluster(nCluster) = length(unique(unqNuclei));
        end
    end

    %% 4. Data Refinement
    % Remove entries for empty clusters (if any)
    nNucleiPerCluster(nNucleiPerCluster == 0) = [];

    % Filter results to return only "true" clusters (containing more than 1 nucleus)
    % Single isolated nuclei are excluded from this specific output.
    nNucleiPerCluster_largerThan1 = nNucleiPerCluster;
    nNucleiPerCluster_largerThan1(nNucleiPerCluster == 1) = [];
end