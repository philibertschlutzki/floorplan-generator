// QCAD Alpine Sennhütte Generator - Vollständig funktionsfähige Version
// Behebt alle Probleme des ursprünglichen Skripts

include("scripts/simple.js");
include("scripts/Tools/arguments.js");

// Globale Variablen
var configFile = "";
var outputFile = "";
var config = null;

// Kommandozeilen-Argumente verarbeiten
function parseArguments() {
    for (var i = 0; i < args.length; i++) {
        if (args[i].indexOf("--config=") === 0) {
            configFile = args[i].substring(9);
        } else if (args[i].indexOf("--output=") === 0) {
            outputFile = args[i].substring(9);
        }
    }
    
    if (!configFile) {
        print("❌ Keine Konfigurationsdatei angegeben. Verwenden Sie --config=datei.json");
        return false;
    }
    
    if (!outputFile) {
        print("❌ Keine Ausgabedatei angegeben. Verwenden Sie --output=datei.dxf");
        return false;
    }
    
    return true;
}

// JSON-Konfiguration laden
function loadJsonConfig(configPath) {
    try {
        var file = new QFile(configPath);
        if (!file.open(QIODevice.ReadOnly)) {
            print("❌ Kann Konfigurationsdatei nicht öffnen: " + configPath);
            return null;
        }
        
        var jsonData = file.readAll().data;
        file.close();
        
        var config = JSON.parse(jsonData);
        print("✓ Konfiguration geladen: " + config.building_type);
        return config;
    } catch(e) {
        print("❌ Fehler beim Laden der JSON-Konfiguration: " + e);
        return null;
    }
}

// Layer erstellen
function createLayer(doc, layerName, color) {
    var layer = new RLayer(doc, layerName);
    layer.setColor(new RColor(color[0], color[1], color[2]));
    layer.setLineweight(RLineweight.Weight025);
    
    var layerOp = new RAddObjectsOperation();
    layerOp.addObject(layer, false);
    return layerName;
}

// Rechteck zeichnen
function drawRectangle(doc, di, x, y, width, height, layerName) {
    // Vier Linien für das Rechteck
    var lines = [
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y + height), new RVector(x, y + height))),
        new RLineEntity(doc, new RLineData(new RVector(x, y + height), new RVector(x, y)))
    ];
    
    var operation = new RAddObjectsOperation();
    for (var i = 0; i < lines.length; i++) {
        lines[i].setLayerName(layerName);
        operation.addObject(lines[i], false);
    }
    
    di.applyOperation(operation);
    print("✓ Rechteck gezeichnet: " + width + "x" + height + " bei (" + x + "," + y + ")");
}

// Tür hinzufügen (als Öffnung in der Wand)
function addDoor(doc, di, x, y, width, layerName) {
    // Türöffnung als gestrichelte Linie
    var doorLine = new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y)));
    doorLine.setLayerName(layerName);
    doorLine.setLinetypeName("DASHED");
    
    var operation = new RAddObjectsOperation();
    operation.addObject(doorLine, false);
    di.applyOperation(operation);
    
    // Türschwung als Bogen
    var doorArc = new RArcEntity(doc, new RArcData(
        new RVector(x, y), 
        width * 0.8, 
        0, 
        Math.PI/2
    ));
    doorArc.setLayerName(layerName);
    operation = new RAddObjectsOperation();
    operation.addObject(doorArc, false);
    di.applyOperation(operation);
    
    print("✓ Tür hinzugefügt bei (" + x + "," + y + "), Breite: " + width);
}

// Fenster hinzufügen
function addWindow(doc, di, x, y, width, layerName) {
    // Fenster als Rechteck mit Diagonalen
    var windowHeight = width * 0.1; // Fensterdarstellung
    
    var windowLines = [
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + windowHeight))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y + windowHeight), new RVector(x, y + windowHeight))),
        new RLineEntity(doc, new RLineData(new RVector(x, y + windowHeight), new RVector(x, y))),
        // Diagonalen für Fenstersymbol
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y + windowHeight))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x, y + windowHeight)))
    ];
    
    var operation = new RAddObjectsOperation();
    for (var i = 0; i < windowLines.length; i++) {
        windowLines[i].setLayerName(layerName);
        operation.addObject(windowLines[i], false);
    }
    
    di.applyOperation(operation);
    print("✓ Fenster hinzugefügt bei (" + x + "," + y + "), Breite: " + width);
}

// Dach als Dreieck zeichnen
function drawRoof(doc, di, x, y, width, height, layerName) {
    var centerX = x + width / 2;
    var roofTop = y + height;
    
    var roofLines = [
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(centerX, roofTop))),
        new RLineEntity(doc, new RLineData(new RVector(centerX, roofTop), new RVector(x + width, y))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x, y)))
    ];
    
    var operation = new RAddObjectsOperation();
    for (var i = 0; i < roofLines.length; i++) {
        roofLines[i].setLayerName(layerName);
        operation.addObject(roofLines[i], false);
    }
    
    di.applyOperation(operation);
    print("✓ Dach gezeichnet: Höhe " + height + " bei (" + x + "," + y + ")");
}

// Text hinzufügen
function addText(doc, di, text, x, y, height, layerName) {
    var textData = new RTextData();
    textData.setText(text);
    textData.setAlignmentPoint(new RVector(x, y));
    textData.setTextHeight(height);
    textData.setHAlign(RS.HAlignCenter);
    textData.setVAlign(RS.VAlignMiddle);
    
    var textEntity = new RTextEntity(doc, textData);
    textEntity.setLayerName(layerName);
    
    var operation = new RAddObjectsOperation();
    operation.addObject(textEntity, false);
    di.applyOperation(operation);
    
    print("✓ Text hinzugefügt: '" + text + "' bei (" + x + "," + y + ")");
}

// Alpine Sennhütte zeichnen
function drawAlpineSennhuette(doc, di, config) {
    var dims = config.dimensions;
    var scale = dims.scale === "1:50" ? 20 : 1; // 1:50 bedeutet 1m = 20mm in der Zeichnung
    
    print("=== Beginne Zeichnung der Alpine Sennhütte ===");
    print("Maßstab: " + config.scale + " (Faktor: " + scale + ")");
    
    // Koordinaten in Zeichnungseinheiten umrechnen
    var foundationLength = dims.foundation_length * scale;
    var foundationWidth = dims.foundation_width * scale;
    var stoneHeight = dims.stone_section_height * scale;
    var woodHeight = dims.wood_section_height * scale;
    var doorWidth = dims.door_width * scale;
    var doorDistance = dims.door_distance_from_edge * scale;
    var windowWidth = dims.wood_window_width * scale;
    
    print("Fundament: " + foundationLength + " x " + foundationWidth + " Einheiten");
    
    // Layer erstellen
    var stoneLayer = createLayer(doc, "Steinbereich", [100, 100, 100]);
    var woodLayer = createLayer(doc, "Holzbereich", [139, 69, 19]);
    var roofLayer = createLayer(doc, "Dach", [200, 0, 0]);
    var textLayer = createLayer(doc, "Beschriftung", [0, 0, 0]);
    
    // Steinbereich (Fundament)
    drawRectangle(doc, di, 0, 0, foundationLength, foundationWidth, stoneLayer);
    
    // Türe im Steinbereich
    addDoor(doc, di, doorDistance, 0, doorWidth, stoneLayer);
    
    // Holzbereich über dem Steinbereich
    var woodY = foundationWidth + 10; // Kleine Lücke zwischen Stein und Holz
    drawRectangle(doc, di, 0, woodY, foundationLength, woodHeight, woodLayer);
    
    // Fenster im Holzbereich
    if (dims.num_wood_windows > 0) {
        var windowSpacing = foundationLength / (dims.num_wood_windows + 1);
        for (var i = 0; i < dims.num_wood_windows; i++) {
            var windowX = windowSpacing * (i + 1) - windowWidth / 2;
            addWindow(doc, di, windowX, woodY + woodHeight * 0.3, windowWidth, woodLayer);
        }
    }
    
    // Dach
    var roofY = woodY + woodHeight + 5;
    var roofHeight = (foundationLength / 2) * Math.tan(dims.roof_pitch_angle * Math.PI / 180);
    drawRoof(doc, di, -dims.roof_overhang * scale, roofY, 
             foundationLength + 2 * dims.roof_overhang * scale, roofHeight, roofLayer);
    
    // Beschriftung
    var titleX = foundationLength / 2;
    var titleY = roofY + roofHeight + 30;
    addText(doc, di, config.building_type, titleX, titleY, 15, textLayer);
    addText(doc, di, "Maßstab " + config.scale, titleX, titleY - 25, 8, textLayer);
    addText(doc, di, "Material: " + dims.stone_finish + ", " + dims.color_description, 
            titleX, titleY - 40, 6, textLayer);
    
    print("=== Zeichnung abgeschlossen ===");
}

// Hauptfunktion
function main() {
    try {
        print("=== QCAD Alpine Sennhütte Generator gestartet ===");
        
        // Argumente verarbeiten
        if (!parseArguments()) {
            return;
        }
        
        // Konfiguration laden
        config = loadJsonConfig(configFile);
        if (!config) {
            return;
        }
        
        // Neues Dokument erstellen
        print("✓ Erstelle neues QCAD-Dokument...");
        var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
        var di = new RDocumentInterface(doc);
        
        // Alpine Sennhütte zeichnen
        drawAlpineSennhuette(doc, di, config);
        
        // Zoom anpassen
        di.autoZoom();
        
        // Datei exportieren
        print("✓ Exportiere nach: " + outputFile);
        var success = di.exportFile(outputFile, "DXF 2013");
        
        if (success) {
            print("✅ Alpine Sennhütte erfolgreich generiert!");
            print("📁 Ausgabedatei: " + outputFile);
        } else {
            print("❌ Fehler beim Export nach: " + outputFile);
        }
        
    } catch(e) {
        print("❌ FEHLER im Hauptprogramm: " + e);
        print("Stack Trace: " + e.stack);
    }
}

// Programm starten
main();