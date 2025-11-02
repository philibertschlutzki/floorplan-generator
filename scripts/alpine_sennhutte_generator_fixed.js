// QCAD Alpine Sennhütte Generator - Minimalistische, sichere Version
// Behebt Speicherzugriffsfehler durch Vermeidung komplexer Layer-Operationen
// Fokus auf Stabilität und erfolgreichen DXF-Export

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

        // Sichere Datei-Öffnung
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

// Minimalistische Rechteck-Funktion OHNE Layer-Operationen
function drawSimpleRectangle(doc, di, x, y, width, height) {
    try {
        // Direkte Linienerstellung ohne Layer-Zuweisungen
        var lines = [
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + height), new RVector(x, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + height), new RVector(x, y)))
        ];

        // Einfache Operation ohne komplexe Layer-Zuweisungen
        var op = new RAddObjectsOperation();
        for (var i = 0; i < lines.length; i++) {
            op.addObject(lines[i], false);
        }
        
        di.applyOperation(op);
        print("✓ Rechteck: " + width + "x" + height + " bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Rechteck-Fehler: " + e);
        return false;
    }
}

// Einfache Tür
function drawSimpleDoor(doc, di, x, y, width) {
    try {
        var doorLine = new RLineEntity(doc, new RLineData(
            new RVector(x, y), 
            new RVector(x + width, y)
        ));
        
        var op = new RAddObjectsOperation();
        op.addObject(doorLine, false);
        di.applyOperation(op);
        
        print("✓ Tür bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Tür-Fehler: " + e);
        return false;
    }
}

// Einfaches Fenster
function drawSimpleWindow(doc, di, x, y, width) {
    try {
        var height = width * 0.1;
        var lines = [
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + height), new RVector(x, y + height))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + height), new RVector(x, y)))
        ];

        var op = new RAddObjectsOperation();
        for (var i = 0; i < lines.length; i++) {
            op.addObject(lines[i], false);
        }
        di.applyOperation(op);
        
        print("✓ Fenster bei (" + x + "," + y + ")");
        return true;
    } catch (e) {
        print("❌ Fenster-Fehler: " + e);
        return false;
    }
}

// Hauptzeichnungsfunktion - VEREINFACHT
function drawAlpineSennhuette(doc, di, cfg) {
    print("=== Beginne Zeichnung (Minimal-Modus) ===");
    
    var dims = cfg.dimensions || {};
    var scale = 20; // 1:50
    
    // Basisdimensionen
    var foundationLength = toNumberOrDefault(dims.foundation_length, 8.0) * scale;
    var foundationWidth  = toNumberOrDefault(dims.foundation_width,  6.0) * scale;
    var stoneHeight      = toNumberOrDefault(dims.stone_section_height, 1.5) * scale;
    var woodHeight       = toNumberOrDefault(dims.wood_section_height,  2.5) * scale;
    var doorWidth        = toNumberOrDefault(dims.door_width, 1.0) * scale;
    var doorDistance     = toNumberOrDefault(dims.door_distance_from_edge, 1.0) * scale;
    
    print("Dimensionen: " + foundationLength + "x" + foundationWidth);

    // KEINE LAYER - Direkte Geometrie-Erstellung
    var success = true;
    
    // 1. Steinbereich (Fundament)
    print("Zeichne Steinbereich...");
    if (!drawSimpleRectangle(doc, di, 0, 0, foundationLength, foundationWidth)) {
        success = false;
    }

    // 2. Tür
    print("Zeichne Tür...");
    if (!drawSimpleDoor(doc, di, doorDistance, 0, doorWidth)) {
        success = false;
    }

    // 3. Holzbereich
    var woodY = foundationWidth + 10;
    print("Zeichne Holzbereich...");
    if (!drawSimpleRectangle(doc, di, 0, woodY, foundationLength, woodHeight)) {
        success = false;
    }

    // 4. Ein Fenster
    var windowWidth = toNumberOrDefault(dims.wood_window_width, 1.0) * scale;
    var windowX = foundationLength / 2 - windowWidth / 2;
    var windowY = woodY + woodHeight * 0.3;
    print("Zeichne Fenster...");
    if (!drawSimpleWindow(doc, di, windowX, windowY, windowWidth)) {
        success = false;
    }

    // 5. Einfaches Dach (Dreieck)
    var roofY = woodY + woodHeight + 5;
    var roofHeight = foundationLength * 0.3;
    var centerX = foundationLength / 2;
    
    print("Zeichne Dach...");
    try {
        var roofLines = [
            new RLineEntity(doc, new RLineData(new RVector(0, roofY), new RVector(centerX, roofY + roofHeight))),
            new RLineEntity(doc, new RLineData(new RVector(centerX, roofY + roofHeight), new RVector(foundationLength, roofY))),
            new RLineEntity(doc, new RLineData(new RVector(foundationLength, roofY), new RVector(0, roofY)))
        ];

        var op = new RAddObjectsOperation();
        for (var i = 0; i < roofLines.length; i++) {
            op.addObject(roofLines[i], false);
        }
        di.applyOperation(op);
        print("✓ Dach gezeichnet");
    } catch (e) {
        print("❌ Dach-Fehler: " + e);
        success = false;
    }

    print("=== Zeichnung abgeschlossen (Erfolg: " + success + ") ===");
    return success;
}

// Hauptfunktion - STARK VEREINFACHT
function main() {
    try {
        print("=== QCAD Alpine Sennhütte Generator (Minimal) ===");

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

        print("✓ Beginne Zeichnung...");
        var drawSuccess = drawAlpineSennhuette(doc, di, config);
        
        if (!drawSuccess) {
            print("⚠️ Zeichnung mit Fehlern abgeschlossen");
        }

        // Export - MEHRERE VERSUCHE
        print("✓ Exportiere...");
        var exportOk = false;
        
        // Versuch 1: Standard DXF
        try {
            exportOk = di.exportFile(outputFile, "DXF 2013");
            if (exportOk) {
                print("✓ Export Versuch 1 erfolgreich");
            }
        } catch (e1) {
            print("⚠️ Export Versuch 1 fehlgeschlagen: " + e1);
        }
        
        // Versuch 2: Ohne Format
        if (!exportOk) {
            try {
                exportOk = di.exportFile(outputFile);
                if (exportOk) {
                    print("✓ Export Versuch 2 erfolgreich");
                }
            } catch (e2) {
                print("⚠️ Export Versuch 2 fehlgeschlagen: " + e2);
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
            } catch (e3) {
                print("⚠️ Validierung fehlgeschlagen: " + e3);
            }
        } else {
            print("❌ Alle Export-Versuche fehlgeschlagen");
        }

        // Cleanup
        try {
            di.destroy();
        } catch (e4) {
            print("⚠️ Cleanup-Warnung: " + e4);
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