var TEST_CONFIG = {
    outputRoot: (function() {
        var scriptFile = new File($.fileName);
        return scriptFile.parent.fsName.replace(/\\/g, "/") + "/output";
    })(),

    compWidth: 1920,
    compHeight: 1080,
    frameRate: 30,
    pixelAspect: 1.0,

    shortDuration: 2,
    mediumDuration: 5,
    longDuration: 10,

    colors: {
        black: [0, 0, 0],
        white: [1, 1, 1],
        red: [1, 0, 0],
        green: [0, 1, 0],
        blue: [0, 0, 1],
        gray: [0.5, 0.5, 0.5]
    }
};

function ensureFolder(path) {
    var folder = new Folder(path);
    if (!folder.exists) {
        folder.create();
    }
    return folder;
}

function saveProject(name) {
    var outputFolder = ensureFolder(TEST_CONFIG.outputRoot);
    var testFolder = ensureFolder(outputFolder.fsName.replace(/\\/g, "/") + "/" + name);
    var savePath = testFolder.fsName.replace(/\\/g, "/") + "/" + name + ".aep";
    app.project.save(new File(savePath));
    return savePath;
}

function closeProject() {
    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
}

function createComp(name, duration, frameRate) {
    duration = duration || TEST_CONFIG.mediumDuration;
    frameRate = frameRate || TEST_CONFIG.frameRate;
    return app.project.items.addComp(
        name,
        TEST_CONFIG.compWidth,
        TEST_CONFIG.compHeight,
        TEST_CONFIG.pixelAspect,
        duration,
        frameRate
    );
}

function addSolid(comp, name, color, duration) {
    color = color || TEST_CONFIG.colors.black;
    duration = duration || comp.duration;
    return comp.layers.addSolid(
        color,
        name,
        TEST_CONFIG.compWidth,
        TEST_CONFIG.compHeight,
        TEST_CONFIG.pixelAspect,
        duration
    );
}

function addText(comp, text, fontSize, color, position) {
    fontSize = fontSize || 80;
    color = color || TEST_CONFIG.colors.white;
    position = position || [comp.width / 2, comp.height / 2];

    var textLayer = comp.layers.addText(text);
    var textProp = textLayer.property("Source Text");
    var textDoc = textProp.value;
    textDoc.fontSize = fontSize;
    textDoc.fillColor = color;
    textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
    textProp.setValue(textDoc);
    textLayer.property("Position").setValue(position);
    return textLayer;
}

function addTextWithFont(comp, text, fontName, fontSize, color, position) {
    fontSize = fontSize || 80;
    color = color || TEST_CONFIG.colors.white;
    position = position || [comp.width / 2, comp.height / 2];

    var textLayer = comp.layers.addText(text);
    var textProp = textLayer.property("Source Text");
    var textDoc = textProp.value;
    textDoc.fontSize = fontSize;
    textDoc.fillColor = color;
    textDoc.font = fontName;
    textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
    textProp.setValue(textDoc);
    textLayer.property("Position").setValue(position);
    return textLayer;
}

function addToRenderQueue(comp, outputPath, outputModule) {
    var rqi = app.project.renderQueue.items.add(comp);
    if (outputPath) {
        rqi.outputModule(1).file = new File(outputPath);
    }
    if (outputModule) {
        rqi.outputModule(1).applyTemplate(outputModule);
    }
    return rqi;
}

function generateColorBars(comp) {
    var barColors = [
        [1, 1, 1],
        [1, 1, 0],
        [0, 1, 1],
        [0, 1, 0],
        [1, 0, 1],
        [1, 0, 0],
        [0, 0, 1]
    ];
    var barWidth = Math.floor(comp.width / barColors.length);

    for (var i = 0; i < barColors.length; i++) {
        var solid = comp.layers.addSolid(
            barColors[i],
            "Bar_" + i,
            barWidth,
            comp.height,
            TEST_CONFIG.pixelAspect,
            comp.duration
        );
        solid.property("Position").setValue([barWidth * i + barWidth / 2, comp.height / 2]);
    }
}

function addAnimatedShape(comp, name) {
    var shapeLayer = comp.layers.addShape();
    shapeLayer.name = name || "AnimatedShape";

    var shapeGroup = shapeLayer.property("Contents").addProperty("ADBE Vector Group");
    var rect = shapeGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
    rect.property("Size").setValue([200, 200]);

    var fill = shapeGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
    fill.property("Color").setValue([1, 0.5, 0]);

    var pos = shapeLayer.property("Position");
    pos.setValueAtTime(0, [100, comp.height / 2]);
    pos.setValueAtTime(comp.duration, [comp.width - 100, comp.height / 2]);

    return shapeLayer;
}

function logMessage(msg) {
    $.writeln("[TestDataGen] " + msg);
}
