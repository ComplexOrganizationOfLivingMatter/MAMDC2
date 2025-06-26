// TO HYDE THE WINDOWS
setBatchMode(true);

// Define crop size
cropSize = 2048;
numCrops = 5;

// Define output folder
projectDir = "F:/Lab/MAMDC2/";
outputFolder = projectDir + "trainingDataset/";
rawMyotubesFolder = outputFolder + "rawMyotubes/";
rawNucleiFolder = outputFolder + "rawNuclei/";
targetMyotubesFolder = outputFolder + "targetMyotubes/";
// Ensure the directories exist before proceeding
if (!File.exists(outputFolder)) File.makeDirectory(outputFolder);
if (!File.exists(rawMyotubesFolder)) File.makeDirectory(rawMyotubesFolder);
if (!File.exists(rawNucleiFolder)) File.makeDirectory(rawNucleiFolder);
if (!File.exists(targetMyotubesFolder)) File.makeDirectory(targetMyotubesFolder);

// Define the directory
rootPath = projectDir + "raw images/lifs/DX/";

// Get the list of all files in the directory
list = getFileList(rootPath);

// Print only .lif files
print("LIF files found in: " + rootPath);
for (f = 0; f < lengthOf(list); f++) {
    if (endsWith(list[f], ".lif")) {
        print(list[f]);  // Print file name

		//run("Bio-Formats (Windowless)", "open=["+rootPath+fileName+"]");
		fileName = list[f];
		run("Bio-Formats", "open=["+rootPath+fileName+"] autoscale color_mode=Default open_all_series rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
		
		totalImages = 2;
		
		
		for (nImg = 0; nImg < totalImages; nImg++) {
			
			// Define possible image names
			imageName1 = rootPath + fileName + " - R " + (nImg+1) + "_Merged";
			imageName2 = rootPath + fileName + " - R 1 ("+(nImg+1) +")_Merged";
			
			// Try selecting the first name
			if (isOpen(imageName1)) {
			    imageName = imageName1;
			} else if (isOpen(imageName2)) {
			    imageName =imageName2;
			} else {
			    print("Error: Image not found - " + imageName1 + " or " + imageName2);
			}
			selectImage(imageName);
			run("8-bit");
			run("8-bit"); //this is simply to remove the green LUT from the 16 bits images
			
			run("Split Channels");
			
			channelMyotubes = "C2-" + imageName;
			channelTopro = "C1-" + imageName;
		
			selectImage(channelMyotubes);
			run("8-bit"); //this is simply to remove the green LUT from the 16 bits images
			run("Z Project...", "projection=[Max Intensity]");
			
			// Get image dimensions
			width = getWidth();
			height = getHeight();
		
			
			// Clean the filename by removing unwanted parts
			simplifiedName = replace(fileName, "TILE-12X12-MAMDC2-", "");
		    simplifiedName = replace(simplifiedName, ".lif", "");
		    		    simplifiedName = replace(simplifiedName, " - ", "");
		    simplifiedName = replace(simplifiedName, "_Merged", "");
		    
			
			
			// Store crop positions separately
			cropX = newArray(numCrops);
			cropY = newArray(numCrops);
			
			// Generate random non-overlapping crops
			for (i = 0; i < numCrops; i++) {
			    selectImage("MAX_" + channelMyotubes);
			    
			    isValid = false;
			
			    while (!isValid) {
			        x = floor(random() * (width - cropSize));
			        y = floor(random() * (height - cropSize));
			        isValid = true;
			
			        // Check overlap with previous crops
			        for (j = 0; j < i; j++) {
			            if (abs(x - cropX[j]) < cropSize && abs(y - cropY[j]) < cropSize) {
			                isValid = false;
			                break;
			            }
			        }
			    }
			    
			    // Store valid crop position
			    cropX[i] = x;
			    cropY[i] = y;
			    
			    // Make a selection
			    makeRectangle(x, y, cropSize, cropSize);
			
			    // Duplicate the selection instead of cropping
			    run("Duplicate...", "title=Crop_" + (i + 1));

			
			    // CROP AND PROCESS INITIAL SEGMENTION OF MAX_Z_PROJECTION OF MYOTUBES
			    
			    cropName = rawMyotubesFolder + simplifiedName + "_R" + (nImg+1) + "_crop_" + (i + 1) + "_" + x + "x_" + y +"y.tif";
			    saveAs("Tiff", cropName);
			    
				//homogeneize close pixel values and remove noise
				run("Gaussian Blur...", "sigma=3");
				//segment using Huang threshold
				setAutoThreshold("Huang dark");
				setOption("BlackBackground", true);
				run("Convert to Mask");
				// remove some noise using a median filter
				//run("Median...", "radius=5");
				//fill holes
				run("Fill Holes");
				//remove small objects
				minSizeObjects = 200; 
				run("Analyze Particles...", "size="+minSizeObjects+"-Infinity pixel show=Masks clear");
				run("Invert LUT");
				// Save duplicate
			    cropName = targetMyotubesFolder + simplifiedName + "_R" + (nImg+1) +  "_crop_" + (i + 1) + "_" + x + "x_" + y +"y.tif";
			    saveAs("Tiff", cropName);
			
			    // Close duplicated image
			    close();
				close();
			    
			    // SAVE 3D CROPS OF TOPRO CHANNEL
			    
			    selectImage(channelTopro);
			    // Make a selection
			    makeRectangle(x, y, cropSize, cropSize);
			
			    // Duplicate the selection instead of cropping
			    run("Duplicate...", "duplicate");
			    run("8-bit"); //this is simply to remove the green LUT from the 16 bits images
			    // Save duplicate
			    cropName = rawNucleiFolder + simplifiedName + "_R" + (nImg+1) +  "_crop_" + (i + 1) + "_" + x + "x_" + y +"y.tif";
			    saveAs("Tiff", cropName);
			    
			    close();
			    
			}
			close(channelMyotubes);
			close(channelTopro);
		    close(imageName);
		    close("MAX_C2-" + imageName);
		}
	}
}
setBatchMode(false);  // Restore normal mode