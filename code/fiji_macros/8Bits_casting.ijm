// TO HYDE THE WINDOWS
setBatchMode(true);


// Define output folder
projectDir = "F:/Lab/MAMDC2/trainingDataset/myotubes/";
outputFolder = projectDir + "curated_8_bits/";

// Ensure the directories exist before proceeding
if (!File.exists(outputFolder)) File.makeDirectory(outputFolder);


// Get the list of all files in the directory
list = getFileList(projectDir + "curatedTarget_1606_Patricia");


for (f = 0; f < lengthOf(list); f++) {
	fileName = list[f];
	open(fileName);
	run("8-bit");
	saveAs("Tiff", outputFolder + fileName);

}
setBatchMode(false);  // Restore normal mode