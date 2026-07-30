// Test Case: Timeout
// Creates a very long composition that should exceed a short timeout.
// Validates: job is terminated when timeout is reached.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Timeout");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    // Create a long, heavy comp that takes significant time to render
    var comp = createComp("Timeout_LongRender", 60, TEST_CONFIG.frameRate);

    addSolid(comp, "Background", [0.1, 0, 0]);
    addText(comp, "Timeout Test", 80, TEST_CONFIG.colors.white, [comp.width / 2, 150]);
    addText(comp, "60 second comp - set short timeout", 40, [1, 0.5, 0.5], [comp.width / 2, 300]);

    // Add many animated layers to make rendering slow
    for (var i = 0; i < 20; i++) {
        var shapeLayer = comp.layers.addShape();
        shapeLayer.name = "HeavyShape_" + i;
        var group = shapeLayer.property("Contents").addProperty("ADBE Vector Group");
        var ellipse = group.property("Contents").addProperty("ADBE Vector Shape - Ellipse");
        ellipse.property("Size").setValue([50 + Math.random() * 200, 50 + Math.random() * 200]);
        var fill = group.property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("Color").setValue([Math.random(), Math.random(), Math.random()]);
        var stroke = group.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
        stroke.property("Color").setValue([Math.random(), Math.random(), Math.random()]);
        stroke.property("Stroke Width").setValue(3);
        shapeLayer.property("Position").setValue([
            Math.random() * comp.width,
            Math.random() * comp.height
        ]);
        var rotation = shapeLayer.property("Rotation");
        rotation.setValueAtTime(0, 0);
        rotation.setValueAtTime(comp.duration, 720);
        var opacity = shapeLayer.property("Opacity");
        opacity.setValueAtTime(0, 100);
        opacity.setValueAtTime(comp.duration / 2, 20);
        opacity.setValueAtTime(comp.duration, 100);
    }

    // Also create a short comp for comparison (should finish within timeout)
    var shortComp = createComp("Timeout_ShortRender", 1, TEST_CONFIG.frameRate);
    addSolid(shortComp, "Background", [0, 0.1, 0]);
    addText(shortComp, "Short Comp (1 sec)", 60, TEST_CONFIG.colors.white, [shortComp.width / 2, shortComp.height / 2]);

    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/06_timeout_test");
    addToRenderQueue(comp, outputFolder.fsName.replace(/\\/g, "/") + "/long_render.mp4");
    addToRenderQueue(shortComp, outputFolder.fsName.replace(/\\/g, "/") + "/short_render.mp4");

    var instructionsFile = new File(outputFolder.fsName.replace(/\\/g, "/") + "/TIMEOUT_INSTRUCTIONS.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Timeout Test Instructions:");
    instructionsFile.writeln("");
    instructionsFile.writeln("1. Open the .aep, select 'Timeout_LongRender' composition");
    instructionsFile.writeln("2. In submitter, set timeout to a very short value (e.g., 1 minute)");
    instructionsFile.writeln("3. Submit the job");
    instructionsFile.writeln("4. Verify the job is cut short / killed due to timeout");
    instructionsFile.writeln("");
    instructionsFile.writeln("Comparison test:");
    instructionsFile.writeln("5. Select 'Timeout_ShortRender' (1 second comp)");
    instructionsFile.writeln("6. Set timeout to 5 minutes");
    instructionsFile.writeln("7. Submit - should complete successfully within timeout");
    instructionsFile.close();

    var savedPath = saveProject("06_timeout_test");
    logMessage("Timeout test project saved: " + savedPath);

    app.endUndoGroup();
})();
