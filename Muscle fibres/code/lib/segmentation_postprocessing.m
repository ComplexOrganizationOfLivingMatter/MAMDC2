function BW_clean = segmentation_postprocessing(segmentedImg, lengthMin)
    % SEGMENTATION_POSTPROCESSING Refines raw segmentation masks through 
    % binarization, morphological filtering, and size-based exclusion.
    %
    % Inputs:
    %   segmentedImg - Raw probability map or grayscale mask from model
    %   lengthMin    - Minimum Max Feret Diameter allowed (pixels)

    %% 1. Binarization
    % Convert to binary using adaptive thresholding to handle local
    % intensity variations. 
    BW = imbinarize(segmentedImg, 'adaptive'); 
    
    %% 2. Morphological Refinement
    % Perform 'closing' (dilation followed by erosion) to bridge small gaps 
    % and smooth the boundaries of the segmented myofibres.
    SE = strel('disk', 5, 8);
    BW_close = imclose(BW, SE); 
    
    %% 3. Object Filtering by Geometric Properties
    % Label connected components and calculate region properties
    L_img = bwlabel(BW_close);
    props = regionprops(L_img, 'MaxFeretDiameter');

    % Extract the maximum Feret diameter (the furthest distance between any two points)
    objDiameter = [props(:).MaxFeretDiameter]';

    % Identify objects that do not meet the minimum length requirement
    obj2del = find(objDiameter < lengthMin);

    % Remove small objects by setting their pixels to background (0)
    BW2del = ismember(L_img, obj2del);
    BW_filt = BW_close;
    BW_filt(BW2del) = 0;

    %% 4. Hole Filling
    % Invert the image to identify background "holes" within the myofibres.
    % Remove background components smaller than 5000 pixels.
    invertedBW = 1 - BW_filt;
    areaHoles = 5000;
    
    % Re-invert to return to original polarity and scale to uint8 [0, 255]
    BW_clean = uint8(1 - bwareaopen(invertedBW, areaHoles)) * 255;

end