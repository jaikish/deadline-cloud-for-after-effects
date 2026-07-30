app.beginUndoGroup("Create Automated Comp");

var randomNum = Math.floor(Math.random() * 10000);

var comp = app.project.items.addComp("Automated Comp " + randomNum, 1920, 1080, 1.0, 10, 30);

var solid = comp.layers.addSolid([0, 0, 0], "Background Solid", 1920, 1080, 1.0, 10);

var textLayer = comp.layers.addText("Automated " + randomNum);
var textProp = textLayer.property("Source Text");
var textDoc = textProp.value;
textDoc.fontSize = 120;
textDoc.fillColor = [1, 1, 1];
textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
textDoc.font = "Arial-BoldMT";
textProp.setValue(textDoc);

textLayer.property("Position").setValue([comp.width / 2, comp.height / 2]);

comp.openInViewer();

var savePath = "C:/Users/jaikish/Projects/deadline-cloud-for-after-effects/output/automated_comp_" + randomNum + ".aep";
var saveFolder = new Folder("C:/Users/jaikish/Projects/deadline-cloud-for-after-effects/output");
if (!saveFolder.exists) {
    saveFolder.create();
}
app.project.save(new File(savePath));

app.endUndoGroup();
