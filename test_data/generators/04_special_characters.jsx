// Test Case: Special Characters in Naming
// Creates compositions with special characters in names: accents, symbols, unicode.
// Validates: submitter handles special chars in comp names and file paths.

#include "../config.jsx"

(function() {
    app.beginUndoGroup("Test: Special Characters");

    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.newProject();

    var testNames = [
        "Comp_With_Tilde_ñ",
        "Comp_Plus+Equals=",
        "Comp_Dash-Underscore_",
        "Comp_Spaces In Name",
        "Comp_Parentheses(test)",
        "Comp_Brackets[test]",
        "Comp_Ampersand&Hash#",
        "Comp_Unicode_éèêë"
    ];

    for (var i = 0; i < testNames.length; i++) {
        var compName = testNames[i];
        var comp = createComp(compName, TEST_CONFIG.shortDuration, TEST_CONFIG.frameRate);

        addSolid(comp, "BG_" + i, TEST_CONFIG.colors.black);
        addText(comp, compName, 48, TEST_CONFIG.colors.white, [comp.width / 2, comp.height / 2 - 50]);
        addText(comp, "Test " + (i + 1) + " of " + testNames.length, 36, TEST_CONFIG.colors.green, [comp.width / 2, comp.height / 2 + 80]);

        var outputFolder = ensureFolder(TEST_CONFIG.outputRoot + "/04_special_characters");
        var safeFileName = "output_" + (i + 1) + ".mp4";
        var outputPath = outputFolder.fsName.replace(/\\/g, "/") + "/" + safeFileName;
        addToRenderQueue(comp, outputPath);
    }

    var savedPath = saveProject("04_special_characters");
    logMessage("Special Characters test project saved: " + savedPath);

    app.endUndoGroup();
})();
