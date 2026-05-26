%% Pipeline for myotubes culture analysis
% This script performs post-processing on semantic segmentation masks,
% extracts skeletonized myofibres, and analyzes nuclei distribution.

clear all;
close all;
addpath(genpath('lib')) % Load custom utility functions

%% 1. Path Configuration
% Define source directories for inferred masks, raw images, and output results
inferredImagesPath = fullfile('..','biapyModel','myotubesInference', 'results', 'myotubesInference_1','per_image');
rawImagesPath =  fullfile('..','raw images','tifs','rawMyotubesProjection');
segmentationMyofibresPath = fullfile('..','results','segmentedMyofibres');
skelMyofibresPath = fullfile('..','results','skeletonizedMyofibres');
segmentedNucleiPath = fullfile('..','results','segmentedNuclei_rz05');
extractedFeaturesPath = fullfile('..','results','extractedFeatures');

% Initialize image list and physical resolution settings
listOfImageNames = dir(fullfile(inferredImagesPath, '*.tif'));
nOfImages = size(listOfImageNames,1);
imageResFactor = 0.2525251; % Pixel width calibration (um/pixel)

%% 2. Image Processing Loop
for nImg = 1:nOfImages
    imageName = listOfImageNames(nImg).name;
    rawImg = imread(fullfile(rawImagesPath, imageName));

    % Check if pre-processed masks already exist to save computation time
    if exist(fullfile(segmentationMyofibresPath, imageName),'file')
        BW_clean = imread(fullfile(segmentationMyofibresPath, imageName));
        BW_skel = imread(fullfile(skelMyofibresPath, imageName));
    else
        % Process raw inference masks if clean masks are missing
        minMyotubeLength = 600; % Threshold for filtering small artifacts (approx 150 um)
        
        % Convert probabilities to binary and apply morphological cleaning
        inferredSegmentationImg = uint8(imread(fullfile(inferredImagesPath, imageName))*255);
        BW_clean = segmentation_postprocessing(inferredSegmentationImg, minMyotubeLength);
        imwrite(BW_clean, fullfile(segmentationMyofibresPath, imageName));

        % Generate skeletonized representation of the fibres
        BW_skel = skeletonizeFibres(BW_clean, minMyotubeLength);
        imwrite(BW_skel, fullfile(skelMyofibresPath, imageName));
    end

    % Load and resize segmented nuclei masks to match raw image dimensions
    imNuclei = imread(fullfile(segmentedNucleiPath, imageName));
    imNuclei = imresize(imNuclei, size(rawImg), 'nearest');
    
    %% 3. Feature Extraction
    % Load cached features or calculate new morphological parameters
    if exist(fullfile(extractedFeaturesPath, strrep(imageName,'.tif','.mat')),'file')
        load(fullfile(extractedFeaturesPath, strrep(imageName,'.tif','.mat')))
        % Update skeleton length with calibrated units
        myotubesParams.totalSkelLength = sum(BW_skel(:) == 1) * imageResFactor;
        allImgsParams(nImg) = myotubesParams;
    else
        % Core analysis: calculate myofibre geometry and nuclei spatial distribution
        [myotubesParams, nucleiIng_filt, nucleiClusters] = myotubes_analysis(BW_clean, BW_skel, imNuclei, rawImg);
        
        myotubesParams.fileName = imageName;
        myotubesParams.totalSkelLength = sum(BW_skel(:) == 1) * imageResFactor;
        allImgsParams(nImg) = myotubesParams;
        
        % Archive results for reproducibility
        save(fullfile(extractedFeaturesPath, strrep(imageName,'.tif','.mat')), ...
            'myotubesParams', 'nucleiClusters', 'nucleiIng_filt')
    end

    disp([num2str(nImg) '/' num2str(nOfImages) ' processed: ' imageName])
end

%% 4. Data Conversion and Normalization
% Convert structure array to table for statistical export
T = struct2table(allImgsParams);

% Reorganize and calibrate table columns
T_res = T(:,[25,1:14,26,15:24]); % Reorder columns for logical grouping
T_res(:,[2:10,12:16,19]) = T_res(:,[2:10,12:16,19]) .* imageResFactor; % Convert pixels to um
T_res(:,26) = T_res(:,26) .* (imageResFactor^2); % Convert area to um^2

% Calculate derived metric: Area-to-Length ratio
T_res.overallRatioAreaLength = T_res.percMyoArea .* T_res.areaImage ./ T_res.totalSkelLength;

%% 5. Export Results
% Save detailed features per fibre
writetable(T_res, fullfile(extractedFeaturesPath, ['features_perFibreIncluded_' date '.xlsx']))

% Generate and save a summary table focusing on whole-image metrics
T_wholeImg = T_res(:,[1,4,9,10,16,18,27,20:26]);
T_wholeImg.largestConnectedSkel = T_res.maxSkelLength;
writetable(T_wholeImg, fullfile(extractedFeaturesPath, ['features_wholeImg_' date '.xlsx']))