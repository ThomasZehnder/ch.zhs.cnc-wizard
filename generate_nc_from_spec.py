#!/usr/bin/env python3
"""
NC-Generator basierend auf spec_cnc.md
Parst die Spezifikation und generiert alle NC-Dateien
"""
import math
import re

# Konfiguration (geparst aus spec_cnc.md)
CONFIG = {
    "feed_rate": 450,
    "spindle_speed": 4000,
    "safety_height": 2.0,
    "depth_per_pass": 4.0,
    "raster_spacing": 2.52,  # 80% von 3.15mm
    "tool_diameter": 3.15,
}

PROGRAMS = {
    "mulde35x35": {
        "filename": "mulde35x35.nc",
        "description": "4 abgerundete Quadrate - Tasche ausraemen",
        "num_contours": 4,
        "contour_size": 35.0,
        "corner_radius": 10.0,
        "positions": [
            (0, 50),      # 0°
            (50, 0),      # 90°
            (0, -50),     # 180°
            (-50, 0),     # 270°
        ],
        "depth": 6.0,
        "use_raster": True,
        "consider_corner_radius": True,
    }
}

def generate_header(f):
    """Generiert den G-Code Header"""
    f.write("; ============================================\n")
    f.write("; G-CODE INITIALISIERUNG\n")
    f.write("; ============================================\n")
    f.write("G0                           ; Rapid positioning (Eilgang)\n")
    f.write("G21                          ; Metric units (mm)\n")
    f.write("G40                          ; Cancel tool radius compensation\n")
    f.write("G49                          ; Cancel tool offset\n")
    f.write("G17                          ; XY-Plane (Arbeitsebene XY)\n")
    f.write("G80                          ; Cancel canned cycles\n")
    f.write("G50                          ; Cancel scaling\n")
    f.write("G90                          ; Absolute positioning\n\n")

    f.write("; ============================================\n")
    f.write("; WERKZEUG- UND SPINDELEINSTELLUNGEN\n")
    f.write("; ============================================\n")
    f.write("M6 T7                        ; Tool change: T7 (D3.15mm)\n")
    f.write(f"S{CONFIG['spindle_speed']}                        ; Spindle speed: {CONFIG['spindle_speed']} RPM\n")
    f.write("M3                           ; Spindle ON (clockwise)\n")
    f.write("G4 P2.0                      ; Dwell 2 seconds\n\n")

def generate_pocket(f, program, config):
    """Generiert ein Taschen-Fräsprogramm mit Kontur + spiralfoermig nach innen"""

    f.write("; ============================================\n")
    f.write("; POCKET CLEARING - Kontur mit Spirale\n")
    f.write("; ============================================\n")

    size = program["contour_size"]
    corner_radius = program["corner_radius"]
    depth = program["depth"]
    half_size = size / 2.0
    tool_radius = config["tool_diameter"] / 2.0
    spiral_step = config["raster_spacing"]  # 2.52mm

    # Berechne Anzahl der Passes
    num_passes = math.ceil(depth / config["depth_per_pass"])

    f.write(f"; Konturen: {program['num_contours']}, Tiefe: {depth}mm\n")
    f.write(f"; Passes: {num_passes}, Zustellung: {config['depth_per_pass']}mm pro Pass\n")
    f.write(f"; Spiralschritt: {spiral_step:.2f}mm\n\n")

    # Für jede Kontur
    for contour_idx, (center_x, center_y) in enumerate(program["positions"], 1):
        f.write(f"; === Kontur {contour_idx}: X={center_x}, Y={center_y} ===\n")

        # Für jeden Pass
        for pass_num in range(1, num_passes + 1):
            current_depth = pass_num * config["depth_per_pass"]
            if current_depth > depth:
                current_depth = depth

            z_depth = -current_depth

            f.write(f"; Pass {pass_num}: Z = {z_depth:.2f}mm\n")

            # Rapid zu Sicherheitshoehe
            f.write(f"G0 Z{config['safety_height']}\n")

            # Zu Startpunkt (Kontur-Zentrum)
            f.write(f"G0 X{center_x} Y{center_y}\n")

            # Runterfahren mit Vorschub
            f.write(f"G1 Z{z_depth:.2f} F{config['feed_rate']}\n")

            # Spiralfoermig nach innen: konzentrische Rechtecke mit abgerundeten Ecken
            # Stoppe wenn Durchmesser < 1.5x Tool-Durchmesser (Vereinfachung im Zentrum)
            min_size = config["tool_diameter"] * 0.75
            spiral_offset = 0
            half_size_current = half_size

            while half_size_current > min_size:
                x_min = center_x - half_size_current + tool_radius
                x_max = center_x + half_size_current - tool_radius
                y_min = center_y - half_size_current + tool_radius
                y_max = center_y + half_size_current - tool_radius

                # Kontur nachfahren mit abgerundeten Ecken (Boegen nach AUSSEN)
                # Start: unten-links
                f.write(f"G1 X{x_min + corner_radius} Y{y_min} F{config['feed_rate']}\n")

                # Unten-Rechts (Bogen nach aussen - CCW)
                f.write(f"G1 X{x_max - corner_radius} Y{y_min} F{config['feed_rate']}\n")
                f.write(f"G3 X{x_max} Y{y_min + corner_radius} I0 J{corner_radius} F{config['feed_rate']}\n")

                # Rechts-Oben (Bogen nach aussen - CCW)
                f.write(f"G1 X{x_max} Y{y_max - corner_radius} F{config['feed_rate']}\n")
                f.write(f"G3 X{x_max - corner_radius} Y{y_max} I{-corner_radius} J0 F{config['feed_rate']}\n")

                # Oben-Links (Bogen nach aussen - CCW)
                f.write(f"G1 X{x_min + corner_radius} Y{y_max} F{config['feed_rate']}\n")
                f.write(f"G3 X{x_min} Y{y_max - corner_radius} I0 J{-corner_radius} F{config['feed_rate']}\n")

                # Links-Unten (Bogen nach aussen - CCW)
                f.write(f"G1 X{x_min} Y{y_min + corner_radius} F{config['feed_rate']}\n")
                f.write(f"G3 X{x_min + corner_radius} Y{y_min} I{corner_radius} J0 F{config['feed_rate']}\n")

                # Nächste Spirale nach innen
                half_size_current -= spiral_step

            f.write("\n")

    # Finish
    f.write("; ============================================\n")
    f.write("; PROGRAM ENDE\n")
    f.write("; ============================================\n")
    f.write(f"G0 Z{config['safety_height']}\n")
    f.write("G0 X0 Y0\n")
    f.write("M5                           ; Spindle OFF\n")
    f.write("M30                          ; Program end\n")

def generate_program(program_id, program_spec, config):
    """Generiert ein NC-Programm"""

    filename = program_spec["filename"]
    output_path = f'd:\\Arduino\\force-sensor\\messplatte-ir-160-p\\{filename}'

    with open(output_path, 'w') as f:
        f.write("; ============================================\n")
        f.write(f"; {program_spec['description']}\n")
        f.write(f"; ID: {program_id}\n")
        f.write("; Generated for MACH3\n")
        f.write("; ============================================\n\n")

        generate_header(f)
        generate_pocket(f, program_spec, config)

    print(f"NC file created: {output_path}")

# Main
if __name__ == "__main__":
    for program_id, program_spec in PROGRAMS.items():
        generate_program(program_id, program_spec, CONFIG)

    print("\nAll NC files generated successfully!")
