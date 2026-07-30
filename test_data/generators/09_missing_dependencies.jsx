// Test Case: Missing Dependencies
// Creates a composition that references external footage files.
// Tester will remove/rename some files to simulate missing dependencies.
// Validates: "Continue with missing dependencies" toggle in submitter.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Missing Dependencies");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/09_missing_dependencies");
    var assetsFolder = ensureFolder(outputFolder.fsName.replace(/\\/g, "/") + "/assets");

    // Generate placeholder image files that the comp will reference
    var placeholderNames = [
        "foreground_element.png",
        "overlay_texture.png",
        "background_plate.png"
    ];

    for (var i = 0; i < placeholderNames.length; i++) {
        var placeholderFile = new File(assetsFolder.fsName.replace(/\\/g, "/") + "/" + placeholderNames[i]);
        // We cannot generate real PNG files from ExtendScript, so create text markers
        placeholderFile.open("w");
        placeholderFile.writeln("PLACEHOLDER - Replace with real image file: " + placeholderNames[i]);
        placeholderFile.close();
    }

    // Create the main composition
    var comp = createComp("Missing_Deps_Test", TEST_CONFIG.mediumDuration, TEST_CONFIG.frameRate);
    addSolid(comp, "Background", [0.1, 0.1, 0.1]);
    addText(comp, "Missing Dependencies Test", 60, TEST_CONFIG.colors.white, [comp.width / 2, 150]);
    addText(comp, "See INSTRUCTIONS for setup", 36, [1, 0.7, 0], [comp.width / 2, 300]);

    // Add visible layers for each expected dependency
    for (var j = 0; j < placeholderNames.length; j++) {
        addText(
            comp,
            "Dependency: " + placeholderNames[j],
            28,
            [0.7, 0.7, 0.7],
            [comp.width / 2, 450 + j * 60]
        );
    }

    addAnimatedShape(comp, "BaseAnimation");

    var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/missing_deps_output.mp4";
    addToRenderQueue(comp, outputPath);

    // Instructions
    var instructionsFile = new File(outputFolder.fsName.replace(/\\/g, "/") + "/MISSING_DEPS_INSTRUCTIONS.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Missing Dependencies Test Instructions:");
    instructionsFile.writeln("");
    instructionsFile.writeln("SETUP (requires manual steps):");
    instructionsFile.writeln("1. Replace placeholder files in assets/ with real PNG images");
    instructionsFile.writeln("   (any PNG files will work, e.g., solid colors or gradients)");
    instructionsFile.writeln("2. Open the .aep file in After Effects");
    instructionsFile.writeln("3. Import all 3 PNG files from assets/ into the project");
    instructionsFile.writeln("4. Add them as layers in the 'Missing_Deps_Test' composition");
    instructionsFile.writeln("5. Save the project");
    instructionsFile.writeln("");
    instructionsFile.writeln("TEST A - Missing dependency with 'Ignore' OFF:");
    instructionsFile.writeln("6. Rename or delete 'foreground_element.png' from assets/");
    instructionsFile.writeln("7. Reopen the .aep (AE will show missing footage warning)");
    instructionsFile.writeln("8. In submitter, set 'Ignore Missing Dependencies' to OFF");
    instructionsFile.writeln("9. Submit job - EXPECTED: render FAILS");
    instructionsFile.writeln("");
    instructionsFile.writeln("TEST B - Missing dependency with 'Ignore' ON:");
    instructionsFile.writeln("10. Same state (file still missing)");
    instructionsFile.writeln("11. In submitter, set 'Ignore Missing Dependencies' to ON");
    instructionsFile.writeln("12. Submit job - EXPECTED: render SUCCEEDS (with missing element)");
    instructionsFile.writeln("");
    instructionsFile.writeln("NOTE: Per previous testing, missing PNG causes failure but missing");
    instructionsFile.writeln("MP3 may still succeed. Test both file types if possible.");
    instructionsFile.close();

    var savedPath = saveProject("09_missing_dependencies");
    logMessage("Missing Dependencies test project saved: " + savedPath);

    app.endUndoGroup();
})();
