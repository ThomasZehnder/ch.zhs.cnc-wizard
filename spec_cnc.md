# Spezifikation fuer die CNC

## Allgemeine Regeln (fuer alle NC-Programme)

- Zeichnung: messplatte.dxf
- Format: MACH3 kompatibel
- Vorschub: F450 mm/min
- Fraesmaschine Durchmesser: 3.15mm
- Sicherheitshoehe Z: 2mm (absolut)
- Zustellung pro Pass: 4mm
- Rasterueberdeckung beim ausraemen: 80% Werkzeugdurchmesser (2.52mm)
- ASCII-Zeichensatz: ja

## Startbedingung (fuer alle Programme)

- Einstochen: auf der **inneren Kontur** (Werkzeugradius-korrigiert)
- Fuer Mulden/Kreise: auf der Außenkante, mit Werkzeugradius-Offset
- Fuer Ringe: auf der äußeren Kontur, mit Werkzeugradius-Offset
- Dann: absenken mit Vorschub F450 auf Taschentiefe
- Dann: Spirale nach innen fahren

## G-Code Header (fuer alle Programme)

```gcode
; ============================================
; G-CODE INITIALISIERUNG
; ============================================
G0                           ; Rapid positioning (Eilgang)
G21                          ; Metric units (mm)
G40                          ; Cancel tool radius compensation
G49                          ; Cancel tool offset
G17                          ; XY-Plane (Arbeitsebene XY)
G80                          ; Cancel canned cycles
G50                          ; Cancel scaling
G90                          ; Absolute positioning

; ============================================
; WERKZEUG- UND SPINDELEINSTELLUNGEN
; ============================================
M6 T7                        ; Tool change: T7 (D3.15mm)
S4000                        ; Spindle speed: 4000 RPM
M3                           ; Spindle ON (clockwise)
G4 P2.0                      ; Dwell 2 seconds (Spindel aufwaermen)
```

---

## NC-Programme

### Mulde Sensor 35x35

**Identifier:** mulde35x35
**Filename:** mulde35x35.nc
**Beschreibung:** 4 abgerundete Quadrate - Tasche ausraemen

**Parameter:**
- Anzahl Konturen: 4
- Kontur-Typ: abgerundetes Quadrat
- Kontur-Groesse: 35mm x 35mm
- Eckradius: 10mm
- Positionen: 0°, 90°, 180°, 270°
- Abstand vom Zentrum: 50mm
- Taschentiefe: 6mm
- Spirale mit Kreisen im Zentrum: ja
- Beruecksichtige Eckenradius: ja

---

### Mulde Sensor 27x27

**Identifier:** mulde27x27
**Filename:** mulde27x27.nc
**Beschreibung:** 4 abgerundete Quadrate - Tasche ausraemen

**Parameter:**
- Anzahl Konturen: 4
- Kontur-Typ: abgerundetes Quadrat
- Kontur-Groesse: 27mm x 27mm
- Eckradius: 4mm
- Positionen: 0°, 90°, 180°, 270°
- Abstand vom Zentrum: 50mm
- Taschentiefe: 8mm
- Spirale mit Kreisen im Zentrum: ja
- Beruecksichtige Eckenradius: ja

---

### Mulde Kreis 50

**Identifier:** bohrung50
**Filename:** bohrung50.nc
**Beschreibung:** bohrung  50

**Parameter:**
- Anzahl 1
- Kontur-Typ: kreis
- Durchmesse: 50mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 12mm
- Spirale mit Kreisen: ja

---

### Ring 110_160

**Identifier:** ring110_160
**Filename:** ring110_160.nc
**Beschreibung:** ring innen 110, aussen 160mmm

**Parameter:**
- Anzahl 1
- Kontur-Typ: ring
- Durchmesse Innen: 110mm
- Durchmesse Aussen: 160mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 6mm
- Spirale mit Kreisen: ja

---

### Ring 160_200

**Identifier:** ring160_200
**Filename:** ring160_200.nc
**Beschreibung:** ring innen 160, aussen 200mmm

**Parameter:**
- Anzahl 1
- Kontur-Typ: ring
- Durchmesse Innen: 160mm
- Durchmesse Aussen: 200mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 6mm
- Spirale mit Kreisen: ja

---

### Bohrungen 4x50

**Identifier:** bohrung_4x50
**Filename:** bohrung_4x50.nc
**Beschreibung:** 4 Bohrungen, Position 45°/135°/225°/315° im Abstand von 50mm vom Zentrum

**Parameter:**
- Anzahl 4
- Kontur-Typ: bohrung
- Position 45°/135°/225°/315°
- Abstand vom Zentrum: 50mm
- Bohrungstiefe: 6mm


---
