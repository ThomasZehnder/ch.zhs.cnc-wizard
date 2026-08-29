; ============================================
; Ring innen 110, aussen 160mm - Tasche ausraemen
; ID: ring110_160
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
; Aussendurchmesser: 160.0mm, Innendurchmesser: 110.0mm
; Tiefe: 6.0mm, Passes: 2, Zustellung: 4.0mm pro Pass
; Spiralabstand: 2.52mm

; Pass 1: Z = -4.00mm
G0 Z2.0
G0 X78.425 Y0
G1 Z-4.00 F450
G2 X78.425 Y0 I-78.425 J0 F450
G2 X75.905 Y0 I-75.905 J0 F450
G2 X73.385 Y0 I-73.385 J0 F450
G2 X70.86500000000001 Y0 I-70.86500000000001 J0 F450
G2 X68.34500000000001 Y0 I-68.34500000000001 J0 F450
G2 X65.82500000000002 Y0 I-65.82500000000002 J0 F450
G2 X63.305000000000014 Y0 I-63.305000000000014 J0 F450
G2 X60.78500000000001 Y0 I-60.78500000000001 J0 F450
G2 X58.26500000000001 Y0 I-58.26500000000001 J0 F450

; Pass 2: Z = -6.00mm
G0 Z2.0
G0 X78.425 Y0
G1 Z-6.00 F450
G1 X78.425 Y0 F450
G2 X78.425 Y0 I-78.425 J0 F450
G1 X75.905 Y0 F450
G2 X75.905 Y0 I-75.905 J0 F450
G1 X73.385 Y0 F450
G2 X73.385 Y0 I-73.385 J0 F450
G1 X70.86500000000001 Y0 F450
G2 X70.86500000000001 Y0 I-70.86500000000001 J0 F450
G1 X68.34500000000001 Y0 F450
G2 X68.34500000000001 Y0 I-68.34500000000001 J0 F450
G1 X65.82500000000002 Y0 F450
G2 X65.82500000000002 Y0 I-65.82500000000002 J0 F450
G1 X63.305000000000014 Y0 F450
G2 X63.305000000000014 Y0 I-63.305000000000014 J0 F450
G1 X60.78500000000001 Y0 F450
G2 X60.78500000000001 Y0 I-60.78500000000001 J0 F450
G1 X58.26500000000001 Y0 F450
G2 X58.26500000000001 Y0 I-58.26500000000001 J0 F450

; ============================================
; PROGRAM ENDE
; ============================================
G0 Z2.0
G0 X0 Y0
M5                           ; Spindle OFF
M30                          ; Program end
