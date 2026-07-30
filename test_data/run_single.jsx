// Run a single test data generator by index.
// Usage: AfterFX.exe -s "var TEST_INDEX=3; $.evalFile('C:/path/to/test_data/run_single.jsx')"
// TEST_INDEX corresponds to the script number (01-10).

(function() {
    if (typeof TEST_INDEX === "undefined") {
        alert("Set TEST_INDEX before running. Example:\nvar TEST_INDEX=1; $.evalFile(...)");
        return;
    }

    var scriptDir = new File($.fileName).parent;
    var generatorsDir = new Folder(scriptDir.fsName + "/generators");
    var scripts = generatorsDir.getFiles("*.jsx");
    scripts.sort();

    var prefix = (TEST_INDEX < 10 ? "0" : "") + TEST_INDEX;

    var targetScript = null;
    for (var i = 0; i < scripts.length; i++) {
        if (scripts[i].name.indexOf(prefix + "_") === 0) {
            targetScript = scripts[i];
            break;
        }
    }

    if (!targetScript) {
        alert("No generator found for TEST_INDEX=" + TEST_INDEX + " (prefix: " + prefix + ")");
        return;
    }

    $.writeln("Running single generator: " + targetScript.name);
    $.evalFile(targetScript);
    $.writeln("Done: " + targetScript.name);
})();
