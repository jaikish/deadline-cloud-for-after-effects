// Master runner: generates all test data .aep files in sequence.
// Run via: AfterFX.exe -s "$.evalFile('C:/path/to/test_data/run_all.jsx')"

(function() {
    var scriptDir = new File($.fileName).parent;
    var generatorsDir = new Folder(scriptDir.fsName + "/generators");

    if (!generatorsDir.exists) {
        alert("Cannot find generators directory: " + generatorsDir.fsName);
        return;
    }

    var scripts = generatorsDir.getFiles("*.jsx");
    scripts.sort();

    $.writeln("=== After Effects Test Data Generator ===");
    $.writeln("Found " + scripts.length + " generator scripts");
    $.writeln("Output directory: " + scriptDir.fsName + "/output");
    $.writeln("");

    var results = [];
    var startTime = new Date();

    for (var i = 0; i < scripts.length; i++) {
        var scriptFile = scripts[i];
        var scriptName = scriptFile.name;
        $.writeln("[" + (i + 1) + "/" + scripts.length + "] Running: " + scriptName);

        try {
            $.evalFile(scriptFile);
            results.push({ name: scriptName, status: "OK" });
            $.writeln("  -> SUCCESS");
        } catch (e) {
            results.push({ name: scriptName, status: "FAILED", error: e.message });
            $.writeln("  -> FAILED: " + e.message);
        }
        $.writeln("");
    }

    var elapsed = ((new Date()) - startTime) / 1000;

    // Summary
    $.writeln("=== SUMMARY ===");
    $.writeln("Total time: " + elapsed.toFixed(1) + " seconds");
    $.writeln("");

    var passed = 0;
    var failed = 0;
    for (var j = 0; j < results.length; j++) {
        var r = results[j];
        var statusMark = (r.status === "OK") ? "[PASS]" : "[FAIL]";
        $.writeln("  " + statusMark + " " + r.name + (r.error ? " - " + r.error : ""));
        if (r.status === "OK") passed++;
        else failed++;
    }

    $.writeln("");
    $.writeln("Passed: " + passed + "/" + results.length);
    if (failed > 0) $.writeln("Failed: " + failed + "/" + results.length);
    $.writeln("");
    $.writeln("Test data saved to: " + scriptDir.fsName + "/output/");

    // Write results log to file
    var logFile = new File(scriptDir.fsName + "/output/generation_log.txt");
    var outputFolder = new Folder(scriptDir.fsName + "/output");
    if (!outputFolder.exists) outputFolder.create();
    logFile.open("w");
    logFile.writeln("Test Data Generation Log");
    logFile.writeln("Generated: " + new Date().toString());
    logFile.writeln("AE Version: " + app.version);
    logFile.writeln("OS: " + $.os);
    logFile.writeln("Duration: " + elapsed.toFixed(1) + "s");
    logFile.writeln("");
    for (var k = 0; k < results.length; k++) {
        var res = results[k];
        logFile.writeln((res.status === "OK" ? "PASS" : "FAIL") + " | " + res.name + (res.error ? " | " + res.error : ""));
    }
    logFile.close();
})();
