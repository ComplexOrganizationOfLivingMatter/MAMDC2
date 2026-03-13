// TO HYDE THE WINDOWS
setBatchMode(true);


// Define output folder
projectDir = "F:/Lab/MAMDC2/raw images/tifs/";
outputFolder = projectDir + "rawNucleiProjection05/";

// Ensure the directories exist before proceeding
if (!File.exists(outputFolder)) File.makeDirectory(outputFolder);


// Get the list of all files in the directory
list = getFileList(projectDir + "rawNucleiProjection");


for (f = 0; f < lengthOf(list); f++) {
	fileName = list[f];
	open(fileName);
	run("Scale...", "x=0.5 y=0.5 interpolation=Bilinear average create");
	run("8-bit");
	saveAs("Tiff", outputFolder + fileName);

}
setBatchMode(false);  // Restore normal mode