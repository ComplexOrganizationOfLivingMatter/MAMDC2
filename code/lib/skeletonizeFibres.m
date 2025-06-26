function BW_skel = skeletonizeFibres(BW_clean, myoFLength)

    %skeletonize and dilate several times to reduce artefacts
    BW_skel = bwskel(logical(BW_clean),'MinBranchLength',myoFLength/2);
    for nIt =1:4
        BW_skel = imdilate(BW_skel, strel('disk',5));
        BW_skel = bwskel(logical(BW_skel),'MinBranchLength',myoFLength/2);
    end    

    % figure; imshow(uint8(BW_skel)*255);
    % endPoints = bwmorph(BW_skel, 'endpoints');
    % [y, x] = find(endPoints);
    % hold on
    % % Plot red circles around endpoints
    % viscircles([x, y], repmat(3, length(x), 1), 'Color', 'y', 'LineWidth', 4);
    % 
    % branchPoints = bwmorph(BW_skel, 'branchpoints');
    % [y, x] = find(branchPoints);
    % % % Plot red circles around endpoints
    % viscircles([x, y], repmat(3, length(x), 1), 'Color', 'r', 'LineWidth', 4);

end