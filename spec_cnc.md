# Spezifikation für die CNC
Zeichnung "messplatte.dxf"

# CNC Format
Muss kompatibel zu MACH3 CNC sein.

# Allgemeine Regeln
* Vorschub: F450 mm/min
* Fräser Durchmesser: 3.15mm
* 2mm über dem Werkzeug verfahren
* Zustellung pro Pass:  4mm
* beim ausräumen 80% Überdeckung des Werkzeuges 
* nur ascii zeichensatz verwenden

## Header am Anfang

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
M6 T7                        ; Tool change: T7 (Ø3.15mm)
S4000                        ; Spindle speed: 4000 RPM
M3                           ; Spindle ON (clockwise)
G4 P2.0                      ; Dwell 2 seconds (Spindel aufwärmen)
```


## Mulde Sensor 35
* Referenz im dxf: mulde35x35
* Tiefe 6mm
* Filename: `mulde35x35.nc` 