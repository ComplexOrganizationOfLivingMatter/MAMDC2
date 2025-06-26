function maxLen = maxGeodesicSkeletonLength(skelImage)
    % skelImage: binary skeleton image (logical)

    % Get endpoints
    endpoints = bwmorph(skelImage, 'endpoints');
    [y, x] = find(endpoints);
    if numel(x) < 2
        maxLen = 0;
        warning('Not enough endpoints to compute length.');
        return;
    end

    % Step 1: Pick first endpoint A
    A = [x(1), y(1)];
    maskA = false(size(skelImage));
    maskA(A(2), A(1)) = true;

    % Step 2: Compute geodesic distances from A
    D1 = bwdistgeodesic(skelImage, maskA, 'quasi-euclidean');

    % Step 3: Find endpoint B furthest from A
    D1_endpoints = D1(sub2ind(size(D1), y, x));
    [~, idxB] = max(D1_endpoints);
    B = [x(idxB), y(idxB)];

    % Step 4: Compute distances from B
    maskB = false(size(skelImage));
    maskB(B(2), B(1)) = true;
    D2 = bwdistgeodesic(skelImage, maskB, 'quasi-euclidean');

    % Step 5: Find endpoint C furthest from B
    D2_endpoints = D2(sub2ind(size(D2), y, x));
    maxLen = max(D2_endpoints);
end