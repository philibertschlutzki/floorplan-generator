include("scripts/simple.js");

print("=== Test startet ===");

try {
    // Neues Dokument erstellen
    var doc = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
    var di = new RDocumentInterface(doc);
    
    // Operation für Transaktionen
    var operation = new RAddObjectsOperation();
    
    // Einfaches Rechteck (5m x 4m bei 1:50 = 100mm x 80mm auf Papier)
    // In QCAD-Einheiten: 5000 x 4000
    
    // Linien zeichnen
    var line1 = new RLineEntity(doc, new RLineData(new RVector(0, 0), new RVector(5000, 0)));
    operation.addObject(line1, false);
    
    var line2 = new RLineEntity(doc, new RLineData(new RVector(5000, 0), new RVector(5000, 4000)));
    operation.addObject(line2, false);
    
    var line3 = new RLineEntity(doc, new RLineData(new RVector(5000, 4000), new RVector(0, 4000)));
    operation.addObject(line3, false);
    
    var line4 = new RLineEntity(doc, new RLineData(new RVector(0, 4000), new RVector(0, 0)));
    operation.addObject(line4, false);
    
    // Operation anwenden
    di.applyOperation(operation);
    
    // Text hinzufügen
    var textData = new RTextData();
    textData.setText("Test Raum");
    textData.setAlignmentPoint(new RVector(2500, 2000));
    textData.setTextHeight(200);
    textData.setHAlign(RS.HAlignCenter);
    textData.setVAlign(RS.VAlignMiddle);
    
    var textEntity = new RTextEntity(doc, textData);
    var textOp = new RAddObjectsOperation();
    textOp.addObject(textEntity, false);
    di.applyOperation(textOp);
    
    // Zoom anpassen
    di.autoZoom();
    
    // Datei speichern
    var success = di.exportFile("/home/user/floorplan-generator/output/test_output.dxf", "DXF 2013");
    
    if (success) {
        print("=== Test erfolgreich! ===");
        print("Ausgabedatei: test_output.dxf");
    } else {
        print("=== Fehler beim Export! ===");
    }
    
} catch(e) {
    print("=== FEHLER: " + e + " ===");
}

