// QCAD Alpine Sennhütte Generator - Vollständig überarbeitete Version
// Verbesserungen:
// - Fix für QFile.open() Aufruf ohne undefined 'file' Variable
// - Robuste JSON-Leselogik mit korrekter QIODevice Syntax
// - Ausführliche Fehlerdiagnostik und Logging
// - Sicherer Umgang mit Layern, Geometrie und Defaults
// - Korrekte Verwendung von scale (Root-Level) statt dimensions.scale
// - Defensive Validierungen und Export-Checks
// - Vollständige Implementierung aller fehlenden Funktionen

// Globale Variablen für Argumentenverarbeitung
var configFile = "";
var outputFile = "";
var config = null;

// Hilfsfunktionen für sichere Typkonvertierung
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
    // QCAD stellt args als globale Variable bereit
    if (typeof args === 'undefined') {
        print("❌ Keine Argumente verfügbar. Script muss mit QCAD -autostart aufgerufen werden.");
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

    print("Config-Datei: " + configFile);
    print("Output-Datei: " + outputFile);

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

// JSON aus Datei laden (robust, UTF-8) - FIX für QFile.open() Problem
function loadJsonConfig(configPath) {
    try {
        var f = new QFile(configPath);
        var fi = new QFileInfo(f);

        if (!fi.exists()) {
            print("❌ Konfigurationsdatei existiert nicht: " + configPath);
            return null;
        }
        
        print("✓ Datei existiert: " + configPath + " (Größe: " + fi.size() + " Bytes)");
        
        // FIX: Vereinfachte QFile.open() ohne QIODevice-Konstanten (ReadOnly-Standard)
        var opened = false;
        try {
            opened = f.open(); // Standard: ReadOnly
        } catch (e1) {
            // Fallback: numerischer Modus (1 = ReadOnly)
            try {
                opened = f.open(1);
            } catch (e2) {
                print("❌ QFile.open() Exception: " + e2);
                opened = false;
            }
        }

        if (!opened) {
            print("❌ Kann Konfigurationsdatei nicht öffnen: " + configPath);
            if (typeof f.errorString === "function") {
                print("Fehler: " + f.errorString());
            }
            return null;
        }

        var ts = new QTextStream(f);
        // UTF-8 Codec setzen falls verfügbar
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

// Layer erstellen oder bestehenden verwenden
function createLayer(doc, layerName, colorArr) {
    try {
        // Prüfen ob Layer bereits existiert
        var layerId = doc.getLayerId(layerName);
        if (layerId && layerId.isValid && layerId.isValid()) {
            print("✓ Verwende bestehenden Layer: " + layerName);
            return layerName;
        }
        
        // Neuen Layer erstellen
        var layer = new RLayer(doc, layerName);
        if (colorArr && colorArr.length === 3) {
            layer.setColor(new RColor(colorArr[0], colorArr[1], colorArr[2]));
        } else {
            layer.setColor(new RColor(0, 0, 0)); // Standard schwarz
        }
        layer.setLineweight(RLineweight.Weight025);
        
        // Layer zum Dokument hinzufügen
        var op = new RAddObjectsOperation();
        op.addObject(layer, false);
        
        // Temporäres DocumentInterface für die Operation
        var diTmp = new RDocumentInterface(doc);
        diTmp.applyOperation(op);
        diTmp.destroy();
        
        print("✓ Layer erstellt: " + layerName);
        return layerName;
    } catch (e) {
        print("❌ Fehler beim Erstellen des Layers '" + layerName + "': " + e);
        return layerName; // Fallback: Name zurückgeben auch wenn Erstellung fehlschlug
    }
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

    try {
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
        print("✓ Rechteck: " + width + "x" + height + " bei (" + x + "," + y + ") auf Layer: " + layerName);
    } catch (e) {
        print("❌ Fehler beim Zeichnen des Rechtecks: " + e);
    }
}

// Tür mit Öffnungsrichtung (Symbolik)
function addDoor(doc, di, x, y, width, layerName) {
    width = toNumberOrDefault(width, 0.9);
    if (width <= 0) {
        print("⚠️ Türbreite <= 0, übersprungen");
        return;
    }

    try {
        var op = new RAddObjectsOperation();

        // Türöffnung als gestrichelte Linie
        var doorLine = new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y)));
        doorLine.setLayerName(layerName);
        doorLine.setLinetypeName("DASHED");
        op.addObject(doorLine, false);

        // Türschwung als Bogen
        var arcRadius = Math.max(0.1, width * 0.8);
        var doorArc = new RArcEntity(doc, new RArcData(new RVector(x, y), arcRadius, 0, Math.PI/2));
        doorArc.setLayerName(layerName);
        op.addObject(doorArc, false);

        di.applyOperation(op);
        print("✓ Tür bei (" + x + "," + y + "), Breite: " + width + " auf Layer: " + layerName);
    } catch (e) {
        print("❌ Fehler beim Zeichnen der Tür: " + e);
    }
}

// Einfaches Fenster-Symbol mit Kreuz
function addWindow(doc, di, x, y, width, layerName) {
    width = toNumberOrDefault(width, 0.8);
    var windowHeight = Math.max(0.05, width * 0.1);

    try {
        var lines = [
            // Fensterrahmen
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x + width, y + windowHeight))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y + windowHeight), new RVector(x, y + windowHeight))),
            new RLineEntity(doc, new RLineData(new RVector(x, y + windowHeight), new RVector(x, y))),
            // Kreuz im Fenster
            new RLineEntity(doc, new RLineData(new RVector(x, y), new RVector(x + width, y + windowHeight))),
            new RLineEntity(doc, new RLineData(new RVector(x + width, y), new RVector(x, y + windowHeight)))
        ];

        var op = new RAddObjectsOperation();
        for (var i = 0; i < lines.length; i++) {
            lines[i].setLayerName(layerName);
            op.addObject(lines[i], false);
        }
        di.applyOperation(op);
        print("✓ Fenster bei (" + x + "," + y + "), Breite: " + width + " auf Layer: " + layerName);
    } catch (e) {
        print("❌ Fehler beim Zeichnen des Fensters: " + e);
    }
}

// Satteldach als Dreieck
function drawRoof(doc, di, x, y, width, height, layerName) {
    width = toNumberOrDefault(width, 0);
    height = toNumberOrDefault(height, 0);
    if (width <= 0 || height <= 0) {
        print("⚠️ Dach ignoriert (Breite/Höhe <= 0)");
        return;
    }

    try {
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
        print("✓ Dach gezeichnet: B=" + width + ", H=" + height + " bei (" + x + "," + y + ") auf Layer: " + layerName);
    } catch (e) {
        print("❌ Fehler beim Zeichnen des Dachs: " + e);
    }
}

// Text hinzufügen
function addText(doc, di, text, x, y, height, layerName) {
    height = clamp(toNumberOrDefault(height, 6), 2, 1000);

    try {
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

        print("✓ Text: '" + text + "' bei (" + x + "," + y + "), H=" + height + " auf Layer: " + layerName);
    } catch (e) {
        print("❌ Fehler beim Hinzufügen des Texts: " + e);
    }
}

// Alpine Sennhütte zeichnen - Hauptfunktion
function drawAlpineSennhuette(doc, di, cfg) {
    var dims = cfg.dimensions || {};

    print("=== Zeichnung Alpine Sennhütte ===");

    // Maßstab bestimmen: config.scale (Root-Level), Standard 1:50 => Faktor 20 (1m = 20 Einheiten)
    var scaleStr = (cfg.scale || "1:50") + "";
    var scale = 1;
    if (scaleStr === "1:50") {
        scale = 20;
    } else if (scaleStr === "1:100") {
        scale = 10;
    } else if (scaleStr === "1:20") {
        scale = 50;
    } else if (scaleStr === "1:25") {
        scale = 40;
    }

    print("Maßstab: " + scaleStr + " (Faktor: " + scale + ")");

    // Konfigurationswerte mit Defaults und Skalierung
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

    print("Dimensionen (skaliert):");
    print("- Fundament: " + foundationLength + " x " + foundationWidth);
    print("- Steinhöhe: " + stoneHeight + ", Holzhöhe: " + woodHeight);
    print("- Türbreite: " + doorWidth + ", Position: " + doorDistance);
    print("- Fenster: " + numWindows + " Stück, Breite: " + windowWidth);

    // Layer erstellen
    var stoneLayer = createLayer(doc, "Steinbereich", [100, 100, 100]);
    var woodLayer  = createLayer(doc, "Holzbereich",  [139, 69, 19]);
    var roofLayer  = createLayer(doc, "Dach",         [200, 0, 0]);
    var textLayer  = createLayer(doc, "Beschriftung", [0, 0, 0]);

    // Steinbereich (Fundament)
    drawRectangle(doc, di, 0, 0, foundationLength, foundationWidth, stoneLayer);

    // Türe im Steinbereich (unten an y=0)
    addDoor(doc, di, doorDistance, 0, doorWidth, stoneLayer);

    // Holzbereich oberhalb des Steinbereichs (mit optischem Abstand)
    var gapBetween = 10; // optische Lücke zwischen Stein und Holz in Zeichnungseinheiten
    var woodY = foundationWidth + gapBetween;
    drawRectangle(doc, di, 0, woodY, foundationLength, woodHeight, woodLayer);

    // Fenster im Holzbereich gleichmäßig verteilt
    if (numWindows > 0) {
        var windowSpacing = foundationLength / (numWindows + 1);
        var windowBaseY = woodY + woodHeight * 0.3; // 30% der Holzhöhe als Basis
        for (var i = 0; i < numWindows; i++) {
            var windowX = windowSpacing * (i + 1) - windowWidth / 2;
            addWindow(doc, di, windowX, windowBaseY, windowWidth, woodLayer);
        }
    }

    // Dach (Satteldach)
    var roofBaseY = woodY + woodHeight + 5; // 5 Einheiten Abstand zum Holzbereich
    var roofWidth = foundationLength + 2 * roofOverhang;
    var roofX     = -roofOverhang;
    var roofHeight = 0;
    
    // Dachhöhe aus Dachneigung berechnen: tan(alpha) * (Breite/2)
    var pitchRad = roofPitchDeg * Math.PI / 180;
    roofHeight = Math.tan(pitchRad) * (foundationLength / 2); // basierend auf Hausbreite
    
    // Mindest- und Maximalhöhe sicherstellen
    roofHeight = clamp(roofHeight, foundationLength * 0.2, foundationLength * 0.6);
    
    print("Dach: Neigung " + roofPitchDeg + "°, Höhe: " + roofHeight + ", Überstand: " + roofOverhang);
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

    // Abmessungen hinzufügen (optional)
    var realLength = toNumberOrDefault(dims.foundation_length, 8.0);
    var realWidth = toNumberOrDefault(dims.foundation_width, 6.0);
    var dimText = realLength + "m × " + realWidth + "m";
    addText(doc, di, dimText, titleX, titleY - 55, 5, textLayer);

    print("=== Zeichnung abgeschlossen ===");
}

// Hauptfunktion
function main() {
    try {
        print("=== QCAD Alpine Sennhütte Generator gestartet ===");
        print("QCAD Version: " + (typeof qcadVersion !== 'undefined' ? qcadVersion : 'unbekannt'));

        // Argumentenverarbeitung
        if (!parseArguments()) {
            print("❌ Argumentenverarbeitung fehlgeschlagen");
            return;
        }

        // Konfiguration laden
        print("✓ Lade Konfiguration aus: " + configFile);
        config = loadJsonConfig(configFile);
        if (!config) {
            print("❌ Abbruch: Konfiguration konnte nicht geladen werden.");
            return;
        }

        // Dokument erzeugen
        print("✓ Erstelle neues QCAD-Dokument...");
        var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
        var di = new RDocumentInterface(doc);

        // Zeichnung erstellen
        print("✓ Beginne mit der Zeichnung...");
        drawAlpineSennhuette(doc, di, config);

        // Zoom auf gesamte Zeichnung
        print("✓ Zoome auf Gesamtansicht...");
        di.autoZoom();

        // Export versuchen
        print("✓ Exportiere nach: " + outputFile);
        var exportOk = false;

        // Verschiedene Export-Strategien probieren
        try {
            // Versuch 1: Mit explizitem DXF 2013 Format
            exportOk = di.exportFile(outputFile, "DXF 2013");
            if (exportOk) {
                print("✓ Export mit 'DXF 2013' erfolgreich");
            } else {
                print("⚠️ Export mit 'DXF 2013' fehlgeschlagen, versuche generisch...");
                // Versuch 2: Ohne explizites Format
                exportOk = di.exportFile(outputFile);
                if (exportOk) {
                    print("✓ Export ohne Format-Spezifikation erfolgreich");
                }
            }
        } catch (ex) {
            print("⚠️ Export-Exception: " + ex);
            // Versuch 3: Nochmaliger Versuch ohne Format
            try { 
                exportOk = di.exportFile(outputFile); 
                if (exportOk) {
                    print("✓ Export im dritten Versuch erfolgreich");
                }
            } catch (ex2) { 
                print("❌ Alle Export-Versuche fehlgeschlagen: " + ex2); 
            }
        }

        // Validierung der Ausgabedatei
        if (exportOk) {
            var outF = new QFileInfo(outputFile);
            if (outF.exists() && outF.size() > 0) {
                print("✅ ===== Alpine Sennhütte erfolgreich generiert! =====");
                print("📁 Ausgabedatei: " + outputFile + " (" + outF.size() + " Bytes)");
                print("🏠 Gebäudetyp: " + (config.building_type || "Alpine Sennhütte"));
                print("📏 Maßstab: " + (config.scale || "1:50"));
            } else {
                print("❌ Export meldete Erfolg, aber Datei fehlt oder ist leer: " + outputFile);
            }
        } else {
            print("❌ FEHLER: Export nach '" + outputFile + "' fehlgeschlagen");
            print("Mögliche Ursachen:");
            print("- Ungültiger Pfad oder fehlende Schreibberechtigung");
            print("- QCAD Export-Plugin nicht verfügbar");
            print("- Dokumentinhalt ist leer");
        }

        // Aufräumen
        di.destroy();
        
    } catch (e) {
        print("❌ KRITISCHER FEHLER im Hauptprogramm: " + e);
        if (e && e.stack) print("Stack Trace: " + e.stack);
    }
}

// Programmstart - wird automatisch beim Laden des Scripts ausgeführt
print("=== Script geladen, starte main() ===");
main();