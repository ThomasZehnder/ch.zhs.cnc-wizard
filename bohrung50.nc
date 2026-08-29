; ============================================
; Bohrung 50mm - Tasche ausraemen
; ID: bohrung50
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
; CIRCULAR POCKET CLEARING
; ============================================
; Durchmesser: 50mm, Tiefe: 12mm
; Passes: 3, Zustellung: 4.0mm pro Pass
; Spiralabstand: 2.52mm

; Pass 1: Z = -4.00mm
G0 Z2.0
G0 X23.425 Y0.0
G1 Z-4.0 F450
G2 X23.425 Y0.0 I-23.425 J0.0 F450
G1 X20.905 Y0.0 F450
G2 X20.905 Y0.0 I-20.905 J0.0 F450
G1 X18.385 Y0.0 F450
G2 X18.385 Y0.0 I-18.385 J0.0 F450
G1 X15.865 Y0.0 F450
G2 X15.865 Y0.0 I-15.865 J0.0 F450
G1 X13.345 Y0.0 F450
G2 X13.345 Y0.0 I-13.345 J0.0 F450
G1 X10.825 Y0.0 F450
G2 X10.825 Y0.0 I-10.825 J0.0 F450
G1 X8.305 Y0.0 F450
G2 X8.305 Y0.0 I-8.305 J0.0 F450
G1 X5.785 Y0.0 F450
G2 X5.785 Y0.0 I-5.785 J0.0 F450
G1 X3.265 Y0.0 F450
G2 X3.265 Y0.0 I-3.265 J0.0 F450

; Pass 2: Z = -8.00mm
G0 Z2.0
G0 X23.425 Y0.0
G1 Z-8.0 F450
G1 X23.425 Y0.0 F450
G2 X23.425 Y0.0 I-23.425 J0.0 F450
G1 X20.905 Y0.0 F450
G2 X20.905 Y0.0 I-20.905 J0.0 F450
G1 X18.385 Y0.0 F450
G2 X18.385 Y0.0 I-18.385 J0.0 F450
G1 X15.865 Y0.0 F450
G2 X15.865 Y0.0 I-15.865 J0.0 F450
G1 X13.345 Y0.0 F450
G2 X13.345 Y0.0 I-13.345 J0.0 F450
G1 X10.825 Y0.0 F450
G2 X10.825 Y0.0 I-10.825 J0.0 F450
G1 X8.305 Y0.0 F450
G2 X8.305 Y0.0 I-8.305 J0.0 F450
G1 X5.785 Y0.0 F450
G2 X5.785 Y0.0 I-5.785 J0.0 F450
G1 X3.265 Y0.0 F450
G2 X3.265 Y0.0 I-3.265 J0.0 F450

; Pass 3: Z = -12.00mm
G0 Z2.0
G0 X23.425 Y0.0
G1 Z-12.0 F450
G1 X23.425 Y0.0 F450
G2 X23.425 Y0.0 I-23.425 J0.0 F450
G1 X20.905 Y0.0 F450
G2 X20.905 Y0.0 I-20.905 J0.0 F450
G1 X18.385 Y0.0 F450
G2 X18.385 Y0.0 I-18.385 J0.0 F450
G1 X15.865 Y0.0 F450
G2 X15.865 Y0.0 I-15.865 J0.0 F450
G1 X13.345 Y0.0 F450
G2 X13.345 Y0.0 I-13.345 J0.0 F450
G1 X10.825 Y0.0 F450
G2 X10.825 Y0.0 I-10.825 J0.0 F450
G1 X8.305 Y0.0 F450
G2 X8.305 Y0.0 I-8.305 J0.0 F450
G1 X5.785 Y0.0 F450
G2 X5.785 Y0.0 I-5.785 J0.0 F450
G1 X3.265 Y0.0 F450
G2 X3.265 Y0.0 I-3.265 J0.0 F450

; ============================================
; PROGRAM ENDE
; ============================================
G0 Z2.0
G0 X0.0 Y0.0
M5                           ; Spindle OFF
M30                          ; Program end
