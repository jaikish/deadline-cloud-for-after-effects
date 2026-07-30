// Test Case: Multi-Composition Submission
// Creates multiple distinct compositions in one project, all added to render queue.
// Validates: selecting multiple comps in submitter and submitting them together.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Multicomp");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var compConfigs = [
        { name: "MultiComp_RedScene", color: [0.8, 0.1, 0.1], text: "Red Scene", duration: 3 },
        { name: "MultiComp_GreenScene", color: [0.1, 0.8, 0.1], text: "Green Scene", duration: 5 },
        { name: "MultiComp_BlueScene", color: [0.1, 0.1, 0.8], text: "Blue Scene", duration: 4 },
        { name: "MultiComp_YellowScene", color: [0.8, 0.8, 0.1], text: "Yellow Scene", duration: 6 },
        { name: "MultiComp_PurpleScene", color: [0.6, 0.1, 0.8], text: "Purple Scene", duration: 2 }
    ];

    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/07_multicomp");

    for (var i = 0; i < compConfigs.length; i++) {
        var cfg = compConfigs[i];
        var comp = createComp(cfg.name, cfg.duration, TEST_CONFIG.frameRate);

        addSolid(comp, "BG_" + cfg.name, cfg.color);

        addText(comp, cfg.text, 80, TEST_CONFIG.colors.white, [comp.width / 2, comp.height / 2 - 80]);
        addText(comp, "Comp " + (i + 1) + " of " + compConfigs.length, 40, [0.9, 0.9, 0.9], [comp.width / 2, comp.height / 2 + 60]);
        addText(comp, cfg.duration + " seconds @ " + TEST_CONFIG.frameRate + "fps", 30, [0.7, 0.7, 0.7], [comp.width / 2, comp.height / 2 + 130]);

        addAnimatedShape(comp, "Anim_" + i);

        var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/" + cfg.name + ".mp4";
        addToRenderQueue(comp, outputPath);
    }

    var savedPath = saveProject("07_multicomp");
    logMessage("Multicomp test project saved: " + savedPath);

    app.endUndoGroup();
})();
