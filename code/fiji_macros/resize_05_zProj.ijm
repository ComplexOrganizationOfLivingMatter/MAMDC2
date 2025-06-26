// TO HYDE THE WINDOWS
setBatchMode(true);


// Define output folder
projectDir = "F:/Lab/MAMDC2/trainingDataset/nuclei/";
outputFolder = projectDir + "rawNuclei_zProjRz05/";

// Ensure the directories exist before proceeding
if (!File.exists(outputFolder)) File.makeDirectory(outputFolder);


// Get the list of all files in the directory
list = getFileList(projectDir + "rawNuclei");


for (f = 0; f < lengthOf(list); f++) {
	fileName = list[f];
	print(fileName);
	open(projectDir + "rawNuclei/" + fileName);
	run("Z Project...", "projection=[Max Intensity]");
	run("Scale...", "x=0.5 y=0.5 interpolation=Bilinear average create");
	run("8-bit");
	saveAs("Tiff", outputFolder + fileName);

}
setBatchMode(false);  // Restore normal mode