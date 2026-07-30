// Test Case: Image Chunking
// Creates a 300-frame composition for JPEG sequence output.
// Validates: Frames per Task chunking at values 1, 100, 299, 300.
// Each frame has unique visual content (frame counter) to verify chunk boundaries.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Image Chunking");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    // 300 frames at 30fps = 10 seconds
    var comp = createComp("Image_Chunk_300frames", 10, 30);

    addSolid(comp, "Background", [0.1, 0.1, 0.2]);

    addText(comp, "Image Chunking Test", 60, TEST_CONFIG.colors.white, [comp.width / 2, 150]);

    // Add a text layer with frame number expression for visual verification
    var frameCounter = comp.layers.addText("Frame 0");
    var counterProp = frameCounter.property("Source Text");
    var counterDoc = counterProp.value;
    counterDoc.fontSize = 120;
    counterDoc.fillColor = [0, 1, 0.5];
    counterDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
    counterProp.setValue(counterDoc);
    frameCounter.property("Position").setValue([comp.width / 2, comp.height / 2]);

    // Expression to show current frame number
    counterProp.expression = 'text.sourceText = "Frame " + Math.floor(time * thisComp.frameRate);';

    // Add animated element to ensure each frame is unique
    var shape = addAnimatedShape(comp, "ProgressIndicator");

    // Add a progress bar via shape layer
    var progressLayer = comp.layers.addShape();
    progressLayer.name = "ProgressBar";
    var progressGroup = progressLayer.property("Contents").addProperty("ADBE Vector Group");
    var progressRect = progressGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
    progressRect.property("Size").setValue([1800, 40]);
    var progressFill = progressGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
    progressFill.property("Color").setValue([0, 0.8, 0.4]);
    progressLayer.property("Position").setValue([comp.width / 2, comp.height - 80]);

    // Animate scale X from 0 to 100 to show progress
    var scaleX = progressLayer.property("Scale");
    scaleX.setValueAtTime(0, [0, 100]);
    scaleX.setValueAtTime(comp.duration, [100, 100]);

    // Set up render queue for JPEG sequence
    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/03_image_chunking");
    var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/frame_[#####].jpg";
    addToRenderQueue(comp, outputPath);

    // Create test instructions for chunk sizes
    var instructionsFile = new File(outputFolder.fsName.replace(/\\/g, "/") + "/CHUNK_TEST_VALUES.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Image Chunking Test - Frames Per Task values to test:");
    instructionsFile.writeln("");
    instructionsFile.writeln("Total frames: 300 (frame 0 to 299)");
    instructionsFile.writeln("");
    instructionsFile.writeln("Test 1: Frames Per Task = 1   -> 300 tasks (1 frame each)");
    instructionsFile.writeln("Test 2: Frames Per Task = 100 -> 3 tasks (100 frames each)");
    instructionsFile.writeln("Test 3: Frames Per Task = 299 -> 2 tasks (299 + 1 frames)");
    instructionsFile.writeln("Test 4: Frames Per Task = 300 -> 1 task (all 300 frames)");
    instructionsFile.writeln("");
    instructionsFile.writeln("Verify: all 300 output JPEG files exist with correct frame numbers");
    instructionsFile.close();

    var savedPath = saveProject("03_image_chunking");
    logMessage("Image Chunking test project saved: " + savedPath);

    app.endUndoGroup();
})();
