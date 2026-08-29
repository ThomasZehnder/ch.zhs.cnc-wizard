; ============================================
; Ring innen 160, aussen 200mm - Tasche ausraemen
; ID: ring160_200
; Generated for MACH3
; ============================================

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
G4 P2.0                      ; Dwell 2 seconds

; ============================================
; RING POCKET CLEARING
; ============================================
; Aussendurchmesser: 200.0mm, Innendurchmesser: 160.0mm
; Tiefe: 6.0mm, Passes: 2, Zustellung: 4.0mm pro Pass
; Spiralabstand: 2.52mm

; Pass 1: Z = -4.00mm
G0 Z2.0
G0 X98.425 Y0
G1 Z-4.00 F450
G2 X98.425 Y0 I-98.425 J0 F450
G2 X95.905 Y0 I-95.905 J0 F450
G2 X93.385 Y0 I-93.385 J0 F450
G2 X90.86500000000001 Y0 I-90.86500000000001 J0 F450
G2 X88.34500000000001 Y0 I-88.34500000000001 J0 F450
G2 X85.82500000000002 Y0 I-85.82500000000002 J0 F450
G2 X83.30500000000002 Y0 I-83.30500000000002 J0 F450

; Pass 2: Z = -6.00mm
G0 Z2.0
G0 X98.425 Y0
G1 Z-6.00 F450
G1 X98.425 Y0 F450
G2 X98.425 Y0 I-98.425 J0 F450
G1 X95.905 Y0 F450
G2 X95.905 Y0 I-95.905 J0 F450
G1 X93.385 Y0 F450
G2 X93.385 Y0 I-93.385 J0 F450
G1 X90.86500000000001 Y0 F450
G2 X90.86500000000001 Y0 I-90.86500000000001 J0 F450
G1 X88.34500000000001 Y0 F450
G2 X88.34500000000001 Y0 I-88.34500000000001 J0 F450
G1 X85.82500000000002 Y0 F450
G2 X85.82500000000002 Y0 I-85.82500000000002 J0 F450
G1 X83.30500000000002 Y0 F450
G2 X83.30500000000002 Y0 I-83.30500000000002 J0 F450

; ============================================
; PROGRAM ENDE
; ============================================
G0 Z2.0
G0 X0 Y0
M5                           ; Spindle OFF
M30                          ; Program end
