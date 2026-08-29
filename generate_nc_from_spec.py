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
            (0, 60),      # 0° - 60mm vom Zentrum
            (60, 0),      # 90° - 60mm vom Zentrum
            (0, -60),     # 180° - 60mm vom Zentrum
            (-60, 0),     # 270° - 60mm vom Zentrum
        ],
        "depth": 6.0,
        "use_raster": True,
        "consider_corner_radius": True,
    },
    "mulde27x27": {
        "filename": "mulde27x27.nc",
        "description": "4 abgerundete Quadrate - Tasche ausraemen",
        "num_contours": 4,
        "contour_size": 27.0,
        "corner_radius": 4.0,
        "positions": [
            (0, 50),      # 0° - 50mm vom Zentrum
            (50, 0),      # 90° - 50mm vom Zentrum
            (0, -50),     # 180° - 50mm vom Zentrum
            (-50, 0),     # 270° - 50mm vom Zentrum
        ],
        "depth": 8.0,
        "use_raster": True,
        "consider_corner_radius": True,
    },
    "bohrung50": {
        "filename": "bohrung50.nc",
        "description": "Bohrung 50mm - Tasche ausraemen",
        "num_contours": 1,
        "type": "circle",
        "diameter": 50.0,
        "center": (0, 0),
        "depth": 12.0,
        "use_spiral": True,
    },
    "ring110_160": {
        "filename": "ring110_160.nc",
        "description": "Ring innen 110, aussen 160mm - Tasche ausraemen",
        "num_contours": 1,
        "type": "ring",
        "diameter_inner": 110.0,
        "diameter_outer": 160.0,
        "center": (0, 0),
        "depth": 6.0,
        "use_spiral": True,
    },
    "ring160_200": {
        "filename": "ring160_200.nc",
        "description": "Ring innen 160, aussen 200mm - Tasche ausraemen",
        "num_contours": 1,
        "type": "ring",
        "diameter_inner": 160.0,
        "diameter_outer": 200.0,
        "center": (0, 0),
        "depth": 6.0,
        "use_spiral": True,
    },
    "bohrung_4x50": {
        "filename": "bohrung_4x50.nc",
        "description": "4 Bohrungen - Position 45/135/225/315 im Abstand 50mm",
        "num_contours": 4,
        "type": "multi_circle",
        "angles": [45, 135, 225, 315],
        "distance": 50.0,
        "depth": 6.0,
    },
    "kreis_200_aussen": {
        "filename": "kreis_200_aussen.nc",
        "description": "Kreis 200mm - Aussenkontur",
        "num_contours": 1,
        "type": "circle_with_correction",
        "diameter": 200.0,
        "center": (0, 0),
        "depth": 12.0,
        "radius_correction": "aussen",
    },
    "kreis_80_innen": {
        "filename": "kreis_80_innen.nc",
        "description": "Kreis 80mm - Innenkontur",
        "num_contours": 1,
        "type": "circle_with_correction",
        "diameter": 80.0,
        "center": (0, 0),
        "depth": 12.0,
        "radius_correction": "innen",
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

            # Zu Startpunkt auf der KONTUR fahren (Werkzeugradius-korrigiert)
            # Anfang der geraden Seite unten, mit Werkzeugradius-Offset
            start_x = center_x + half_size - corner_radius - tool_radius
            start_y = center_y - half_size + tool_radius
            f.write(f"G0 X{start_x} Y{start_y}\n")

            # Runterfahren mit Vorschub
            f.write(f"G1 Z{z_depth:.2f} F{config['feed_rate']}\n")

            # Spiralfoermig nach innen: konzentrische Rechtecke mit abgerundeten Ecken
            # Wechsle zu Kreisen wenn gerade Seite < Tool-Durchmesser wird
            min_straight_length = config["tool_diameter"]
            spiral_offset = 0
            half_size_current = half_size
            use_circles = False

            while half_size_current > tool_radius:
                x_min = center_x - half_size_current + tool_radius
                x_max = center_x + half_size_current - tool_radius
                y_min = center_y - half_size_current + tool_radius
                y_max = center_y + half_size_current - tool_radius

                # Pruefe ob gerade Seiten noch sinnvoll sind
                straight_length = x_max - x_min - 2 * corner_radius

                if straight_length < min_straight_length:
                    use_circles = True

                if use_circles:
                    # Nur noch Kreise fahren
                    f.write(f"G1 X{center_x + half_size_current} Y{center_y} F{config['feed_rate']}\n")
                    f.write(f"G2 X{center_x + half_size_current} Y{center_y} I{-half_size_current} J0 F{config['feed_rate']}\n")
                else:
                    # Kontur mit abgerundeten Ecken fahren
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

def generate_ring_pocket(f, program, config):
    """Generiert ein ringfoermiges Taschenprogramm"""

    f.write("; ============================================\n")
    f.write("; RING POCKET CLEARING\n")
    f.write("; ============================================\n")

    diameter_outer = program["diameter_outer"]
    diameter_inner = program["diameter_inner"]
    radius_outer = diameter_outer / 2.0
    radius_inner = diameter_inner / 2.0
    depth = program["depth"]
    center_x, center_y = program["center"]
    tool_radius = config["tool_diameter"] / 2.0

    # Berechne Anzahl der Passes
    num_passes = math.ceil(depth / config["depth_per_pass"])

    f.write(f"; Aussendurchmesser: {diameter_outer}mm, Innendurchmesser: {diameter_inner}mm\n")
    f.write(f"; Tiefe: {depth}mm, Passes: {num_passes}, Zustellung: {config['depth_per_pass']}mm pro Pass\n")
    f.write(f"; Spiralabstand: {config['raster_spacing']:.2f}mm\n\n")

    # Für jeden Pass
    for pass_num in range(1, num_passes + 1):
        current_depth = pass_num * config["depth_per_pass"]
        if current_depth > depth:
            current_depth = depth

        z_depth = -current_depth

        f.write(f"; Pass {pass_num}: Z = {z_depth:.2f}mm\n")

        # Rapid zu Sicherheitshoehe
        f.write(f"G0 Z{config['safety_height']}\n")

        # Zu Startpunkt auf der AUSSEN-Kontur fahren
        start_radius = radius_outer - tool_radius
        f.write(f"G0 X{center_x + start_radius} Y{center_y}\n")

        # Runterfahren mit Vorschub
        f.write(f"G1 Z{z_depth:.2f} F{config['feed_rate']}\n")

        # Spiralfoermig: konzentrische Kreise von aussen nach innen (bis Innendurchmesser)
        circle_radius = radius_outer - tool_radius
        min_radius = radius_inner + tool_radius

        while circle_radius > min_radius:
            # Zu Startpunkt des Kreises fahren (falls nicht bereits dort)
            if circle_radius != start_radius or pass_num > 1:
                f.write(f"G1 X{center_x + circle_radius} Y{center_y} F{config['feed_rate']}\n")

            # Kreis fahren (G2 = clockwise)
            f.write(f"G2 X{center_x + circle_radius} Y{center_y} I{-circle_radius} J0 F{config['feed_rate']}\n")

            # Nächster Kreis nach innen
            circle_radius -= config["raster_spacing"]
            start_radius = circle_radius

        f.write("\n")

    # Finish
    f.write("; ============================================\n")
    f.write("; PROGRAM ENDE\n")
    f.write("; ============================================\n")
    f.write(f"G0 Z{config['safety_height']}\n")
    f.write("G0 X0 Y0\n")
    f.write("M5                           ; Spindle OFF\n")
    f.write("M30                          ; Program end\n")

def generate_multi_circle_pockets(f, program, config):
    """Generiert mehrere senkrechte Bohrungen an verschiedenen Positionen"""

    f.write("; ============================================\n")
    f.write("; MULTIPLE BOREHOLES (senkrecht)\n")
    f.write("; ============================================\n")

    depth = program["depth"]
    angles = program["angles"]
    distance = program["distance"]

    # Berechne Anzahl der Passes
    num_passes = math.ceil(depth / config["depth_per_pass"])

    f.write(f"; Anzahl Bohrungen: {len(angles)}, Tiefe: {depth}mm\n")
    f.write(f"; Positionen: {angles}°, Abstand: {distance}mm vom Zentrum\n")
    f.write(f"; Passes: {num_passes}, Zustellung: {config['depth_per_pass']}mm pro Pass\n\n")

    # Für jede Bohrung
    for hole_idx, angle_deg in enumerate(angles, 1):
        f.write(f"; === Bohrung {hole_idx}: {angle_deg}° ===\n")

        angle_rad = math.radians(angle_deg)
        center_x = distance * math.cos(angle_rad)
        center_y = distance * math.sin(angle_rad)

        # Für jeden Pass
        for pass_num in range(1, num_passes + 1):
            current_depth = pass_num * config["depth_per_pass"]
            if current_depth > depth:
                current_depth = depth

            z_depth = -current_depth

            f.write(f"; Pass {pass_num}: Z = {z_depth:.2f}mm\n")

            # Rapid zu Sicherheitshoehe
            f.write(f"G0 Z{config['safety_height']}\n")

            # Zu Bohrungsmittelpunkt fahren
            f.write(f"G0 X{center_x} Y{center_y}\n")

            # Senkrecht absenken mit Vorschub
            f.write(f"G1 Z{z_depth:.2f} F{config['feed_rate']}\n")

            f.write("\n")

    # Finish
    f.write("; ============================================\n")
    f.write("; PROGRAM ENDE\n")
    f.write("; ============================================\n")
    f.write(f"G0 Z{config['safety_height']}\n")
    f.write("G0 X0 Y0\n")
    f.write("M5                           ; Spindle OFF\n")
    f.write("M30                          ; Program end\n")

def generate_circle_with_correction(f, program, config):
    """Generiert einen Kreis mit Radiuskorrektur (aussen/innen)"""

    f.write("; ============================================\n")
    f.write("; CIRCLE WITH RADIUS CORRECTION\n")
    f.write("; ============================================\n")

    diameter = program["diameter"]
    radius = diameter / 2.0
    depth = program["depth"]
    center_x, center_y = program["center"]
    tool_radius = config["tool_diameter"] / 2.0
    radius_correction = program["radius_correction"]

    # Berechne Anzahl der Passes
    num_passes = math.ceil(depth / config["depth_per_pass"])

    f.write(f"; Durchmesser: {diameter}mm, Tiefe: {depth}mm\n")
    f.write(f"; Radiuskorrektur: {radius_correction}\n")
    f.write(f"; Passes: {num_passes}, Zustellung: {config['depth_per_pass']}mm pro Pass\n\n")

    # Für jeden Pass
    for pass_num in range(1, num_passes + 1):
        current_depth = pass_num * config["depth_per_pass"]
        if current_depth > depth:
            current_depth = depth

        z_depth = -current_depth

        f.write(f"; Pass {pass_num}: Z = {z_depth:.2f}mm\n")

        # Rapid zu Sicherheitshoehe
        f.write(f"G0 Z{config['safety_height']}\n")

        # Startpunkt je nach Radiuskorrektur
        if radius_correction == "aussen":
            # Aussen: Werkzeug ist ausserhalb des Kreises
            start_radius = radius + tool_radius
        else:  # innen
            # Innen: Werkzeug ist innerhalb des Kreises
            start_radius = radius - tool_radius

        f.write(f"G0 X{center_x + start_radius} Y{center_y}\n")

        # Runterfahren mit Vorschub
        f.write(f"G1 Z{z_depth:.2f} F{config['feed_rate']}\n")

        # Einen Kreis fahren
        f.write(f"G2 X{center_x + start_radius} Y{center_y} I{-start_radius} J0 F{config['feed_rate']}\n")

        f.write("\n")

    # Finish
    f.write("; ============================================\n")
    f.write("; PROGRAM ENDE\n")
    f.write("; ============================================\n")
    f.write(f"G0 Z{config['safety_height']}\n")
    f.write("G0 X0 Y0\n")
    f.write("M5                           ; Spindle OFF\n")
    f.write("M30                          ; Program end\n")

def generate_circle_pocket(f, program, config):
    """Generiert ein kreisfoermiges Taschenprogramm"""

    f.write("; ============================================\n")
    f.write("; CIRCULAR POCKET CLEARING\n")
    f.write("; ============================================\n")

    diameter = program["diameter"]
    radius = diameter / 2.0
    depth = program["depth"]
    center_x, center_y = program["center"]
    tool_radius = config["tool_diameter"] / 2.0

    # Berechne Anzahl der Passes
    num_passes = math.ceil(depth / config["depth_per_pass"])

    f.write(f"; Durchmesser: {diameter}mm, Tiefe: {depth}mm\n")
    f.write(f"; Passes: {num_passes}, Zustellung: {config['depth_per_pass']}mm pro Pass\n")
    f.write(f"; Spiralabstand: {config['raster_spacing']:.2f}mm\n\n")

    # Für jeden Pass
    for pass_num in range(1, num_passes + 1):
        current_depth = pass_num * config["depth_per_pass"]
        if current_depth > depth:
            current_depth = depth

        z_depth = -current_depth

        f.write(f"; Pass {pass_num}: Z = {z_depth:.2f}mm\n")

        # Rapid zu Sicherheitshoehe
        f.write(f"G0 Z{config['safety_height']}\n")

        # Zu Startpunkt auf der AUSSEN-Kontur fahren
        start_radius = radius - tool_radius
        f.write(f"G0 X{center_x + start_radius} Y{center_y}\n")

        # Runterfahren mit Vorschub
        f.write(f"G1 Z{z_depth:.2f} F{config['feed_rate']}\n")

        # Spiralfoermig: konzentrische Kreise von aussen nach innen
        circle_radius = radius - tool_radius
        min_radius = tool_radius

        while circle_radius > min_radius:
            # Zu Startpunkt des Kreises fahren (falls nicht bereits dort)
            if circle_radius != start_radius or pass_num > 1:
                f.write(f"G1 X{center_x + circle_radius} Y{center_y} F{config['feed_rate']}\n")

            # Kreis fahren (G2 = clockwise)
            f.write(f"G2 X{center_x + circle_radius} Y{center_y} I{-circle_radius} J0 F{config['feed_rate']}\n")

            # Nächster Kreis nach innen
            circle_radius -= config["raster_spacing"]

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

        # Unterscheide zwischen verschiedenen Typen
        if program_spec.get("type") == "multi_circle":
            generate_multi_circle_pockets(f, program_spec, config)
        elif program_spec.get("type") == "circle_with_correction":
            generate_circle_with_correction(f, program_spec, config)
        elif program_spec.get("type") == "circle":
            generate_circle_pocket(f, program_spec, config)
        elif program_spec.get("type") == "ring":
            generate_ring_pocket(f, program_spec, config)
        else:
            generate_pocket(f, program_spec, config)

    print(f"NC file created: {output_path}")

# Main
if __name__ == "__main__":
    for program_id, program_spec in PROGRAMS.items():
        generate_program(program_id, program_spec, CONFIG)

    print("\nAll NC files generated successfully!")
