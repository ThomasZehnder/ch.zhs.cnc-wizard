; ============================================
; Kreis 200mm - Aussenkontur
; ID: kreis_200_aussen
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
; CIRCLE WITH RADIUS CORRECTION
; ============================================
; Durchmesser: 200.0mm, Tiefe: 12.0mm
; Radiuskorrektur: aussen
; Passes: 3, Zustellung: 4.0mm pro Pass

; Pass 1: Z = -4.00mm
G0 Z2.0
G0 X101.575 Y0
G1 Z-4.00 F450
G2 X101.575 Y0 I-101.575 J0 F450

; Pass 2: Z = -8.00mm
G0 Z2.0
G0 X101.575 Y0
G1 Z-8.00 F450
G2 X101.575 Y0 I-101.575 J0 F450

; Pass 3: Z = -12.00mm
G0 Z2.0
G0 X101.575 Y0
G1 Z-12.00 F450
G2 X101.575 Y0 I-101.575 J0 F450

; ============================================
; PROGRAM ENDE
; ============================================
G0 Z2.0
G0 X0 Y0
M5                           ; Spindle OFF
M30                          ; Program end
