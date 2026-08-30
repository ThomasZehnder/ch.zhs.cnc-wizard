# Spezifikation fuer die CNC Messplatte IR160P

## Allgemeine Regeln (fuer alle NC-Programme)

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

## DXF-Spezifikation

### Allgemeine DXF-Parameter

**Filename:** demo.dxf
**Format:** AutoCAD R12 DXF
**Einheit:** mm

### DXF-Geometrie

#### Kreis-Labels

**Type:** circle_labels
**Description:** Beschriftung der Kreise mit Durchmesser

**Parameters:**
- Durchmesser: 160mm, 110mm, 30mm
- Abstand zum Kreis: 2mm
- Position: -60°
- Schriftgröße: 5mm

#### Bohrungen

**Type:** bohrung_programs
**Description:** Bohrungen als Punkte im DXF

**Parameters:**
- bohrung50
- bohrung_2x50
- bohrung_zentrum

#### Mulden

**Type:** mulde_programs
**Description:** Mulden/Taschen im DXF

**Parameters:**
- mulde35x35
- mulde27x27

#### Titel-Label

**Type:** title
**Description:** Beschriftung der Messplatte

**Parameters:**
- Text: "Messplatte Demo"
- Position: 45° vom Zentrum
- Abstand vom Zentrum: 110mm
- Schriftgröße: 5mm

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
**Description:** 2 abgerundete Quadrate - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 2
- Kontur Groesse: 35mm
- Eckradius: 15mm
- Positionen: 90°, 180°
- Abstand vom Zentrum: 50mm
- Taschentiefe: 6mm

---

### Mulde Sensor 27x27

**Identifier:** mulde27x27
**Filename:** mulde27ax27a.nc
**Type:** pocket_square
**Description:** 2 abgerundete Quadrate - Tasche ausraemen

**Parameters:**
- Anzahl Konturen: 2
- Kontur Groesse: 27mm
- Eckradius: 4mm
- Positionen: 180°, 270°
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

### Bohrungen 2x50

**Identifier:** bohrung_2x50
**Filename:** bohrung_2x50.nc
**Type:** multi_circle_drill
**Description:** 2 Bohrungen - senkrecht bohren

**Parameters:**
- Anzahl Bohrungen: 2
- Positionen: 45°, 135°, 225°, 315°
- Abstand vom Zentrum: 50mm
- Bohrungstiefe: 6mm


---

### Bohrung Zentrum

**Identifier:** bohrung_zentrum
**Filename:** bohrung_zentrum.nc
**Type:** multi_circle_drill
**Description:** 1 Bohrung im Zentrum - senkrecht bohren

**Parameters:**
- Anzahl Bohrungen: 1
- Abstand vom Zentrum: 0mm
- Positionen: 0°
- Taschentiefe: 6mm

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
- Taschentiefe: 6mm


---

### Kreis 20 Innen

**Identifier:** kreis_20_innen
**Filename:** kreis_20_innen.nc
**Type:** circle
**Description:** Kreis 20mm - Innenkontur

**Parameters:**
- Durchmesser: 20mm
- Taschentiefe: 12mm
- Radiuskorrektur: innen

---
