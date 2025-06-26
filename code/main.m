%% Postprocessing after semantic segmentation
clear all;
close all;
addpath(genpath('lib'))

inferredImagesPath = fullfile('..','biapyModel','myotubesInference', 'results', 'myotubesInference_1','per_image');
rawImagesPath =  fullfile('..','raw images','tifs','rawMyotubesProjection');
segmentationMyofibresPath = fullfile('..','results','segmentedMyofibres');
skelMyofibresPath = fullfile('..','results','skeletonizedMyofibres');
segmentedNucleiPath = fullfile('..','results','segmentedNuclei_rz05');
extractedFeaturesPath = fullfile('..','results','extractedFeatures');

listOfImageNames = dir(fullfile(inferredImagesPath, '*.tif'));
nOfImages = size(listOfImageNames,1);

for nImg =1:nOfImages

    imageName = listOfImageNames(nImg).name;
    
    rawImg = imread(fullfile(rawImagesPath, imageName));

    if exist(fullfile(segmentationMyofibresPath, imageName),'file')
        BW_clean = imread(fullfile(segmentationMyofibresPath, imageName));
        BW_skel = imread(fullfile(skelMyofibresPath, imageName));
    else
        minMyotubeLength = 600; %150 um
        %write 
        inferredSegmentationImg = uint8(imread(fullfile(inferredImagesPath, imageName))*255);
        BW_clean = segmentation_postprocessing(inferredSegmentationImg,minMyotubeLength);
        imwrite(BW_clean, fullfile(segmentationMyofibresPath, imageName));

        %skeletonize
        BW_skel = skeletonizeFibres(BW_clean,minMyotubeLength);
        imwrite(BW_skel,fullfile(skelMyofibresPath, imageName));
    end

    %load segmented nuclei (cellpose-SAM)
    imNuclei = imread(fullfile(segmentedNucleiPath,imageName));
    imNuclei=imresize(imNuclei,size(rawImg),'nearest');
    

    if exist(fullfile(extractedFeaturesPath,strrep(imageName,'.tif','.mat')),'file')
        load(fullfile(extractedFeaturesPath,strrep(imageName,'.tif','.mat')))
        allImgsParams(nImg) = myotubesParams;
    else
        [myotubesParams,nucleiClusters] = myotubes_analysis(BW_clean, BW_skel,imNuclei,rawImg);
        myotubesParams.fileName = imageName;
        allImgsParams(nImg) = myotubesParams;
        save(fullfile(extractedFeaturesPath,strrep(imageName,'.tif','.mat')),'myotubesParams','nucleiClusters')
    end

    disp([num2str(nImg) '/' num2str(nOfImages) ' loaded - ' imageName])
    
   
end

T = struct2table(allImgsParams);
writetable(T,fullfile(extractedFeaturesPath,'allImagesFeatures.xlsx'))


    
