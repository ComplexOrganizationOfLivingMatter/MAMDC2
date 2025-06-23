%% Postprocessing after semantic segmentation
clear all;
close all;
addpath(genpath('lib'))

inferredImagesPath = fullfile('..','biapyModel','myotubesInference', 'results', 'myotubesInference_1','per_image');
rawImagesPath =  fullfile('..','raw images','tifs','rawMyotubesProjection');
listOfImageNames = dir(fullfile(inferredImagesPath, '*.tif'));

for nImg =1:size(listOfImageNames,1)

    imageName = listOfImageNames(nImg).name;
    inferredSegmentationImg = uint8(imread(fullfile(inferredImagesPath, imageName))*255);
    rawImg = imread(fullfile(rawImagesPath, imageName));
    [BW_clean, BW_skel] = segmentation_postprocessing(inferredSegmentationImg,rawImg);
    
    myotubesParams = myotubes_analysis(BW_clean, BW_skel);


end