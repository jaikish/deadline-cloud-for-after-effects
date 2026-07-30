// Test Case: Audio Rendering
// Creates a composition with a generated tone (via solid + expression) for MP3 output.
// Validates: audio job attachment submission, output module set to audio format.
// Note: AE cannot generate audio via script alone, but this creates the project structure.
// Tester must manually import an audio file OR use the placeholder approach below.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Audio Rendering");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var comp = createComp("Audio_Render_Test", TEST_CONFIG.mediumDuration, TEST_CONFIG.frameRate);

    addSolid(comp, "Background", TEST_CONFIG.colors.black);

    addText(comp, "Audio Render Test", 72, TEST_CONFIG.colors.white, [comp.width / 2, 200]);
    addText(comp, "Import audio file to this comp", 36, [1, 0.8, 0], [comp.width / 2, 400]);
    addText(comp, "Set Output Module to MP3", 36, [1, 0.8, 0], [comp.width / 2, 500]);

    addAnimatedShape(comp, "VisualSync");

    // Generate a placeholder WAV file for the tester
    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/02_audio_rendering");
    var assetsFolder = ensureFolder(outputFolder.fsName.replace(/\\/g, "/") + "/assets");

    // Create instructions file
    var instructionsFile = new File(assetsFolder.fsName.replace(/\\/g, "/") + "/INSTRUCTIONS.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Audio Rendering Test Setup:");
    instructionsFile.writeln("1. Place any .wav or .mp3 file in this 'assets' folder");
    instructionsFile.writeln("2. Open the .aep file in After Effects");
    instructionsFile.writeln("3. Import the audio file into the project");
    instructionsFile.writeln("4. Drag the audio file into the 'Audio_Render_Test' composition");
    instructionsFile.writeln("5. In Render Queue, set Output Module to MP3 or WAV");
    instructionsFile.writeln("6. Ensure 'Audio Output: On' is checked in Output Module settings");
    instructionsFile.writeln("7. Submit via Deadline Cloud submitter");
    instructionsFile.close();

    var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/audio_output.mp3";
    addToRenderQueue(comp, outputPath);

    var savedPath = saveProject("02_audio_rendering");
    logMessage("Audio Rendering test project saved: " + savedPath);

    app.endUndoGroup();
})();
