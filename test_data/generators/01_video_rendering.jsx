// Test Case: Video Rendering
// Creates a composition suitable for H.264 video output with animated content.
// Validates: basic video submission, job attachments, render queue output module settings.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Video Rendering");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var comp = createComp("Video_Render_Test", TEST_CONFIG.mediumDuration, TEST_CONFIG.frameRate);

    addSolid(comp, "Background", TEST_CONFIG.colors.black);

    addText(comp, "Video Render Test", 72, TEST_CONFIG.colors.white, [comp.width / 2, 200]);

    addAnimatedShape(comp, "MovingBox");

    generateColorBars(comp);

    var labelLayer = addText(comp, "Frame: [time]", 36, TEST_CONFIG.colors.green, [comp.width / 2, comp.height - 100]);

    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/01_video_rendering");
    var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/video_output.mp4";
    addToRenderQueue(comp, outputPath);

    var savedPath = saveProject("01_video_rendering");
    logMessage("Video Rendering test project saved: " + savedPath);

    app.endUndoGroup();
})();
