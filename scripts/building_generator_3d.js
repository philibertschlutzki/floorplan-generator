// ===== building_generator_3d.js =====
// QCAD Script zur automatisierten Erstellung von 3D-Gebäuden (Isometrische Darstellung)
// Erstellt komplette Gebäude mit vier Wänden, Dach und Boden

include("scripts/simple.js");

// 3D-Gebäudeparameter
var buildingParams = {
  width: 10000,
  depth: 8000,
  floors: 2,
  wallHeight: 3000,
  roofType: "flat",
  roofHeight: 0,
  windowCount: 2,
  doorCount: 1,
  wallColor: "#CCCCCC",
  roofColor: "#AA0000",
  foundationHeight: 500,
  isoAngle: 30,
  viewScale: 1.0,
  detailLevel: 2,
  outputFormat: 1,
  outputFile: ""
};

// Isometrische Transformationsmatrix
var isoTransform = {
  // Standard isometrische Projektion (30°)
  xx: Math.cos(Math.PI/6),  // cos(30°)
  xy: -Math.cos(Math.PI/6), // -cos(30°)
  yx: Math.sin(Math.PI/6),  // sin(30°)
  yy: Math.sin(Math.PI/6)   // sin(30°)
};

function printHelp() {
  print("3D-Gebäudegenerator für QCAD");
  print("Erstellt komplette Gebäude mit vier Wänden, Dach und Boden");
  print();
  print("Parameter:");
  print(" --width=SIZE        Gebäudebreite");
  print(" --depth=SIZE        Gebäudetiefe");
  print(" --floors=NUM        Anzahl Geschosse");
  print(" --wall-height=SIZE  Wandhöhe pro Geschoss");
  print(" --roof-type=TYPE    Dachtyp: flat, gable, hip, shed");
  print(" --roof-height=SIZE  Dachhöhe");
  print(" --window-count=NUM  Fenster pro Wand");
  print(" --door-count=NUM    Anzahl Türen");
  print(" --wall-color=COLOR  Wandfarbe (Hex)");
  print(" --roof-color=COLOR  Dachfarbe (Hex)");
  print(" --iso-angle=ANGLE   Isometrischer Winkel");
  print(" --view-scale=SCALE  Darstellungsmaßstab");
}

// Erweiterte Argumentverarbeitung
function parseArguments() {
  for (var i = 0; i < arguments.length; i++) {
    var arg = arguments[i];
    
    if (arg === "-h" || arg === "--help") {
      printHelp();
      return false;
    }
    
    // Parameter extrahieren
    if (arg.indexOf("--width=") === 0) {
      buildingParams.width = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--depth=") === 0) {
      buildingParams.depth = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--floors=") === 0) {
      buildingParams.floors = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--wall-height=") === 0) {
      buildingParams.wallHeight = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--roof-type=") === 0) {
      buildingParams.roofType = arg.split("=")[1];
    } else if (arg.indexOf("--roof-height=") === 0) {
      buildingParams.roofHeight = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--window-count=") === 0) {
      buildingParams.windowCount = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--door-count=") === 0) {
      buildingParams.doorCount = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--wall-color=") === 0) {
      buildingParams.wallColor = arg.split("=")[1];
    } else if (arg.indexOf("--roof-color=") === 0) {
      buildingParams.roofColor = arg.split("=")[1];
    } else if (arg.indexOf("--foundation-height=") === 0) {
      buildingParams.foundationHeight = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--iso-angle=") === 0) {
      var angle = parseFloat(arg.split("=")[1]) * Math.PI / 180;
      buildingParams.isoAngle = angle;
      updateIsoTransform(angle);
    } else if (arg.indexOf("--view-scale=") === 0) {
      buildingParams.viewScale = parseFloat(arg.split("=")[1]);
    } else if (arg.indexOf("--detail-level=") === 0) {
      buildingParams.detailLevel = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--output-format=") === 0) {
      buildingParams.outputFormat = parseInt(arg.split("=")[1]);
    } else if (arg.indexOf("--output=") === 0) {
      buildingParams.outputFile = arg.split("=")[1];
    }
  }
  
  return true;
}

// Isometrische Transformation aktualisieren
function updateIsoTransform(angle) {
  isoTransform.xx = Math.cos(angle);
  isoTransform.xy = -Math.cos(angle);
  isoTransform.yx = Math.sin(angle);
  isoTransform.yy = Math.sin(angle);
}

// Punkt isometrisch transformieren
function transformPoint(x, y, z) {
  var isoX = (x * isoTransform.xx + y * isoTransform.xy) * buildingParams.viewScale;
  var isoY = (x * isoTransform.yx + y * isoTransform.yy + z) * buildingParams.viewScale;
  return new RVector(isoX, isoY);
}

// Farbe aus Hex-String parsen
function parseColor(hexColor) {
  if (!hexColor || hexColor.charAt(0) !== '#') {
    return new RColor(200, 200, 200); // Standard grau
  }
  
  var r = parseInt(hexColor.substr(1, 2), 16);
  var g = parseInt(hexColor.substr(3, 2), 16);
  var b = parseInt(hexColor.substr(5, 2), 16);
  return new RColor(r, g, b);
}

// Layer mit Farbe erstellen
function createLayerWithColor(doc, operation, name, hexColor) {
  var color = parseColor(hexColor);
  var layer = new RLayer(doc, name, false, false, color, RLineweight.Weight025);
  operation.addObject(layer, false);
  return layer.getId();
}

// 3D-Linie zeichnen (isometrisch transformiert)
function draw3DLine(doc, operation, x1, y1, z1, x2, y2, z2, layerId) {
  var start = transformPoint(x1, y1, z1);
  var end = transformPoint(x2, y2, z2);
  
  var line = new RLineEntity(doc, new RLineData(start, end));
  line.setLayerId(layerId);
  operation.addObject(line, false);
}

// Fundament/Boden zeichnen
function drawFoundation(doc, operation, layerId) {
  var h = buildingParams.foundationHeight;
  var w = buildingParams.width;
  var d = buildingParams.depth;
  
  // Grundfläche (Boden)
  draw3DLine(doc, operation, 0, 0, 0, w, 0, 0, layerId);
  draw3DLine(doc, operation, w, 0, 0, w, d, 0, layerId);
  draw3DLine(doc, operation, w, d, 0, 0, d, 0, layerId);
  draw3DLine(doc, operation, 0, d, 0, 0, 0, 0, layerId);
  
  // Fundamenthöhe
  draw3DLine(doc, operation, 0, 0, 0, 0, 0, h, layerId);
  draw3DLine(doc, operation, w, 0, 0, w, 0, h, layerId);
  draw3DLine(doc, operation, w, d, 0, w, d, h, layerId);
  draw3DLine(doc, operation, 0, d, 0, 0, d, h, layerId);
  
  // Obere Fundamentkante
  draw3DLine(doc, operation, 0, 0, h, w, 0, h, layerId);
  draw3DLine(doc, operation, w, 0, h, w, d, h, layerId);
  draw3DLine(doc, operation, w, d, h, 0, d, h, layerId);
  draw3DLine(doc, operation, 0, d, h, 0, 0, h, layerId);
}

// Wände für ein Geschoss zeichnen
function drawWalls(doc, operation, floorNum, layerId) {
  var w = buildingParams.width;
  var d = buildingParams.depth;
  var baseZ = buildingParams.foundationHeight + (floorNum - 1) * buildingParams.wallHeight;
  var topZ = baseZ + buildingParams.wallHeight;
  
  // Vier Wände - vertikale Linien
  draw3DLine(doc, operation, 0, 0, baseZ, 0, 0, topZ, layerId); // Ecke 1
  draw3DLine(doc, operation, w, 0, baseZ, w, 0, topZ, layerId); // Ecke 2
  draw3DLine(doc, operation, w, d, baseZ, w, d, topZ, layerId); // Ecke 3
  draw3DLine(doc, operation, 0, d, baseZ, 0, d, topZ, layerId); // Ecke 4
  
  // Untere Wandkanten
  draw3DLine(doc, operation, 0, 0, baseZ, w, 0, baseZ, layerId); // Vorderwand unten
  draw3DLine(doc, operation, w, 0, baseZ, w, d, baseZ, layerId); // Rechte Wand unten
  draw3DLine(doc, operation, w, d, baseZ, 0, d, baseZ, layerId); // Rückwand unten
  draw3DLine(doc, operation, 0, d, baseZ, 0, 0, baseZ, layerId); // Linke Wand unten
  
  // Obere Wandkanten
  draw3DLine(doc, operation, 0, 0, topZ, w, 0, topZ, layerId); // Vorderwand oben
  draw3DLine(doc, operation, w, 0, topZ, w, d, topZ, layerId); // Rechte Wand oben
  draw3DLine(doc, operation, w, d, topZ, 0, d, topZ, layerId); // Rückwand oben
  draw3DLine(doc, operation, 0, d, topZ, 0, 0, topZ, layerId); // Linke Wand oben
}

// Fenster hinzufügen
function addWindows(doc, operation, floorNum, layerId) {
  if (buildingParams.detailLevel < 2) return;
  
  var w = buildingParams.width;
  var d = buildingParams.depth;
  var baseZ = buildingParams.foundationHeight + (floorNum - 1) * buildingParams.wallHeight;
  var windowHeight = buildingParams.wallHeight * 0.4;
  var windowY = baseZ + buildingParams.wallHeight * 0.3;
  var windowTop = windowY + windowHeight;
  var windowWidth = w / (buildingParams.windowCount + 1);
  
  // Fenster an Vorderwand
  for (var i = 1; i <= buildingParams.windowCount; i++) {
    var windowX = i * windowWidth - windowWidth * 0.3;
    var windowX2 = i * windowWidth + windowWidth * 0.3;
    
    // Fensterrahmen
    draw3DLine(doc, operation, windowX, 0, windowY, windowX2, 0, windowY, layerId);
    draw3DLine(doc, operation, windowX2, 0, windowY, windowX2, 0, windowTop, layerId);
    draw3DLine(doc, operation, windowX2, 0, windowTop, windowX, 0, windowTop, layerId);
    draw3DLine(doc, operation, windowX, 0, windowTop, windowX, 0, windowY, layerId);
    
    // Fensterkreuz
    if (buildingParams.detailLevel >= 3) {
      var midX = (windowX + windowX2) / 2;
      var midY = (windowY + windowTop) / 2;
      draw3DLine(doc, operation, midX, 0, windowY, midX, 0, windowTop, layerId);
      draw3DLine(doc, operation, windowX, 0, midY, windowX2, 0, midY, layerId);
    }
  }
  
  // Fenster an Rückwand (gespiegelt)
  for (var i = 1; i <= buildingParams.windowCount; i++) {
    var windowX = i * windowWidth - windowWidth * 0.3;
    var windowX2 = i * windowWidth + windowWidth * 0.3;
    
    draw3DLine(doc, operation, windowX, d, windowY, windowX2, d, windowY, layerId);
    draw3DLine(doc, operation, windowX2, d, windowY, windowX2, d, windowTop, layerId);
    draw3DLine(doc, operation, windowX2, d, windowTop, windowX, d, windowTop, layerId);
    draw3DLine(doc, operation, windowX, d, windowTop, windowX, d, windowY, layerId);
  }
}

// Türen hinzufügen
function addDoors(doc, operation, layerId) {
  if (buildingParams.detailLevel < 2) return;
  
  var w = buildingParams.width;
  var d = buildingParams.depth;
  var baseZ = buildingParams.foundationHeight;
  var doorHeight = buildingParams.wallHeight * 0.8;
  var doorWidth = w * 0.08; // 8% der Gebäudebreite
  var doorX = (w - doorWidth) / 2; // Mittig an Vorderwand
  
  // Haupteingang
  draw3DLine(doc, operation, doorX, 0, baseZ, doorX + doorWidth, 0, baseZ, layerId);
  draw3DLine(doc, operation, doorX + doorWidth, 0, baseZ, doorX + doorWidth, 0, baseZ + doorHeight, layerId);
  draw3DLine(doc, operation, doorX + doorWidth, 0, baseZ + doorHeight, doorX, 0, baseZ + doorHeight, layerId);
  draw3DLine(doc, operation, doorX, 0, baseZ + doorHeight, doorX, 0, baseZ, layerId);
  
  // Türgriff (Detail Level 3)
  if (buildingParams.detailLevel >= 3) {
    var handleX = doorX + doorWidth * 0.8;
    var handleZ = baseZ + doorHeight * 0.5;
    draw3DLine(doc, operation, handleX, 0, handleZ - 50, handleX, 0, handleZ + 50, layerId);
  }
}

// Dach zeichnen
function drawRoof(doc, operation, roofLayerId) {
  var w = buildingParams.width;
  var d = buildingParams.depth;
  var totalFloorHeight = buildingParams.foundationHeight + buildingParams.floors * buildingParams.wallHeight;
  var roofHeight = buildingParams.roofHeight;
  
  switch (buildingParams.roofType) {
    case "flat":
      drawFlatRoof(doc, operation, roofLayerId, w, d, totalFloorHeight);
      break;
    case "gable":
      drawGableRoof(doc, operation, roofLayerId, w, d, totalFloorHeight, roofHeight);
      break;
    case "hip":
      drawHipRoof(doc, operation, roofLayerId, w, d, totalFloorHeight, roofHeight);
      break;
    case "shed":
      drawShedRoof(doc, operation, roofLayerId, w, d, totalFloorHeight, roofHeight);
      break;
  }
}

// Flachdach
function drawFlatRoof(doc, operation, layerId, w, d, baseZ) {
  draw3DLine(doc, operation, 0, 0, baseZ, w, 0, baseZ, layerId);
  draw3DLine(doc, operation, w, 0, baseZ, w, d, baseZ, layerId);
  draw3DLine(doc, operation, w, d, baseZ, 0, d, baseZ, layerId);
  draw3DLine(doc, operation, 0, d, baseZ, 0, 0, baseZ, layerId);
}

// Satteldach
function drawGableRoof(doc, operation, layerId, w, d, baseZ, height) {
  var midX = w / 2;
  var peakZ = baseZ + height;
  
  // Dachfirst
  draw3DLine(doc, operation, midX, 0, peakZ, midX, d, peakZ, layerId);
  
  // Dachflächen
  draw3DLine(doc, operation, 0, 0, baseZ, midX, 0, peakZ, layerId);
  draw3DLine(doc, operation, midX, 0, peakZ, w, 0, baseZ, layerId);
  draw3DLine(doc, operation, 0, d, baseZ, midX, d, peakZ, layerId);
  draw3DLine(doc, operation, midX, d, peakZ, w, d, baseZ, layerId);
  
  // Giebelwände
  draw3DLine(doc, operation, 0, 0, baseZ, 0, d, baseZ, layerId);
  draw3DLine(doc, operation, w, 0, baseZ, w, d, baseZ, layerId);
  draw3DLine(doc, operation, 0, 0, baseZ, midX, 0, peakZ, layerId);
  draw3DLine(doc, operation, 0, d, baseZ, midX, d, peakZ, layerId);
  draw3DLine(doc, operation, w, 0, baseZ, midX, 0, peakZ, layerId);
  draw3DLine(doc, operation, w, d, baseZ, midX, d, peakZ, layerId);
}

// Walmdach
function drawHipRoof(doc, operation, layerId, w, d, baseZ, height) {
  var midX = w / 2;
  var midY = d / 2;
  var peakZ = baseZ + height;
  
  // Dachspitze (bei quadratischem Grundriss) oder First
  if (Math.abs(w - d) < 1000) { // Nahezu quadratisch - Pyramidendach
    draw3DLine(doc, operation, 0, 0, baseZ, midX, midY, peakZ, layerId);
    draw3DLine(doc, operation, w, 0, baseZ, midX, midY, peakZ, layerId);
    draw3DLine(doc, operation, w, d, baseZ, midX, midY, peakZ, layerId);
    draw3DLine(doc, operation, 0, d, baseZ, midX, midY, peakZ, layerId);
  } else { // Walmdach mit First
    var firstStart = Math.min(w, d) / 4;
    var firstEnd = Math.max(w, d) - firstStart;
    
    if (w > d) { // First parallel zur Tiefe
      draw3DLine(doc, operation, firstStart, midY, peakZ, firstEnd, midY, peakZ, layerId);
      // Dachflächen
      draw3DLine(doc, operation, 0, 0, baseZ, firstStart, midY, peakZ, layerId);
      draw3DLine(doc, operation, 0, d, baseZ, firstStart, midY, peakZ, layerId);
      draw3DLine(doc, operation, w, 0, baseZ, firstEnd, midY, peakZ, layerId);
      draw3DLine(doc, operation, w, d, baseZ, firstEnd, midY, peakZ, layerId);
    } else { // First parallel zur Breite
      draw3DLine(doc, operation, midX, firstStart, peakZ, midX, firstEnd, peakZ, layerId);
      draw3DLine(doc, operation, 0, 0, baseZ, midX, firstStart, peakZ, layerId);
      draw3DLine(doc, operation, w, 0, baseZ, midX, firstStart, peakZ, layerId);
      draw3DLine(doc, operation, 0, d, baseZ, midX, firstEnd, peakZ, layerId);
      draw3DLine(doc, operation, w, d, baseZ, midX, firstEnd, peakZ, layerId);
    }
  }
}

// Pultdach
function drawShedRoof(doc, operation, layerId, w, d, baseZ, height) {
  var topZ = baseZ + height;
  
  // Dachkante (von niedrig zu hoch)
  draw3DLine(doc, operation, 0, 0, baseZ, 0, d, baseZ, layerId);
  draw3DLine(doc, operation, w, 0, topZ, w, d, topZ, layerId);
  
  // Dachfläche
  draw3DLine(doc, operation, 0, 0, baseZ, w, 0, topZ, layerId);
  draw3DLine(doc, operation, 0, d, baseZ, w, d, topZ, layerId);
  
  // Seitenwände
  draw3DLine(doc, operation, 0, 0, baseZ, w, 0, topZ, layerId);
  draw3DLine(doc, operation, 0, d, baseZ, w, d, topZ, layerId);
}

// 3D-Text-Label hinzufügen
function add3DTextLabel(doc, operation, text, x, y, z, height, layerId) {
  var pos = transformPoint(x, y, z);
  var textData = new RTextData();
  textData.setText(text);
  textData.setAlignmentPoint(pos);
  textData.setTextHeight(height * buildingParams.viewScale);
  textData.setHAlign(RS.HAlignCenter);
  textData.setVAlign(RS.VAlignMiddle);
  var textEntity = new RTextEntity(doc, textData);
  textEntity.setLayerId(layerId);
  operation.addObject(textEntity, false);
}

// Komplettes 3D-Gebäude zeichnen
function draw3DBuilding(doc, di) {
  var operation = new RAddObjectsOperation();
  
  // Layer erstellen
  var foundationLayer = createLayerWithColor(doc, operation, "Foundation", "#8B4513");
  var wallsLayer = createLayerWithColor(doc, operation, "Walls", buildingParams.wallColor);
  var windowsLayer = createLayerWithColor(doc, operation, "Windows", "#87CEEB");
  var doorsLayer = createLayerWithColor(doc, operation, "Doors", "#DEB887");
  var roofLayer = createLayerWithColor(doc, operation, "Roof", buildingParams.roofColor);
  var labelsLayer = createLayerWithColor(doc, operation, "Labels", "#000000");
  
  // Fundament/Boden zeichnen
  drawFoundation(doc, operation, foundationLayer);
  
  // Alle Geschosse zeichnen
  for (var floor = 1; floor <= buildingParams.floors; floor++) {
    drawWalls(doc, operation, floor, wallsLayer);
    addWindows(doc, operation, floor, windowsLayer);
    
    if (floor === 1) { // Nur im Erdgeschoss Türen
      addDoors(doc, operation, doorsLayer);
    }
  }
  
  // Dach zeichnen
  drawRoof(doc, operation, roofLayer);
  
  // Beschriftungen hinzufügen
  if (buildingParams.detailLevel >= 2) {
    var labelZ = buildingParams.foundationHeight + buildingParams.floors * buildingParams.wallHeight + 500;
    add3DTextLabel(doc, operation, 
      buildingParams.floors + "-stöckiges Gebäude",
      buildingParams.width / 2, buildingParams.depth / 2, labelZ, 
      300, labelsLayer);
    
    add3DTextLabel(doc, operation, 
      (buildingParams.width/1000) + "m x " + (buildingParams.depth/1000) + "m",
      buildingParams.width / 2, buildingParams.depth / 2, labelZ - 500, 
      200, labelsLayer);
  }
  
  di.applyOperation(operation);
}

// Hauptfunktion
function main() {
  if (!parseArguments()) {
    return;
  }
  
  print("=== 3D-Gebäudegenerator startet ===");
  print("Breite: " + buildingParams.width + ", Tiefe: " + buildingParams.depth);
  print("Geschosse: " + buildingParams.floors + ", Wandhöhe: " + buildingParams.wallHeight);
  print("Dach: " + buildingParams.roofType + " (Höhe: " + buildingParams.roofHeight + ")");
  print("Isometrischer Winkel: " + (buildingParams.isoAngle * 180 / Math.PI) + "°");
  print("Detailgrad: " + buildingParams.detailLevel);
  
  try {
    var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
    var di = new RDocumentInterface(doc);
    
    // 3D-Gebäude erstellen
    draw3DBuilding(doc, di);
    
    di.autoZoom();
    
    // Ausgabedatei bestimmen
    var outputPath = buildingParams.outputFile;
    if (outputPath === "") {
      var timestamp = new Date().getTime();
      var extension = "dxf";
      if (buildingParams.outputFormat === 2) extension = "svg";
      else if (buildingParams.outputFormat === 3) extension = "pdf";
      
      outputPath = "/home/user/floorplan-generator/output/" +
        "building_3d_" + timestamp + "." + extension;
    }
    
    // Export je nach Format
    var success = false;
    if (buildingParams.outputFormat === 1) {
      success = di.exportFile(outputPath, "DXF");
    } else if (buildingParams.outputFormat === 2) {
      success = di.exportFile(outputPath, "SVG");
    } else if (buildingParams.outputFormat === 3) {
      success = di.exportFile(outputPath, "PDF");
    }
    
    if (success) {
      print("=== 3D-Gebäude erfolgreich erstellt! ===");
      print("✓ Vier Wände gezeichnet");
      print("✓ " + buildingParams.roofType + "-Dach hinzugefügt");
      print("✓ Fundament/Boden erstellt");
      print("✓ " + buildingParams.windowCount + " Fenster pro Wand");
      print("✓ Isometrische Darstellung (" + (buildingParams.isoAngle * 180 / Math.PI) + "°)");
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