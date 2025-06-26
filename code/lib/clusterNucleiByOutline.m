function [nucleiClusters,nNucleiPerCluster] = clusterNucleiByOutline(labelledNuclei, distanceThreshold)
    % Inputs:
    % - labelledNuclei: 2D label image (e.g., output of bwlabel)
    % - distanceThreshold: max distance (in pixels) to consider nuclei clustered

    BW_nuclei = labelledNuclei>0;

    dilatedNuclei = imdilate(BW_nuclei, strel('disk', round(distanceThreshold/2)));

    nucleiClusters = bwlabel(dilatedNuclei,8);
    nucleiClusters(labelledNuclei==0)=0;

    totalClusters =  max(nucleiClusters(:));
    nNucleiPerCluster = zeros(1,totalClusters);
    for nCluster = 1: totalClusters
        unqNuclei = labelledNuclei(nucleiClusters==nCluster);
        if unqNuclei>0
            nNucleiPerCluster(nCluster) = length(unique(unqNuclei));
        end
    end

    nNucleiPerCluster(nNucleiPerCluster==0)=[];
end
