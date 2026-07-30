// Test Case: Custom Fonts
// Creates a composition with text using various font types to test font detection
// and job attachment submission.
// Validates: font files are found and submitted as job attachments.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Custom Fonts");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var comp = createComp("Custom_Fonts_Test", TEST_CONFIG.mediumDuration, TEST_CONFIG.frameRate);
    addSolid(comp, "Background", [0.05, 0.05, 0.1]);

    addText(comp, "Font Coverage Test", 60, TEST_CONFIG.colors.white, [comp.width / 2, 100]);

    // Common system fonts that should be findable on both platforms
    var fontTests = [
        { font: "ArialMT", label: "Arial (System)", y: 220 },
        { font: "TimesNewRomanPSMT", label: "Times New Roman (System)", y: 320 },
        { font: "Courier", label: "Courier (System)", y: 420 },
        { font: "Georgia", label: "Georgia (System)", y: 520 },
        { font: "Verdana", label: "Verdana (System)", y: 620 }
    ];

    // Platform-specific fonts to test detection across OS
    var isWindows = ($.os.indexOf("Windows") !== -1);
    if (isWindows) {
        fontTests.push({ font: "Calibri", label: "Calibri (Windows)", y: 720 });
        fontTests.push({ font: "SegoeUI", label: "Segoe UI (Windows)", y: 820 });
    } else {
        fontTests.push({ font: "Helvetica", label: "Helvetica (macOS)", y: 720 });
        fontTests.push({ font: "SFProDisplay-Regular", label: "SF Pro (macOS)", y: 820 });
    }

    for (var i = 0; i < fontTests.length; i++) {
        var ft = fontTests[i];
        try {
            addTextWithFont(comp, ft.label, ft.font, 36, TEST_CONFIG.colors.white, [comp.width / 2, ft.y]);
        } catch (e) {
            // Font not available - add with default font and note it
            addText(comp, ft.label + " [NOT FOUND]", 36, [1, 0.3, 0.3], [comp.width / 2, ft.y]);
        }
    }

    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/10_custom_fonts");
    var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/font_test_output.mp4";
    addToRenderQueue(comp, outputPath);

    // Create a second comp specifically for testing custom/downloaded fonts
    var customFontComp = createComp("Custom_Downloaded_Fonts", TEST_CONFIG.mediumDuration, TEST_CONFIG.frameRate);
    addSolid(customFontComp, "Background", [0.1, 0.05, 0.05]);
    addText(customFontComp, "Custom Font Test", 60, TEST_CONFIG.colors.white, [customFontComp.width / 2, 100]);
    addText(customFontComp, "Add custom fonts below manually:", 30, [1, 0.8, 0], [customFontComp.width / 2, 200]);

    // Placeholder text layers where tester can change font to custom ones
    var customFontSlots = [
        { label: "Slot 1: Amazon Ember (install separately)", y: 350 },
        { label: "Slot 2: Adobe Creative Cloud Font", y: 450 },
        { label: "Slot 3: Any .ttc font (e.g., Avenir)", y: 550 },
        { label: "Slot 4: Font then removed from system", y: 650 }
    ];

    for (var k = 0; k < customFontSlots.length; k++) {
        addText(
            customFontComp,
            customFontSlots[k].label,
            32,
            [0.8, 0.8, 0.8],
            [customFontComp.width / 2, customFontSlots[k].y]
        );
    }

    var customOutputPath = outputFolder.fsName.replace(/\\/g, "/") + "/custom_font_output.mp4";
    addToRenderQueue(customFontComp, customOutputPath);

    // Instructions
    var instructionsFile = new File(outputFolder.fsName.replace(/\\/g, "/") + "/FONT_INSTRUCTIONS.txt");
    instructionsFile.open("w");
    instructionsFile.writeln("Custom Fonts Test Instructions:");
    instructionsFile.writeln("");
    instructionsFile.writeln("COMP 1: Custom_Fonts_Test (automated system fonts)");
    instructionsFile.writeln("  - Submit as-is. Verify all font files appear in job attachments.");
    instructionsFile.writeln("  - Verify rendered output uses correct fonts.");
    instructionsFile.writeln("");
    instructionsFile.writeln("COMP 2: Custom_Downloaded_Fonts (manual setup required)");
    instructionsFile.writeln("  - Install Amazon Ember font, change Slot 1 text to use it");
    instructionsFile.writeln("  - Activate an Adobe Creative Cloud font, use it for Slot 2");
    instructionsFile.writeln("  - Use a .ttc font (e.g., Avenir on Mac) for Slot 3");
    instructionsFile.writeln("  - For Slot 4: set a font, save, then remove font from system");
    instructionsFile.writeln("    (expect error message in submitter about missing font)");
    instructionsFile.writeln("");
    instructionsFile.writeln("VERIFY:");
    instructionsFile.writeln("  - Job attachments list should include font files (.ttf, .otf)");
    instructionsFile.writeln("  - .ttc fonts should produce an error/warning message");
    instructionsFile.writeln("  - Missing fonts should produce an error/warning message");
    instructionsFile.writeln("  - Rendered output should use the correct custom fonts");
    instructionsFile.close();

    var savedPath = saveProject("10_custom_fonts");
    logMessage("Custom Fonts test project saved: " + savedPath);

    app.endUndoGroup();
})();
