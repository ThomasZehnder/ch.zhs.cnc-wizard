; ============================================
; Ring innen 110mm, aussen 160mm - Tasche ausraemen
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
