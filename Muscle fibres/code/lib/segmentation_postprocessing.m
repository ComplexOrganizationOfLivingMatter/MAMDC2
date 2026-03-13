function BW_clean = segmentation_postprocessing(segmentedImg,lengthMin)


    BW = imbinarize(segmentedImg, 'adaptive'); %% check oversegmentation
    %[BW] = imbinarize(segmentedImg, 0.95); %%as the model is very precise w
    
    SE = strel('disk',5,8);
    BW_close = imclose(BW,SE); 
    
    L_img = bwlabel(BW_close);
    props = regionprops(L_img,'all');

    %filter by length
    objDiameter =[props(:).MaxFeretDiameter]';

    obj2del = find(objDiameter<lengthMin);

    BW2del= ismember(L_img,obj2del);
    BW_filt = BW_close;
    BW_filt(BW2del)=0;

    %%fill small holes
    invertedBW = 1- BW_filt;
    areaHoles = 5000;
    BW_clean = uint8(1-bwareaopen(invertedBW, areaHoles))*255;

end