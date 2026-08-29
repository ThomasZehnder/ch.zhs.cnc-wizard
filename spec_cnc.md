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
- Rastermuster: ja (horizontal spirale)
- Beruecksichtige Eckenradius: ja

---
