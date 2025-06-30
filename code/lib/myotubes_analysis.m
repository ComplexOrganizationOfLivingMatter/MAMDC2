function [params,imgNuclei_noUnder,nucleiClusters] = myotubes_analysis(BW_clean, BW_skel, imgNuclei,rawImage)

    %% Fibres diameter quantification. Diameter counted as distance from skeleton point to the closest black pixel.
    %%find approximatly equidistanced points along the individual skeletons
    ptDistance = 300;
    L_fibres = bwlabel(BW_clean,8);
    L_skel = bwlabel(BW_skel,8);
    
    [params.aveg_meanDiam, params.std_meanDiam, params.max_maxDiam, params.aveg_maxDiam, ....
        params.std_maxDiam, params.aveg_stdDiam, params.std_stdDiam,params.avg_diamWholeCulture, params.std_diamWholeCulture, listOfMeanDiam,listOfMaxDiam,listOfStdDiam] ...
     = diameter_measurement(L_skel,BW_clean,ptDistance);
    
    %% number of individual fibres
    params.nFibres = max(L_skel(:));
    
    %% Skeleton myotubes length and branches
    parfor nSkel = 1:params.nFibres
        individualSkel = L_skel==nSkel;
        maxLen(nSkel) = maxGeodesicSkeletonLength(individualSkel);
        endpointsMask = bwmorph(individualSkel, 'endpoints');
        % Get (row, column) coordinates of endpoints
        [yEP, xEP] = find(endpointsMask);
    
        nEP(nSkel) = length(yEP);
    end
    params.medianSkelLength = median(maxLen);
    params.meanSkelLength = mean(maxLen);
    params.stdSkelLength = std(maxLen);
    params.maxSkelLength = max(maxLen);
    
    nEP = nEP-2;
    nEP(nEP<0)=0;
    params.meanBranches = mean(nEP);
    params.totalBranches = sum(nEP);
    
    
    %% Myotubes area/skeleton length
    areaFibres = regionprops(L_fibres,'area');
    nonZeroSkel=maxLen>0;
    ratioAreaLength = horzcat(areaFibres(nonZeroSkel).Area)./maxLen(nonZeroSkel);
    params.meanRatioAreaLength =  mean(ratioAreaLength);
    
    %% % of area covered by myotubes
    % Count white pixels
    whitePixels = sum(logical(BW_clean(:)));
    totalPixels = numel(BW_clean);
    % Compute percentage
    params.percMyoArea = 100 * whitePixels / totalPixels;
    
    
    %% fusion index: nuclei in tubes / total nuclei. In nuclei need to be including within the fibre more than a 80%
    areaNuclei = vertcat(regionprops(imgNuclei,'area').Area);
    id2remUnder = find(areaNuclei < (median(areaNuclei) - 2*std(areaNuclei)));
    
    imgNuclei_noUnder=imgNuclei;
    imgNuclei_noUnder(ismember(imgNuclei,vertcat(id2remUnder)))=0;
    areaNuclei = vertcat(regionprops(imgNuclei_noUnder,'area').Area);
    imgNucleiInFibres = imgNuclei_noUnder;
    imgNucleiInFibres(BW_clean==0)=0;
    areaNucleiFibres = vertcat(regionprops(imgNucleiInFibres,'area').Area);
    percThreshIn = 80; %percentage threshold in. Nuclei with % area 
    percNucleiIn = areaNucleiFibres./areaNuclei(1:length(areaNucleiFibres));
    
    idsNucleiIn = find(percNucleiIn*100 > percThreshIn);
    nNucleiIn = length(idsNucleiIn);
    
    params.fusionIndex = nNucleiIn/sum(areaNuclei>0);
    params.totalNuclei = sum(areaNuclei>0);

    %% number of nuclei clusters
    threshClusterDistance = 20; %within 5 um, same cluster
    nucleiInFibres_filtered = imgNucleiInFibres .* uint16(ismember(imgNucleiInFibres,idsNucleiIn)); 
    [nucleiClusters,nNucleiPerCluster] = clusterNucleiByOutline(nucleiInFibres_filtered, threshClusterDistance);
    params.nNucleiClusters = length(nNucleiPerCluster);
    
    %%average nuclei per cluster
    params.meanNucleiPerCluster = mean(nNucleiPerCluster);
    
    %% myofibres intensity level in max projection
    params.meanMyoIntensity = mean(rawImage(logical(BW_clean)));
    
    %% areaImage
    params.areaImage=totalPixels;

end