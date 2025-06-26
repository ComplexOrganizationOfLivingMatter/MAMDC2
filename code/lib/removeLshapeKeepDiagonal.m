function skelOut = removeLshapeKeepDiagonal(skelIn)
    skelOut = skelIn;
    branchPts = bwmorph(skelOut, 'branchpoints');
    [by, bx] = find(branchPts);
    numPts = numel(bx);
    
    % Preallocate cell array to collect changes from each iteration
    changes = cell(numPts, 1);
    
    % Define L-shape configurations
    Lshapes = {
        [0 -1; -1 0], [-1 -1]; % up+left
        [0 1; -1 0],  [-1 1];  % up+right
        [0 -1; 1 0],  [1 -1];  % down+left
        [0 1; 1 0],   [1 1];   % down+right
    };

    % Parallel loop
    parfor i = 1:numPts
        x = bx(i);
        y = by(i);
        localChanges = [];

        if x > 1 && x < size(skelIn,2) && y > 1 && y < size(skelIn,1)
            for j = 1:4
                orthoDirs = Lshapes{j,1};
                diagOffset = Lshapes{j,2};

                y1 = y + orthoDirs(1,1); x1 = x + orthoDirs(1,2);
                y2 = y + orthoDirs(2,1); x2 = x + orthoDirs(2,2);
                yd = y + diagOffset(1);  xd = x + diagOffset(2);

                if skelIn(y1,x1) && skelIn(y2,x2)
                    % Create temporary test skeleton
                    testSkel = skelIn;
                    testSkel(y1,x1) = 0;
                    testSkel(y2,x2) = 0;
                    testSkel(yd,xd) = 1;

                    CC_orig = bwconncomp(skelIn);
                    CC_test = bwconncomp(testSkel);

                    if CC_test.NumObjects <= CC_orig.NumObjects
                        % Store changes: [y x newValue]
                        localChanges = [localChanges;
                                        y1 x1 0;
                                        y2 x2 0;
                                        yd xd 1];
                    end
                end
            end
        end
        changes{i} = localChanges;
    end

    % Apply changes sequentially
    for i = 1:numPts
        edits = changes{i};
        for k = 1:size(edits,1)
            skelOut(edits(k,1), edits(k,2)) = edits(k,3);
        end
    end
end
