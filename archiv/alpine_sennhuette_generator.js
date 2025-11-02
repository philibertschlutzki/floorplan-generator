// JSON-Konfiguration einlesen
function loadJsonConfig(configPath) {
    // JSON-Datei lesen und parsen
    var jsonData = readFile(configPath);
    return JSON.parse(jsonData);
}

// Alpine Sennhütte zeichnen basierend auf JSON
function drawAlpineSennhuette(doc, di, config) {
    var dims = config.dimensions;
    var scale = 1/50; // Massstab 1:50 zu mm
    
    // Koordinaten in mm umrechnen
    var foundationLength = dims.foundation_length * 1000 * scale;
    var foundationWidth = dims.foundation_width * 1000 * scale;
    var stoneHeight = dims.stone_section_height * 1000 * scale;
    var woodHeight = dims.wood_section_height * 1000 * scale;
    
    // Layer erstellen
    var stoneLayer = createLayer(doc, "Steinbereich", [100, 100, 100]);
    var woodLayer = createLayer(doc, "Holzbereich", [139, 69, 19]);
    var roofLayer = createLayer(doc, "Dach", [200, 0, 0]);
    
    // Grundriss Steinbereich
    drawRectangle(doc, 0, 0, foundationLength, foundationWidth, stoneLayer);
    
    // Türe
    var doorWidth = dims.door_width * 1000 * scale;
    var doorPos = dims.door_distance_from_edge * 1000 * scale;
    addDoor(doc, doorPos, 0, doorWidth, stoneLayer);
    
    // Holzbereich (vereinfacht als Rechteck über Steinbereich)
    drawRectangle(doc, 0, foundationWidth + 500, foundationLength, woodHeight, woodLayer);
    
    // Fenster im Holzbereich
    for (var i = 0; i < dims.num_wood_windows; i++) {
        var windowWidth = dims.wood_window_width * 1000 * scale;
        var windowX = (foundationLength / (dims.num_wood_windows + 1)) * (i + 1);
        addWindow(doc, windowX, foundationWidth + 500, windowWidth, woodLayer);
    }
    
    // Dach als Dreieck
    var roofPitch = dims.roof_pitch_angle;
    var roofHeight = (foundationLength / 2) * Math.tan(roofPitch * Math.PI / 180);
    drawRoof(doc, 0, foundationWidth + 500 + woodHeight, foundationLength, roofHeight, roofLayer);
}

