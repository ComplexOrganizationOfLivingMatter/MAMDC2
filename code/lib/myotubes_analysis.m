function params = myotubes_analysis(BW_clean, BW_skel)

%% Fibres diameter quantification. Diameter counted as distance from skeleton point to the closest black pixel.
%%find approximatly equidistanced points along the individual skeletons
ptDistance = 300;
L_skel = bwlabel(BW_skel,8);
[fibresParams.aveg_meanDiam, fibresParams.std_meanDiam, fibresParams.max_maxDiam, fibresParams.aveg_maxDiam, ....
    fibresParams.std_maxDiam, fibresParams.aveg_stdDiam, fibresParams.std_stdDiam,fibresParams.avg_diamWholeCulture, fibresParams.std_diamWholeCulture, listOfMeanDiam,listOfMaxDiam,listOfStdDiam] ...
 = diameter_measurement(L_skel,ptDistance);

%% number of branching points 
endPoints = bwmorph(BW_skel, 'endpoints');
nBranches = 
minBranchDistance = XXX;


%% number of myotubes per image


%% myotubes density. 

%% % of area covered my myotubes

%% myotubes length

%% fusion index: nuclei in tubes / total nuclei

%% number of nuclei clusters

%% average nuclei per cluster

%% myofibres intensity level in max projection

%% nuclei number along the image/density



end