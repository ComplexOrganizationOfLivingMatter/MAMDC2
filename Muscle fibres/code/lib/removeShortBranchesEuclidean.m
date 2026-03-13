function skel_pruned = removeShortBranchesEuclidean(BW_skel, distThreshold)
    % Find branchpoints and endpoints
    B = bwmorph(BW_skel, 'branchpoints');
    E = bwmorph(BW_skel, 'endpoints');
    [y, x] = find(E);
    [by, bx] = find(B);

    Dmask = false(size(BW_skel));

    % Preallocate masks for each endpoint
    masks = false([size(BW_skel), numel(x)]);
    
    parfor k = 1:numel(x)
        % Coordinates of endpoint
        ex = x(k);
        ey = y(k);

        % Euclidean distances from this endpoint to all branchpoints
        distances = sqrt((bx - ex).^2 + (by - ey).^2);
        minDist = min(distances);

        % If minDist > threshold, skip pruning for this endpoint
        if minDist > distThreshold
            continue
        end

        % Mark pixels within minDist radius from endpoint
        [X, Y] = meshgrid(1:size(BW_skel,2), 1:size(BW_skel,1));
        distMat = sqrt((X - ex).^2 + (Y - ey).^2);

        % Include pixels inside the minDist circle
        masks(:,:,k) = distMat < minDist;
    end

    % Combine all masks from endpoints
    combinedMask = any(masks, 3);

    % Prune pixels inside combinedMask
    skel_pruned = BW_skel & ~combinedMask;
end
