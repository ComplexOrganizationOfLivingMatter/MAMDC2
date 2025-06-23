function [BW_clean, BW_skel] = segmentation_postprocessing(segmentedImg, rawImg)


    % imshow([segmentedImg,rawImg])
    BW = imbinarize(segmentedImg, 'adaptive'); %% check oversegmentation
    %[BW] = imbinarize(segmentedImg, 0.95); %%as the model is very precise w
    
    SE = strel('disk',5,8);
    BW_close = imclose(BW,SE); 

    %imshow([uint8(BW*255),rawImg])

    L_img = bwlabel(BW_close);
    props = regionprops(L_img,'all');

    %filter by length
    lengthMin = 600; % ~150 um
    objDiameter =[props(:).MaxFeretDiameter]';

    obj2del = find(objDiameter<lengthMin);

    BW2del= ismember(L_img,obj2del);
    BW_filt = BW_close;
    BW_filt(BW2del)=0;

    %%fill small holes
    invertedBW = 1- BW_filt;
    areaHoles = 5000;
    BW_clean = uint8(1-bwareaopen(invertedBW, areaHoles))*255;
    figure;
    imshow([segmentedImg,uint8(BW_clean*255),rawImg])


    %%filter by multinucleation. At least 2 nuclei inside.

    L_fibres = bwlabel(BW_clean,8);
    figure;imshow(uint8(L_fibres))
    maxValue = max([L_fibres(:)]);
    cmap = colorcube;
    cmap(1,:)=[0,0,0];
    colormap(cmap)

    %%Skeletonize to quantify branching
    BW_skel = bwskel(imbinarize(BW_clean),'MinBranchLength',lengthMin/2);
    BW_skel = bwmorph(BW_skel, 'spur', 10);


    dil_skel=imdilate(BW_skel, strel('disk',5));
    imshow([[imadjust(rawImg), segmentedImg];[BW_clean,uint8(dil_skel)*255]])

    % figure; imshow(uint8(skel_clean)*255);
    % endPoints = bwmorph(skel_clean, 'endpoints');
    % [y, x] = find(endPoints);
    % hold on
    % % Plot red circles around endpoints
    % viscircles([x, y], repmat(3, length(x), 1), 'Color', 'y', 'LineWidth', 4);

    


end