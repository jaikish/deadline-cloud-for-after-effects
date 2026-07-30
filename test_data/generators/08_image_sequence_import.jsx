// Test Case: Image Sequence Import
// Creates a composition that generates an image sequence, then a second composition
// that imports that sequence. Validates: the ENTIRE sequence is submitted as job
// attachments, not just the first frame.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Image Sequence Import");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/08_image_sequence_import");
    var sequenceFolder = ensureFolder(outputFolder.fsName.replace(/\\/g, "/") + "/source_sequence");

    // Step 1: Create a source comp that renders to an image sequence
    var sourceComp = createComp("Source_ImageSeq", 2, TEST_CONFIG.frameRate);
    addSolid(sourceComp, "GradientBG", [0.2, 0.3, 0.5]);

    var frameLabel = comp = sourceComp.layers.addText("Source Frame");
    var frameProp = frameLabel.property("Source Text");
    var frameDoc = frameProp.value;
    frameDoc.fontSize = 100;
    frameDoc.fillColor = [1, 1, 0];
    frameDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
    frameProp.setValue(frameDoc);
    frameLabel.property("Position").setValue([sourceComp.width / 2, sourceComp.height / 2]);
    frameProp.expression = 'text.sourceText = "Source Frame " + Math.floor(time * thisComp.frameRate);';

    // Render queue item for generating the source sequence
    var seqOutputPath = sequenceFolder.fsName.replace(/\\/g, "/") + "/src_[#####].png";
    addToRenderQueue(sourceComp, seqOutputPath);

    // Step 2: Create a consumer comp that will import the rendered sequence
    var consumerComp = createComp("Consumer_UsesImageSeq", 3, TEST_CONFIG.frameRate);
    addSolid(consumerComp, "Background", TEST_CONFIG.colors.black);
    addText(consumerComp, "Image Sequence Consumer", 60, TEST_CONFIG.colors.white, [consumerComp.width / 2, 150]);
    addText(consumerComp, "After rendering source, import sequence here", 30, [1, 0.8, 0], [consumerComp.width / 2, consumerComp.height - 100]);

    var consumerOutputPath = outputFolder.fsName.replace(/\\/g, "/") + "/consumer_output.mp4";
    addToRenderQueue(consumerComp, consumerOutputPath);

    // Instructions
    var instructionsFile = new File(outputFolder.fsName.replace(/\\/g, "/") + "/IMAGE_SEQ_INSTRUCTIONS.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Image Sequence Import Test - Two-step process:");
    instructionsFile.writeln("");
    instructionsFile.writeln("STEP 1: Generate the source image sequence");
    instructionsFile.writeln("  - Render 'Source_ImageSeq' locally (or submit to farm)");
    instructionsFile.writeln("  - This creates PNG files in source_sequence/ folder");
    instructionsFile.writeln("");
    instructionsFile.writeln("STEP 2: Import sequence into consumer comp");
    instructionsFile.writeln("  - File > Import > File > select first frame of source_sequence/");
    instructionsFile.writeln("  - Check 'JPEG/PNG Sequence' checkbox in import dialog");
    instructionsFile.writeln("  - Drag imported sequence into 'Consumer_UsesImageSeq' comp");
    instructionsFile.writeln("  - Submit 'Consumer_UsesImageSeq' via Deadline Cloud");
    instructionsFile.writeln("");
    instructionsFile.writeln("VERIFY:");
    instructionsFile.writeln("  - In job attachments, ALL frames of the sequence should appear");
    instructionsFile.writeln("  - NOT just the first frame (e.g., src_00000.png)");
    instructionsFile.writeln("  - The rendered output video should show the sequence playing");
    instructionsFile.close();

    var savedPath = saveProject("08_image_sequence_import");
    logMessage("Image Sequence Import test project saved: " + savedPath);

    app.endUndoGroup();
})();
