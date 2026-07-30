// Test Case: Multi-Frame Rendering (MFR)
// Creates a composition with settings suitable for MFR testing.
// Validates: MFR parameters are passed in aerender CLI call, settings persist per-comp.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Multi-Frame Rendering");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    // Create multiple comps to test MFR with different settings
    var configs = [
        { name: "MFR_Enabled_50pct", mfrNote: "MFR ON, 50% CPU" },
        { name: "MFR_Enabled_100pct", mfrNote: "MFR ON, 100% CPU" },
        { name: "MFR_Disabled", mfrNote: "MFR OFF" }
    ];

    for (var i = 0; i < configs.length; i++) {
        var cfg = configs[i];
        var comp = createComp(cfg.name, TEST_CONFIG.mediumDuration, TEST_CONFIG.frameRate);

        addSolid(comp, "Background", [0.05, 0.05, 0.15]);

        addText(comp, cfg.name, 60, TEST_CONFIG.colors.white, [comp.width / 2, 200]);
        addText(comp, cfg.mfrNote, 40, [0.5, 1, 0.5], [comp.width / 2, 350]);

        // Add computationally intensive layers to benefit from MFR
        for (var j = 0; j < 5; j++) {
            var shapeLayer = comp.layers.addShape();
            shapeLayer.name = "Shape_" + j;
            var group = shapeLayer.property("Contents").addProperty("ADBE Vector Group");
            var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
            ellipse.property("Size").setValue([100 + j * 50, 100 + j * 50]);
            var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
            fill.property("Color").setValue([Math.random(), Math.random(), Math.random()]);
            shapeLayer.property("Position").setValue([
                200 + j * 350,
                comp.height / 2 + 150
            ]);
            // Animate rotation
            var rotation = shapeLayer.property("Rotation");
            rotation.setValueAtTime(0, 0);
            rotation.setValueAtTime(comp.duration, 360 * (j + 1));
        }

        var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/05_multi_frame_rendering");
        var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/" + cfg.name + ".mp4";
        addToRenderQueue(comp, outputPath);
    }

    // Write instructions for setting MFR in submitter
    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/05_multi_frame_rendering");
    var instructionsFile = new File(outputFolder.fsName.replace(/\\/g, "/") + "/MFR_INSTRUCTIONS.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Multi-Frame Rendering Test Instructions:");
    instructionsFile.writeln("");
    instructionsFile.writeln("For each composition, set these values in the Deadline Cloud submitter:");
    instructionsFile.writeln("");
    instructionsFile.writeln("1. MFR_Enabled_50pct:");
    instructionsFile.writeln("   - Multi-Frame Rendering: ON");
    instructionsFile.writeln("   - Max CPU Usage Percentage: 50");
    instructionsFile.writeln("");
    instructionsFile.writeln("2. MFR_Enabled_100pct:");
    instructionsFile.writeln("   - Multi-Frame Rendering: ON");
    instructionsFile.writeln("   - Max CPU Usage Percentage: 100");
    instructionsFile.writeln("");
    instructionsFile.writeln("3. MFR_Disabled:");
    instructionsFile.writeln("   - Multi-Frame Rendering: OFF");
    instructionsFile.writeln("");
    instructionsFile.writeln("Verify in Deadline Cloud Monitor job logs that aerender CLI call");
    instructionsFile.writeln("includes -mfr ENABLED -mfr_max_cpu_usage <value> for MFR comps.");
    instructionsFile.close();

    var savedPath = saveProject("05_multi_frame_rendering");
    logMessage("Multi-Frame Rendering test project saved: " + savedPath);

    app.endUndoGroup();
})();
