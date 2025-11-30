// QCAD Alpine Sennhütte Generator - Vollständige Implementierung
// Berücksichtigt ALLE Werte aus der JSON-Konfiguration
// Erweiterte Funktionalität mit stabiler DXF-Ausgabe, Multi-Fassade und Hintergrundbildern

var configFile = "";
var outputFile = "";
var config = null;

// Sichere Hilfsfunktionen
function isNumber(n) {
    return typeof n === "number" && isFinite(n);
}

function toNumberOrDefault(v, dflt) {
    if (isNumber(v)) return v;
    if (typeof v === "string") {
        var t = Number(v);
        if (isNumber(t)) return t;
    }
    return dflt;
}

// Umrechnung von Maßstab zu Pixeln (basierend auf scale)
function getScaleFactor(scaleString) {
    if (typeof scaleString === "string" && scaleString.indexOf(":") > 0) {
        var parts = scaleString.split(":");
        var ratio = toNumberOrDefault(parts[1], 50);
        return ratio; // 1:50 = 50 Pixel pro Meter
    }
    return 20; // Standard-Fallback
}

// Kommandozeilen-Argumente verarbeiten
function parseArguments() {
    if (typeof args === 'undefined') {
        print("❌ Keine Argumente verfügbar.");
        return false;
    }

    for (var i = 0; i < args.length; i++) {
        var arg = String(args[i]);
        print("Debug: Argument " + i + ": " + arg);
        
        if (arg.indexOf("--config=") === 0) {
            configFile = arg.substring("--config=".length);
        } else if (arg.indexOf("--output=") === 0) {
            outputFile = arg.substring("--output=".length);
        }
    }

    if (!configFile || !outputFile) {
        print("❌ Fehlende Argumente: --config und --output erforderlich");
        return false;
    }
    
    print("Config: " + configFile);
    print("Output: " + outputFile);
    return true;
}

// JSON-Konfiguration laden
function loadJsonConfig(configPath) {
    try {
        var f = new QFile(configPath);
        var fi = new QFileInfo(f);

        if (!fi.exists()) {
            print("❌ Datei nicht gefunden: " + configPath);
            return null;
        }

        var opened = false;
        try {
            if (typeof QIODevice !== 'undefined' && typeof QIODevice.ReadOnly !== 'undefined') {
                opened = f.open(QIODevice.ReadOnly);
            } else {
                opened = f.open(1); // ReadOnly = 1
            }
        } catch (e) {
            print("❌ Datei konnte nicht geöffnet werden: " + e);
            return null;
        }

        if (!opened) {
            print("❌ QFile.open() fehlgeschlagen");
            return null;
        }

        var ts = new QTextStream(f);
        var content = ts.readAll();
        f.close();

        if (!content || content.length === 0) {
            print("❌ Leere Datei");
            return null;
        }

        print("✓ JSON geladen (" + content.length + " Zeichen)");
        return JSON.parse(content);
    } catch (e) {
        print("❌ JSON-Fehler: " + e);
        return null;
    }
}

// Erweiterte Rechteck-Funktion mit Wandstärke
function drawThickWall(doc, di, x, y, width, height, thickness) {
    try {
        // Äußere Wand
        var outerLines = [
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + height), new RVector(x, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + height), new RVector(x, y)))
        ];
        
        // Innere Wand (falls Wandstärke > 0)
        var innerLines = [];
        if (thickness > 0) {
            innerLines = [
                new RLineEntity(doc, new RLineData(new RVector(x + thickness, y + thickness), new RVector(x + width - thickness, y + thickness))),
                new RLineEntity(doc, new RLineData(new RVector(x + width - thickness, y + thickness), new RVector(x + width - thickness, y + height - thickness))),
                new RLineEntity(doc, new RLineData(new RVector(x + width - thickness, y + height - thickness), new RVector(x + thickness, y + height - thickness))),
                new RLineEntity(doc, new RLineData(new RVector(x + thickness, y + height - thickness), new RVector(x + thickness, y + thickness)))
            ];
        }

        var op = new RAddObjectsOperation();
        
        // Alle Linien hinzufügen
        for (var i = 0; i < outerLines.length; i++) {
            op.addObject(outerLines[i], false);
        }
        for (var j = 0; j < innerLines.length; j++) {
            op.addObject(innerLines[j], false);
        }
        
        di.applyOperation(op);
        // print("✓ Wand: " + width + "x" + height + " (Stärke: " + thickness + ") bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Wand-Fehler: " + e);
        return false;
    }
}

// Erweiterte Tür mit Höhe
function drawDetailedDoor(doc, di, x, y, width, height) {
    try {
        var doorLines = [
            // Türrahmen
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + height), new RVector(x, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + height), new RVector(x, y))),
            // Türgriff (kleine Linie)
            new RLineEntity(doc, new RLineData(new RVector(x + width * 0.8, y + height * 0.5), new RVector(x + width * 0.9, y + height * 0.5)))
        ];
        
        var op = new RAddObjectsOperation();
        for (var i = 0; i < doorLines.length; i++) {
            op.addObject(doorLines[i], false);
        }
        di.applyOperation(op);
        
        // print("✓ Tür: " + width + "x" + height + " bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Tür-Fehler: " + e);
        return false;
    }
}

// Erweiterte Fenster mit konfigurierbarer Größe
function drawDetailedWindow(doc, di, x, y, width, height) {
    try {
        var windowLines = [
            // Fensterrahmen
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + height), new RVector(x, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + height), new RVector(x, y))),
            // Kreuz in der Mitte
            new RLineEntity(doc, new RLineData(new RVector(x + width/2, y), new RVector(x + width/2, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + height/2), new RVector(x + width, y + height/2)))
        ];

        var op = new RAddObjectsOperation();
        for (var i = 0; i < windowLines.length; i++) {
            op.addObject(windowLines[i], false);
        }
        di.applyOperation(op);
        
        // print("✓ Fenster: " + width + "x" + height + " bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Fenster-Fehler: " + e);
        return false;
    }
}

// Dach mit konfigurierbarem Winkel und Überhang
function drawDetailedRoof(doc, di, x, y, width, angle, overhang) {
    try {
        var angleRad = (angle * Math.PI) / 180;
        var roofHeight = (width / 2) * Math.tan(angleRad);
        var centerX = x + width / 2;
        
        // Dachlinien mit Überhang
        var roofLines = [
            // Linke Dachseite
            new RLineEntity(doc, new RLineData(new RVector(x - overhang, y), new RVector(centerX, y + roofHeight))),
            // Rechte Dachseite
            new RLineEntity(doc, new RLineData(new RVector(centerX, y + roofHeight), new RVector(x + width + overhang, y))),
            // Dachbasis
            new RLineEntity(doc, new RLineData(new RVector(x - overhang, y), new RVector(x + width + overhang, y)))
        ];

        var op = new RAddObjectsOperation();
        for (var i = 0; i < roofLines.length; i++) {
            op.addObject(roofLines[i], false);
        }
        di.applyOperation(op);
        
        // print("✓ Dach: Winkel " + angle + "°, Überhang " + overhang + " bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Dach-Fehler: " + e);
        return false;
    }
}

// Holzstruktur mit Balken (log_diameter)
function drawLogStructure(doc, di, x, y, width, height, logDiameter) {
    try {
        var numLogs = Math.floor(height / logDiameter);
        var logSpacing = height / numLogs;
        
        var logLines = [];
        
        // Horizontale Balken
        for (var i = 0; i <= numLogs; i++) {
            var logY = y + (i * logSpacing);
            logLines.push(new RLineEntity(doc, new RLineData(new RVector(x, logY), new RVector(x + width, logY))));
        }
        
        // Vertikale Verbindungen an den Ecken
        logLines.push(new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x, y + height))));
        logLines.push(new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))));

        var op = new RAddObjectsOperation();
        for (var j = 0; j < logLines.length; j++) {
            op.addObject(logLines[j], false);
        }
        di.applyOperation(op);
        
        // print("✓ Holzstruktur: " + numLogs + " Balken (Ø " + logDiameter + ") bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Holzstruktur-Fehler: " + e);
        return false;
    }
}

// Veranda (falls konfiguriert)
function drawPorch(doc, di, x, y, width, depth, height) {
    if (width <= 0 || depth <= 0) {
        // print("ℹ️ Keine Veranda (Breite oder Tiefe = 0)");
        return true;
    }
    
    try {
        var porchLines = [
            // Verandaboden
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + depth))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + depth), new RVector(x, y + depth))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + depth), new RVector(x, y)))
        ];
        
        // Säulen (vereinfacht)
        if (height > 0) {
            porchLines.push(new RLineEntity(doc, new RLineData(new RVector(x + width * 0.2, y), new RVector(x + width * 0.2, y + height))));
            porchLines.push(new RLineEntity(doc, new RLineData(new RVector(x + width * 0.8, y), new RVector(x + width * 0.8, y + height))));
        }

        var op = new RAddObjectsOperation();
        for (var i = 0; i < porchLines.length; i++) {
            op.addObject(porchLines[i], false);
        }
        di.applyOperation(op);
        
        // print("✓ Veranda: " + width + "x" + depth + " (Höhe: " + height + ") bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Veranda-Fehler: " + e);
        return false;
    }
}

// Hintergrundbild einfügen
function drawBackgroundImage(doc, di, imagePath, x, y, width, height) {
    try {
        if (!imagePath || imagePath === "") {
            return false;
        }

        print("Versuche Bild zu laden: " + imagePath);

        // In QCAD Javascript API, RImageEntity is used
        // Parameters: document, data (RImageData), position (RVector)

        // Note: QCAD scripting API for images can be tricky depending on version.
        // Assuming RImageEntity(RDocument, RImageData, RVector)

        // Need to create RImageData first
        var imageData = new RImageData(imagePath, new RVector(x, y), new RVector(1, 0), new RVector(0, 1), width, height, 0);

        var imageEntity = new RImageEntity(doc, imageData);

        var op = new RAddObjectsOperation();
        op.addObject(imageEntity, false);
        di.applyOperation(op);

        print("✓ Hintergrundbild eingefügt bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Bild-Fehler: " + e);
        // Fallback or just ignore if image fails (don't break the whole export)
        return false;
    }
}


// Hauptzeichnungsfunktion - VOLLSTÄNDIG ERWEITERT
function drawAlpineSennhuette(doc, di, cfg, offsetX, offsetY) {
    print("=== Zeichne Facade bei Offset " + offsetX + ", " + offsetY + " ===");
    
    var dims = cfg.dimensions || {};
    var scaleFactor = getScaleFactor(cfg.scale || "1:50");
    
    // ALLE Dimensionen aus der Konfiguration
    var foundationLength = toNumberOrDefault(dims.foundation_length, 8.5) * scaleFactor;
    var foundationWidth = toNumberOrDefault(dims.foundation_width, 7.0) * scaleFactor;
    var stoneHeight = toNumberOrDefault(dims.stone_section_height, 1.8) * scaleFactor;
    var stoneThickness = toNumberOrDefault(dims.stone_wall_thickness, 1.0) * scaleFactor;
    var doorWidth = toNumberOrDefault(dims.door_width, 1.5) * scaleFactor;
    var doorHeight = toNumberOrDefault(dims.door_height, 1.5) * scaleFactor;
    var doorDistance = toNumberOrDefault(dims.door_distance_from_edge, 0.1) * scaleFactor;
    var woodHeight = toNumberOrDefault(dims.wood_section_height, 2.5) * scaleFactor;
    var logDiameter = toNumberOrDefault(dims.log_diameter, 0.2) * scaleFactor;
    var windowWidth = toNumberOrDefault(dims.wood_window_width, 1.0) * scaleFactor;
    var windowHeight = toNumberOrDefault(dims.wood_window_height, 1.0) * scaleFactor;
    var numWindows = toNumberOrDefault(dims.num_wood_windows, 3);
    var roofAngle = toNumberOrDefault(dims.roof_pitch_angle, 45.0);
    var roofOverhang = toNumberOrDefault(dims.roof_overhang, 0.5) * scaleFactor;
    var porchWidth = toNumberOrDefault(dims.porch_width, 0) * scaleFactor;
    var porchDepth = toNumberOrDefault(dims.porch_depth, 0) * scaleFactor;
    var porchHeight = toNumberOrDefault(dims.porch_height, 0) * scaleFactor;
    
    // Hintergrundbild
    if (cfg.processed_image_path) {
        // Berechne Gesamthöhe für Bildskalierung (ungefähr)
        var totalHeight = stoneHeight + woodHeight + (foundationLength/2 * Math.tan(roofAngle * Math.PI/180));
        // Wir zeichnen das Bild leicht transparent oder dahinter?
        // In DXF gibt es keine Transparenz für Bilder direkt, aber Draw Order.
        // Zeichne Bild etwas größer als das Gebäude
        drawBackgroundImage(doc, di, cfg.processed_image_path, offsetX, offsetY, foundationLength, totalHeight);
    }
    
    var success = true;
    
    // Koordinaten an Offset anpassen
    var currentX = offsetX;
    var currentY = offsetY;

    // 1. Steinbereich (Fundament) mit Wandstärke
    // print("\n--- Zeichne Steinbereich ---");
    if (!drawThickWall(doc, di, currentX, currentY, foundationLength, foundationWidth, stoneThickness)) {
        success = false;
    }

    // 2. Tür mit korrekter Höhe
    // print("\n--- Zeichne Tür ---");
    if (!drawDetailedDoor(doc, di, currentX + doorDistance, currentY, doorWidth, doorHeight)) {
        success = false;
    }

    // 3. Holzbereich mit Balkenstruktur
    var woodY = currentY + foundationWidth + 10;
    // print("\n--- Zeichne Holzbereich ---");
    if (!drawLogStructure(doc, di, currentX, woodY, foundationLength, woodHeight, logDiameter)) {
        success = false;
    }

    // 4. Mehrere Fenster entsprechend der Konfiguration
    // print("\n--- Zeichne Fenster ---");
    if (numWindows > 0) {
        var windowSpacing = foundationLength / (numWindows + 1);
        for (var w = 1; w <= numWindows; w++) {
            var windowX = currentX + (windowSpacing * w) - (windowWidth / 2);
            var windowY = woodY + (woodHeight - windowHeight) / 2;
            
            if (!drawDetailedWindow(doc, di, windowX, windowY, windowWidth, windowHeight)) {
                success = false;
            }
        }
    }

    // 5. Dach mit konfigurierbarem Winkel und Überhang
    var roofY = woodY + woodHeight + 5;
    // print("\n--- Zeichne Dach ---");
    if (!drawDetailedRoof(doc, di, currentX, roofY, foundationLength, roofAngle, roofOverhang)) {
        success = false;
    }

    // 6. Veranda (falls konfiguriert)
    if (porchWidth > 0 && porchDepth > 0) {
        // print("\n--- Zeichne Veranda ---");
        var porchX = currentX + (foundationLength - porchWidth) / 2;
        var porchY = currentY - porchDepth;
        if (!drawPorch(doc, di, porchX, porchY, porchWidth, porchDepth, porchHeight)) {
            success = false;
        }
    }

    return success;
}

// Hauptfunktion
function main() {
    try {
        print("=== QCAD Alpine Sennhütte Generator (Vollständig) ===");
        print("Version: 3.0 - Multi-Fassade Support");

        if (!parseArguments()) {
            return;
        }

        config = loadJsonConfig(configFile);
        if (!config) {
            print("❌ Konfiguration nicht ladbar");
            return;
        }

        print("✓ Erstelle Dokument...");
        var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
        var di = new RDocumentInterface(doc);

        print("✓ Beginne vollständige Zeichnung...");
        var drawSuccess = true;

        // Prüfe ob neuer Multi-Config Modus
        if (config.mode && config.configs && Array.isArray(config.configs)) {
            print("ℹ️ Multi-Fassade Modus: " + config.configs.length + " Ansichten");
            var offsetX = 0;
            var spacing = 1000; // Abstand zwischen Fassaden

            for (var i = 0; i < config.configs.length; i++) {
                var subConfig = config.configs[i];
                if (!drawAlpineSennhuette(doc, di, subConfig, offsetX, 0)) {
                    drawSuccess = false;
                }
                // Offset für nächste Fassade berechnen (grob geschätzt auf 20m + Abstand)
                // Besser: Aus Config lesen
                var width = 2000; // Fallback
                 if (subConfig.dimensions && subConfig.dimensions.foundation_length) {
                     var scale = getScaleFactor(subConfig.scale || "1:50");
                     width = subConfig.dimensions.foundation_length * scale;
                 }
                offsetX += width + spacing;
            }
        } else {
            // Legacy Single Config
            print("ℹ️ Einzel-Ansicht Modus");
            if (!drawAlpineSennhuette(doc, di, config, 0, 0)) {
                drawSuccess = false;
            }
        }
        
        if (!drawSuccess) {
            print("⚠️ Zeichnung mit Fehlern abgeschlossen");
        }

        // Export mit mehreren Versuchen
        print("\n=== EXPORT-PHASE ===");
        var exportOk = false;
        
        // Versuch 1: Standard DXF 2013
        try {
            exportOk = di.exportFile(outputFile, "DXF 2013");
            if (exportOk) {
                print("✓ Export (DXF 2013) erfolgreich");
            }
        } catch (e1) {
            print("⚠️ Export DXF 2013 fehlgeschlagen: " + e1);
        }
        
        // Versuch 2: DXF 2007
        if (!exportOk) {
            try {
                exportOk = di.exportFile(outputFile, "DXF 2007");
                if (exportOk) {
                    print("✓ Export (DXF 2007) erfolgreich");
                }
            } catch (e2) {
                print("⚠️ Export DXF 2007 fehlgeschlagen: " + e2);
            }
        }
        
        // Versuch 3: Ohne Format-Angabe
        if (!exportOk) {
            try {
                exportOk = di.exportFile(outputFile);
                if (exportOk) {
                    print("✓ Export (Standard) erfolgreich");
                }
            } catch (e3) {
                print("⚠️ Export Standard fehlgeschlagen: " + e3);
            }
        }

        // Datei-Validierung
        if (exportOk) {
            try {
                var outF = new QFileInfo(outputFile);
                if (outF.exists() && outF.size() > 100) {
                    print("✅ ERFOLG: " + outputFile + " (" + outF.size() + " Bytes)");
                } else {
                    print("❌ Export fehlerhaft: Datei zu klein oder nicht vorhanden");
                }
            } catch (e4) {
                print("⚠️ Validierung fehlgeschlagen: " + e4);
            }
        } else {
            print("❌ Alle Export-Versuche fehlgeschlagen");
        }

        // Cleanup
        try {
            di.destroy();
        } catch (e5) {
            print("⚠️ Cleanup-Warnung: " + e5);
        }

    } catch (e) {
        print("❌ KRITISCHER FEHLER: " + e);
        if (e && e.stack) {
            print("Stack: " + e.stack);
        }
    }
}

// Start
print("=== Script geladen, starte main() ===");
main();
