// ===== building_generator.js =====
// QCAD Script zur automatisierten Erstellung von 2-Geschoss-Gebäudeplänen
// Aufruf: qcad -autostart building_generator.js --width=10000 --depth=8000 --floors=2

include("scripts/simple.js");

// Hilfe-Funktion
function printHelp() {
  print("Usage: qcad -autostart building_generator.js [OPTIONS]");
  print();
  print("Optionen:");
  print(" --width=SIZE Gebäudebreite in Einheiten (default: 10000)");
  print(" --depth=SIZE Gebäudetiefe in Einheiten (default: 8000)");
  print(" --floors=NUM Anzahl der Geschosse (default: 2)");
  print(" --output=FILE Output DXF Dateiname (default: auto)");
  print(" --rooms=LAYOUT Raumlayout: 'simple' oder 'complex' (default: simple)");
  print(" -h, --help Diese Hilfe anzeigen");
  print();
}

// Standardwerte
var buildingParams = {
  width: 10000,
  depth: 8000,
  floors: 2,
  outputFile: "",
  roomLayout: "simple"
};

// Parameter aus Kommandozeile parsen (KORREKT)
function parseArguments() {
  // Zugriff auf globale 'arguments' Variable (nicht getArguments())
  for (var i = 0; i < arguments.length; i++) {
    var arg = arguments[i];
    
    if (arg === "-h" || arg === "--help") {
      printHelp();
      return false;
    }
    
    if (arg.indexOf("--width=") === 0) {
      buildingParams.width = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--depth=") === 0) {
      buildingParams.depth = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--floors=") === 0) {
      buildingParams.floors = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--output=") === 0) {
      buildingParams.outputFile = arg.split("=")[1];
    } else if (arg.indexOf("--rooms=") === 0) {
      buildingParams.roomLayout = arg.split("=")[1];
    }
  }
  
  return true;
}

// Rechteck (Außenwände) zeichnen
function drawRectangle(doc, operation, x, y, width, height, layerId) {
  var line1 = new RLineEntity(doc, new RLineData(
    new RVector(x, y),
    new RVector(x + width, y)
  ));
  line1.setLayerId(layerId);
  operation.addObject(line1, false);
  
  var line2 = new RLineEntity(doc, new RLineData(
    new RVector(x + width, y),
    new RVector(x + width, y + height)
  ));
  line2.setLayerId(layerId);
  operation.addObject(line2, false);
  
  var line3 = new RLineEntity(doc, new RLineData(
    new RVector(x + width, y + height),
    new RVector(x, y + height)
  ));
  line3.setLayerId(layerId);
  operation.addObject(line3, false);
  
  var line4 = new RLineEntity(doc, new RLineData(
    new RVector(x, y + height),
    new RVector(x, y)
  ));
  line4.setLayerId(layerId);
  operation.addObject(line4, false);
}

// Innenwände zeichnen (einfaches Layout)
function drawInternalWalls(doc, operation, x, y, width, height, layerId) {
  var midX = x + width / 2;
  var midY = y + height / 2;
  
  var vLine = new RLineEntity(doc, new RLineData(
    new RVector(midX, y),
    new RVector(midX, y + height)
  ));
  vLine.setLayerId(layerId);
  operation.addObject(vLine, false);
  
  var hLine = new RLineEntity(doc, new RLineData(
    new RVector(x, midY),
    new RVector(x + width, midY)
  ));
  hLine.setLayerId(layerId);
  operation.addObject(hLine, false);
}

// Türen einfügen
function addDoor(doc, operation, x, y, width, layerId) {
  var door = new RLineEntity(doc, new RLineData(
    new RVector(x, y),
    new RVector(x + width, y)
  ));
  door.setLayerId(layerId);
  operation.addObject(door, false);
}

// Fenster einfügen
function addWindow(doc, operation, x, y, width, layerId) {
  var wh = 200;
  for (var i = 0; i < 3; i++) {
    var wx = x + (i * (width / 3));
    var window = new RLineEntity(doc, new RLineData(
      new RVector(wx, y),
      new RVector(wx, y + wh)
    ));
    window.setLayerId(layerId);
    operation.addObject(window, false);
  }
}

// Text-Label hinzufügen
function addTextLabel(doc, operation, text, x, y, height, layerId) {
  var textData = new RTextData();
  textData.setText(text);
  textData.setAlignmentPoint(new RVector(x, y));
  textData.setTextHeight(height);
  textData.setHAlign(RS.HAlignCenter);
  textData.setVAlign(RS.VAlignMiddle);
  var textEntity = new RTextEntity(doc, textData);
  textEntity.setLayerId(layerId);
  operation.addObject(textEntity, false);
}

// Layer erstellen
function createLayer(doc, operation, name, colorCode) {
  var color = new RColor();
  color.setRed(colorCode[0]);
  color.setGreen(colorCode[1]);
  color.setBlue(colorCode[2]);
  var layer = new RLayer(doc, name, false, false, color, RLineweight.Weight000);
  operation.addObject(layer, false);
  return layer.getId();
}

// Komplettes Geschoss zeichnen
function drawFloor(doc, di, floorNumber, startY, buildingWidth, buildingDepth) {
  var operation = new RAddObjectsOperation();
  var layerName = "Floor_" + floorNumber;
  var wallsLayer = createLayer(doc, operation, layerName + "_Walls", [0, 0, 0]);
  var doorsLayer = createLayer(doc, operation, layerName + "_Doors", [255, 0, 0]);
  var windowsLayer = createLayer(doc, operation, layerName + "_Windows", [0, 100, 255]);
  var labelsLayer = createLayer(doc, operation, layerName + "_Labels", [255, 255, 0]);
  
  drawRectangle(doc, operation, 0, startY, buildingWidth, buildingDepth, wallsLayer);
  drawInternalWalls(doc, operation, 0, startY, buildingWidth, buildingDepth, wallsLayer);
  
  addWindow(doc, operation, buildingWidth - 100, startY + 1000, 800, windowsLayer);
  addWindow(doc, operation, buildingWidth - 100, startY + 4000, 800, windowsLayer);
  addDoor(doc, operation, buildingWidth / 2 - 500, startY, 1000, doorsLayer);
  
  var labelY = startY + buildingDepth / 2;
  addTextLabel(doc, operation, "Floor " + floorNumber,
    buildingWidth / 4, labelY, 300, labelsLayer);
  addTextLabel(doc, operation, "Room A",
    buildingWidth / 4, labelY - 500, 200, labelsLayer);
  addTextLabel(doc, operation, "Room B",
    (buildingWidth * 3) / 4, labelY - 500, 200, labelsLayer);
  
  di.applyOperation(operation);
}

// Hauptfunktion
function main() {
  if (!parseArguments()) {
    return;
  }
  
  print("=== Gebäude-Generator startet ===");
  print("Breite: " + buildingParams.width);
  print("Tiefe: " + buildingParams.depth);
  print("Geschosse: " + buildingParams.floors);
  
  try {
    var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
    var di = new RDocumentInterface(doc);
    
    for (var floor = 1; floor <= buildingParams.floors; floor++) {
      var startY = (floor - 1) * (buildingParams.depth + 1000);
      drawFloor(doc, di, floor, startY, buildingParams.width, buildingParams.depth);
    }
    
    di.autoZoom();
    
    var outputPath = buildingParams.outputFile;
    if (outputPath === "") {
      var timestamp = new Date().getTime();
      outputPath = "/home/user/floorplan-generator/output/" +
        "building_" + timestamp + ".dxf";
    }
    
    var success = di.exportFile(outputPath, "DXF 2013");
    if (success) {
      print("=== Erfolgreich erstellt! ===");
      print("Ausgabedatei: " + outputPath);
    } else {
      print("=== Fehler beim Export! ===");
    }
    
  } catch(e) {
    print("=== FEHLER: " + e + " ===");
    if (e.stack) {
      print(e.stack);
    }
  }
}

main();

