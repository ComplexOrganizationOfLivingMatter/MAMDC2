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

imageResFactor = 0.2525251; %pixel width in um

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
        myotubesParams.totalSkelLength = sum(BW_skel(:)==1)*imageResFactor;
        allImgsParams(nImg) = myotubesParams;
    else
        [myotubesParams,nucleiIng_filt,nucleiClusters] = myotubes_analysis(BW_clean, BW_skel,imNuclei,rawImg);
        myotubesParams.fileName = imageName;
        myotubesParams.totalSkelLength = sum(BW_skel(:)==1)*imageResFactor;
        allImgsParams(nImg) = myotubesParams;
        save(fullfile(extractedFeaturesPath,strrep(imageName,'.tif','.mat')),'myotubesParams','nucleiClusters','nucleiIng_filt')
    end

    disp([num2str(nImg) '/' num2str(nOfImages) ' loaded - ' imageName])
    
   
end

T = struct2table(allImgsParams);
T_res = T(:,[25,1:14,26,15:24]);
T_res(:,[2:10,12:16,19])=T_res(:,[2:10,12:16,19]).*imageResFactor;
T_res(:,26)=T_res(:,26).*(imageResFactor^2);
T_res.overallRatioAreaLength = T_res.percMyoArea.*T_res.areaImage./T_res.totalSkelLength;


writetable(T_res,fullfile(extractedFeaturesPath,['features_perFibreIncluded_' date '.xlsx']))

T_wholeImg = T_res(:,[1,4,9,10,16,18,27,20:26]);
T_wholeImg.largestConnectedSkel = T_res.maxSkelLength;
writetable(T_wholeImg,fullfile(extractedFeaturesPath,['features_wholeImg_' date '.xlsx']))

