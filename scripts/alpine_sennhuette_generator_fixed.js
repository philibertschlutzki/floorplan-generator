// QCAD Alpine Sennhütte Generator - Vollständig überarbeitete Version
// Verbesserungen:
// - Robuste JSON-Leselogik (QTextStream UTF-8, QIODevice.Text)
// - Ausführliche Fehlerdiagnostik und Logging
// - Sicherer Umgang mit Layern, Geometrie und Defaults
// - Korrekte Verwendung von scale (Root-Level) statt dimensions.scale
// - Defensive Validierungen und Export-Checks

include("scripts/simple.js");
include("scripts/Tools/arguments.js");

// Globale Variablen
var configFile = "";
var outputFile = "";
var config = null;

// Hilfsfunktionen
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
function clamp(v, minV, maxV) {
    v = toNumberOrDefault(v, v);
    if (isNumber(minV) && v < minV) return minV;
    if (isNumber(maxV) && v > maxV) return maxV;
    return v;
}

// Kommandozeilen-Argumente verarbeiten
function parseArguments() {
    for (var i = 0; i < args.length; i++) {
        if (args[i].indexOf("--config=") === 0) {
            configFile = args[i].substring("--config=".length);
        } else if (args[i].indexOf("--output=") === 0) {
            outputFile = args[i].substring("--output=".length);
        }
    }

    if (!configFile) {
        print("❌ Keine Konfigurationsdatei angegeben. Verwenden Sie --config=<datei.json>");
        return false;
    }
    if (!outputFile) {
        print("❌ Keine Ausgabedatei angegeben. Verwenden Sie --output=<datei.dxf>");
        return false;
    }
    return true;
}

// JSON aus Datei laden (robust, UTF-8)
function loadJsonConfig(configPath) {
    try {
        var f = new QFile(configPath);
        var fi = new QFileInfo(f);

        if (!fi.exists()) {
            print("❌ Konfigurationsdatei existiert nicht: " + configPath);
            return null;
        }
        if (!f.open(QIODevice.ReadOnly | QIODevice.Text)) {
            print("❌ Kann Konfigurationsdatei nicht öffnen (ReadOnly|Text): " + configPath);
            return null;
        }

        var ts = new QTextStream(f);
        // Manche QCAD/Qt Builds nutzen 'setCodecName' statt 'setCodec', aber QCAD 3.x kennt setCodec:
        if (typeof ts.setCodec === "function") {
            ts.setCodec("UTF-8");
        }
        var content = ts.readAll();
        f.close();

        if (!content || content.length === 0) {
            print("❌ JSON-Datei ist leer: " + configPath);
            return null;
        }

        // Debug-Snippet
        var head = content.substring(0, Math.min(120, content.length));
        print("📝 JSON gelesen (" + content.length + " Zeichen). Vorschau: " + head.replace(/\n/g, " "));

        var parsed = JSON.parse(content);
        if (!parsed) {
            print("❌ JSON.parse lieferte kein Objekt");
            return null;
        }

        print("✓ Konfiguration geladen: " + (parsed.building_type || "unbekannt"));
        return parsed;
    } catch (e) {
        print("❌ Fehler beim Laden/Parsen der JSON-Konfiguration: " + e);
        if (e && e.stack) print("Stack: " + e.stack);
        return null;
    }
}

// Sicheres Layer-Handling: existierenden Layer nutzen oder anlegen
function ensureLayer(doc, layerName, colorArr) {
    var layerId = doc.getLayerId(layerName);
    if (layerId.isValid && layerId.isValid()) {
        return layerName; // existiert bereits
    }
    var layer = new RLayer(doc, layerName);
    if (colorArr && colorArr.length === 3) {
        layer.setColor(new RColor(colorArr[0], colorArr[1], colorArr[2]));
    }
    layer.setLineweight(RLineweight.Weight025);
    var op = new RAddObjectsOperation();
    op.addObject(layer, false);
    var diTmp = new RDocumentInterface(doc);
    diTmp.applyOperation(op);
    diTmp.destroy();
    return layerName;
}

// Rechteck aus Linien zeichnen
function drawRectangle(doc, di, x, y, width, height, layerName) {
    width  = toNumberOrDefault(width, 0);
    height = toNumberOrDefault(height, 0);
    if (width <= 0 || height <= 0) {
        print("⚠️ Rechteck ignoriert (Breite/Höhe <= 0): " + width + " x " + height);
        return;
    }

    var x2 = x + width;
    var y2 = y + height;

    var lines = [
        new RLineEntity(doc, new RLineData(new RVector(x, y),  new RVector(x2, y))),
        new RLineEntity(doc, new RLineData(new RVector(x2, y), new RVector(x2, y2))),
        new RLineEntity(doc, new RLineData(new RVector(x2, y2),new RVector(x, y2))),
        new RLineEntity(doc, new RLineData(new RVector(x, y2), new RVector(x, y)))
    ];

    var op = new RAddObjectsOperation();
    for (var i = 0; i < lines.length; i++) {
        lines[i].setLayerName(layerName);
        op.addObject(lines[i], false);
    }
    di.applyOperation(op);
    print("✓ Rechteck: " + width + "x" + height + " bei (" + x + "," + y + ")");
}

// Tür (Symbolik)
function addDoor(doc, di, x, y, width, layerName) {
    width = toNumberOrDefault(width, 0.9);
    if (width <= 0) {
        print("⚠️ Türbreite <= 0, übersprungen");
        return;
    }

    var op = new RAddObjectsOperation();

    var doorLine = new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y)));
    doorLine.setLayerName(layerName);
    doorLine.setLinetypeName("DASHED");
    op.addObject(doorLine, false);

    var arcRadius = Math.max(0.1, width * 0.8);
    var doorArc = new RArcEntity(doc, new RArcData(new RVector(x, y), arcRadius, 0, Math.PI/2));
    doorArc.setLayerName(layerName);
    op.addObject(doorArc, false);

    di.applyOperation(op);
    print("✓ Tür bei (" + x + "," + y + "), Breite: " + width);
}

// Einfaches Fenster-Symbol
function addWindow(doc, di, x, y, width, layerName) {
    width = toNumberOrDefault(width, 0.8);
    var windowHeight = Math.max(0.05, width * 0.1);

    var lines = [
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + windowHeight))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y + windowHeight), new RVector(x, y + windowHeight))),
        new RLineEntity(doc, new RLineData(new RVector(x, y + windowHeight), new RVector(x, y))),
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y + windowHeight))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x, y + windowHeight)))
    ];

    var op = new RAddObjectsOperation();
    for (var i = 0; i < lines.length; i++) {
        lines[i].setLayerName(layerName);
        op.addObject(lines[i], false);
    }
    di.applyOperation(op);
    print("✓ Fenster bei (" + x + "," + y + "), Breite: " + width);
}

// Satteldach als Dreieck
function drawRoof(doc, di, x, y, width, height, layerName) {
    width = toNumberOrDefault(width, 0);
    height = toNumberOrDefault(height, 0);
    if (width <= 0 || height <= 0) {
        print("⚠️ Dach ignoriert (Breite/Höhe <= 0)");
        return;
    }

    var centerX = x + width / 2;
    var roofLines = [
        new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(centerX, y + height))),
        new RLineEntity(doc, new RLineData(new RVector(centerX, y + height), new RVector(x + width, y))),
        new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x, y)))
    ];

    var op = new RAddObjectsOperation();
    for (var i = 0; i < roofLines.length; i++) {
        roofLines[i].setLayerName(layerName);
        op.addObject(roofLines[i], false);
    }
    di.applyOperation(op);
    print("✓ Dach gezeichnet: B=" + width + ", H=" + height + " bei (" + x + "," + y + ")");
}

// Text hinzufügen
function addText(doc, di, text, x, y, height, layerName) {
    height = clamp(toNumberOrDefault(height, 6), 2, 1000);

    var td = new RTextData();
    td.setText(String(text));
    td.setAlignmentPoint(new RVector(x, y));
    td.setTextHeight(height);
    td.setHAlign(RS.HAlignCenter);
    td.setVAlign(RS.VAlignMiddle);

    var te = new RTextEntity(doc, td);
    te.setLayerName(layerName);

    var op = new RAddObjectsOperation();
    op.addObject(te, false);
    di.applyOperation(op);

    print("✓ Text: '" + text + "' bei (" + x + "," + y + "), H=" + height);
}

// Alpine Sennhütte zeichnen
function drawAlpineSennhuette(doc, di, cfg) {
    var dims = cfg.dimensions || {};

    // Maßstab bestimmen: config.scale (Root-Level), Standard 1:50 => Faktor 20 (1m = 20 Einheiten)
    var scaleStr = (cfg.scale || "1:50") + "";
    var scale = 1;
    if (scaleStr === "1:50") {
        scale = 20;
    } else if (scaleStr === "1:100") {
        scale = 10;
    } else if (scaleStr === "1:20") {
        scale = 50;
    } // ggf. weitere Maßstäbe ergänzen

    print("=== Zeichnung Alpine Sennhütte ===");
    print("Maßstab: " + scaleStr + " (Faktor: " + scale + ")");

    // Konfigurationswerte (mit Defaults)
    var foundationLength = toNumberOrDefault(dims.foundation_length, 8.0) * scale;
    var foundationWidth  = toNumberOrDefault(dims.foundation_width,  6.0) * scale;

    var stoneHeight      = toNumberOrDefault(dims.stone_section_height, 1.5) * scale;
    var woodHeight       = toNumberOrDefault(dims.wood_section_height,  2.5) * scale;

    var doorWidth        = toNumberOrDefault(dims.door_width, 1.0) * scale;
    var doorDistance     = toNumberOrDefault(dims.door_distance_from_edge, 1.0) * scale;

    var windowWidth      = toNumberOrDefault(dims.wood_window_width, 1.0) * scale;
    var numWindows       = Math.max(0, toNumberOrDefault(dims.num_wood_windows, 1));

    var roofPitchDeg     = toNumberOrDefault(dims.roof_pitch_angle, 45.0);
    var roofOverhang     = toNumberOrDefault(dims.roof_overhang, 0.2) * scale;

    // Layer
    var stoneLayer = ensureLayer(doc, "Steinbereich", [100, 100, 100]);
    var woodLayer  = ensureLayer(doc, "Holzbereich",  [139, 69, 19]);
    var roofLayer  = ensureLayer(doc, "Dach",         [200, 0, 0]);
    var textLayer  = ensureLayer(doc, "Beschriftung", [0, 0, 0]);

    print("Fundament: " + foundationLength + " x " + foundationWidth + " (Zeichnungseinheiten)");

    // Steinbereich (Fundament)
    drawRectangle(doc, di, 0, 0, foundationLength, foundationWidth, stoneLayer);

    // Türe im Steinbereich (unten an y=0)
    addDoor(doc, di, doorDistance, 0, doorWidth, stoneLayer);

    // Holzbereich oberhalb des Steinbereichs
    var gapBetween = 10; // optische Lücke zwischen Stein und Holz in Zeichnungseinheiten
    var woodY = foundationWidth + gapBetween;
    drawRectangle(doc, di, 0, woodY, foundationLength, woodHeight, woodLayer);

    // Fenster im Holzbereich
    if (numWindows > 0) {
        var windowSpacing = foundationLength / (numWindows + 1);
        var windowBaseY = woodY + woodHeight * 0.3;
        for (var i = 0; i < numWindows; i++) {
            var windowX = windowSpacing * (i + 1) - windowWidth / 2;
            addWindow(doc, di, windowX, windowBaseY, windowWidth, woodLayer);
        }
    }

    // Dach
    var roofBaseY = woodY + woodHeight + 5;
    var roofWidth = foundationLength + 2 * roofOverhang;
    var roofX     = -roofOverhang;
    var roofHeight = 0;
    // Höhe aus Dachneigung: tan(alpha) * (Breite/2)
    var pitchRad = roofPitchDeg * Math.PI / 180;
    roofHeight = Math.tan(pitchRad) * (foundationLength / 2); // basierend auf Hausbreite, nicht inkl. Überstand

    // Sicherstellen, dass roofHeight sinnvoll ist:
    roofHeight = Math.max(5, toNumberOrDefault(roofHeight, foundationLength * 0.25));
    drawRoof(doc, di, roofX, roofBaseY, roofWidth, roofHeight, roofLayer);

    // Beschriftungen
    var titleX = foundationLength / 2;
    var titleY = roofBaseY + roofHeight + 30;
    var buildingTitle = cfg.building_type || "Alpine Sennhütte";
    addText(doc, di, buildingTitle, titleX, titleY, 15, textLayer);
    addText(doc, di, "Maßstab " + scaleStr, titleX, titleY - 25, 8, textLayer);

    var matStone = dims.stone_finish || "Naturstein";
    var colorDesc = dims.color_description || "";
    var matText = "Material: " + matStone + (colorDesc ? (", " + colorDesc) : "");
    addText(doc, di, matText, titleX, titleY - 40, 6, textLayer);

    print("=== Zeichnung abgeschlossen ===");
}

// Hauptfunktion
function main() {
    try {
        print("=== QCAD Alpine Sennhütte Generator gestartet ===");

        if (!parseArguments()) {
            return;
        }

        // Konfiguration laden
        config = loadJsonConfig(configFile);
        if (!config) {
            print("❌ Abbruch: Konfiguration konnte nicht geladen werden.");
            return;
        }

        // Dokument erzeugen
        print("✓ Erstelle neues QCAD-Dokument...");
        var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
        var di = new RDocumentInterface(doc);

        // Zeichnung
        drawAlpineSennhuette(doc, di, config);

        // Zoom
        di.autoZoom();

        // Export
        print("✓ Exportiere nach: " + outputFile);
        var exportOk = false;

        // Einige QCAD Builds nutzen Writer-IDs oder Friendly Names leicht unterschiedlich.
        // Erst versuchen mit "DXF 2013", bei Misserfolg generisch:
        try {
            exportOk = di.exportFile(outputFile, "DXF 2013");
            if (!exportOk) {
                print("⚠️ Export mit 'DXF 2013' fehlgeschlagen, versuche generisch ohne Format-ID...");
                exportOk = di.exportFile(outputFile);
            }
        } catch (ex) {
            print("⚠️ Export-Exception: " + ex);
            // letzter Versuch ohne Format:
            try { exportOk = di.exportFile(outputFile); } catch (ex2) { print("⚠️ Zweiter Export-Fehler: " + ex2); }
        }

        // Validierung Ausgabedatei
        if (exportOk) {
            var outF = new QFileInfo(outputFile);
            if (outF.exists() && outF.size() > 0) {
                print("✅ Alpine Sennhütte erfolgreich generiert!");
                print("📁 Ausgabedatei: " + outputFile + " (" + outF.size() + " Bytes)");
            } else {
                print("❌ Export meldete Erfolg, aber Datei fehlt oder ist leer: " + outputFile);
            }
        } else {
            print("❌ Fehler beim Export nach: " + outputFile);
        }

        di.destroy();
    } catch (e) {
        print("❌ FEHLER im Hauptprogramm: " + e);
        if (e && e.stack) print("Stack Trace: " + e.stack);
    }
}

// Programmstart
main();
