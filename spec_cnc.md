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

## NC-Programme (einheitliches Format)

### Mulde Sensor 35x35

**Identifier:** mulde35x35
**Filename:** mulde35x35.nc
**Type:** pocket_square
**Description:** 4 abgerundete Quadrate - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 4
- Kontur Groesse: 35mm
- Eckradius: 10mm
- Positionen: 0°, 90°, 180°, 270°
- Abstand vom Zentrum: 60mm
- Taschentiefe: 6mm

---

### Mulde Sensor 27x27

**Identifier:** mulde27x27
**Filename:** mulde27x27.nc
**Type:** pocket_square
**Description:** 4 abgerundete Quadrate - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 4
- Kontur Groesse: 27mm
- Eckradius: 4mm
- Positionen: 0°, 90°, 180°, 270°
- Abstand vom Zentrum: 50mm
- Taschentiefe: 8mm

---

### Bohrung 50

**Identifier:** bohrung50
**Filename:** bohrung50.nc
**Type:** circle_pocket
**Description:** Bohrung 50mm - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 1
- Durchmesser: 50mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 12mm

---

### Bohrungen 4x50

**Identifier:** bohrung_4x50
**Filename:** bohrung_4x50.nc
**Type:** multi_circle_drill
**Description:** 4 Bohrungen - senkrecht bohren

**Parameters:**
- Anzahl Bohrungen: 4
- Positionen: 45°, 135°, 225°, 315°
- Abstand vom Zentrum: 50mm
- Bohrungstiefe: 6mm

---

### Ring 110_160

**Identifier:** ring110_160
**Filename:** ring110_160.nc
**Type:** ring_pocket
**Description:** Ring innen 110mm, aussen 160mm - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 1
- Durchmesser Innen: 110mm
- Durchmesser Aussen: 160mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 6mm

---

### Ring 160_200

**Identifier:** ring160_200
**Filename:** ring160_200.nc
**Type:** ring_pocket
**Description:** Ring innen 160mm, aussen 200mm - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 1
- Durchmesser Innen: 160mm
- Durchmesser Aussen: 200mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 6mm

---

### Kreis 200 Aussen

**Identifier:** kreis_200_aussen
**Filename:** kreis_200_aussen.nc
**Type:** circle_outer
**Description:** Kreis 200mm - Aussenkontur

**Parameters:**
- Anzahl Konturen: 1
- Durchmesser: 200mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 12mm
- Radiuskorrektur: aussen

---

### Kreis 80 Innen

**Identifier:** kreis_80_innen
**Filename:** kreis_80_innen.nc
**Type:** circle_inner
**Description:** Kreis 80mm - Innenkontur

**Parameters:**
- Anzahl Konturen: 1
- Durchmesser: 80mm
- Abstand vom Zentrum: 0mm
- Taschentiefe: 12mm
- Radiuskorrektur: innen

---
