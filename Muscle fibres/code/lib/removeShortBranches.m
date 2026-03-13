function skel_pruned_dist = removeShortBranches(BW_skel, threshold)
% Remove skeleton branches shorter than the specified threshold
% Input:
%   BW_skel   - binary skeleton image
%   threshold - minimum branch length (in pixels) to keep
% Output:
%   skel_pruned_dist - pruned skeleton with short branches removed

    % Detect branch and end points
    B = bwmorph(BW_skel, 'branchpoints');
    E = bwmorph(BW_skel, 'endpoints');
    [y, x] = find(E);
    B_loc = find(B);
    Dmask = false(size(BW_skel));

    % Loop over each endpoint
    for k = 1:numel(x)
        % Compute geodesic distances from current endpoint
        D = bwdistgeodesic(BW_skel, x(k), y(k));

        % Find shortest path from endpoint to any branch point
        distanceToBranchPt = min(D(B_loc));

        % If the branch is shorter than the threshold, mark it for deletion
        if distanceToBranchPt < threshold
            Dmask(D < distanceToBranchPt) = true;
        end
    end

    % Remove the marked short branches
    skel_pruned_dist = BW_skel & ~Dmask;
end
