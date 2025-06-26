// TO HYDE THE WINDOWS
//setBatchMode(true);


// Define output folder
projectDir = "F:/Lab/MAMDC2/";
outputFolder = projectDir + "rawImages/tifs/";
rawMyotubesFolder = outputFolder + "rawMyotubesProjection/";
rawNucleiFolder = outputFolder + "rawNuclei3D/";

// Ensure the directories exist before proceeding
if (!File.exists(outputFolder)) File.makeDirectory(outputFolder);
if (!File.exists(rawMyotubesFolder)) File.makeDirectory(rawMyotubesFolder);
if (!File.exists(rawNucleiFolder)) File.makeDirectory(rawNucleiFolder);


/*// Define the directory
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
		    
		    selectImage("MAX_" + channelMyotubes);
			saveAs("Tiff", rawMyotubesFolder + simplifiedName);
	
			close();

			    
			// SAVE TOPRO CHANNEL 3D
		    selectImage(channelTopro);
			run("8-bit"); //this is simply to remove the green LUT from the 16 bits images
			saveAs("Tiff", rawNucleiFolder + simplifiedName);
			    
			close();
			    
			}
			close(channelMyotubes);
			close(channelTopro);
		    close(imageName);

		}
	}
}
setBatchMode(false);  // Restore normal mode
*/