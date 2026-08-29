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

def parse_spec_cnc(filename):
    """Parst die standardisierte spec_cnc.md und generiert PROGRAMS Dictionary"""
    # Mapping von Markdown-Parameternamen zu Python-Schlüsseln
    param_mapping = {
        "Anzahl Konturen": "num_contours",
        "Kontur Groesse": "contour_size",
        "Eckradius": "corner_radius",
        "Positionen": "positions",
        "Abstand vom Zentrum": "distance_from_center",
        "Taschentiefe": "pocket_depth",
        "Anzahl Bohrungen": "num_holes",
        "Bohrungstiefe": "hole_depth",
        "Durchmesser": "diameter",
        "Durchmesser Innen": "diameter_inner",
        "Durchmesser Aussen": "diameter_outer",
        "Radiuskorrektur": "radius_correction",
    }

    # Gültige Werte für Radiuskorrektur
    valid_radius_corrections = {"keine", "innen", "aussen", "inner", "outer"}

    programs = {}

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Suche nach Programm-Sektionen (### Name)
        if line.startswith('### '):
            program_name = line[4:].strip()
            identifier = None
            filename = None
            prog_type = None
            description = None
            params = {}

            # Lese nächste Zeilen für Metadaten
            i += 1
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith('**Identifier:**'):
                    identifier = line.split(':', 1)[1].strip().strip('*').strip()
                elif line.startswith('**Filename:**'):
                    filename = line.split(':', 1)[1].strip().strip('*').strip()
                elif line.startswith('**Type:**'):
                    prog_type = line.split(':', 1)[1].strip().strip('*').strip()
                elif line.startswith('**Description:**'):
                    description = line.split(':', 1)[1].strip().strip('*').strip()
                elif line.startswith('**Parameters:**'):
                    # Parse alle Parameter-Zeilen
                    i += 1
                    while i < len(lines):
                        param_line = lines[i].strip()

                        if param_line.startswith('- ') and ':' in param_line:
                            param_line = param_line[2:].strip()
                            key, value = param_line.split(':', 1)
                            key = key.strip()
                            value = value.strip()

                            # Konvertiere Markdown-Namen zu Python-Namen
                            python_key = param_mapping.get(key, key.lower().replace(' ', '_'))

                            # Konvertiere zu Python-Typen
                            if value.lower() in ('ja', 'true'):
                                params[python_key] = True
                            elif value.lower() in ('nein', 'false'):
                                params[python_key] = False
                            elif '°' in value:
                                # Winkel: "0°, 90°, 180°, 270°"
                                params[python_key] = [int(re.sub(r'[°\s]', '', x)) for x in value.split(',')]
                            else:
                                # Entferne 'mm' suffix und versuche zu konvertieren
                                clean_value = re.sub(r'mm\s*$', '', value).strip()
                                if clean_value.isdigit():
                                    params[python_key] = int(clean_value)
                                elif re.match(r'^-?\d+\.?\d*$', clean_value):
                                    params[python_key] = float(clean_value)
                                else:
                                    params[python_key] = value
                        elif param_line.startswith('---') or param_line.startswith('###'):
                            break
                        elif param_line == '':
                            pass
                        else:
                            break

                        i += 1

                    break

                i += 1

            # Erstelle Programm-Dict
            if identifier and filename:
                program = {
                    "filename": filename,
                    "description": description,
                    "type": prog_type,
                }
                program.update(params)
                programs[identifier] = program

            continue

        i += 1

    return programs

# Programme aus spec_cnc.md parsen
PROGRAMS = parse_spec_cnc('spec_cnc.md')

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

def generate_circle_with_correction(f, program, config):
    """Generiert einen Kreis mit Radiuskorrektur (aussen/innen) - nur ein Kreis pro Pass"""

    f.write("; ============================================\n")
    f.write("; CIRCLE WITH RADIUS CORRECTION\n")
    f.write("; ============================================\n")

    diameter = program["diameter"]
    radius = diameter / 2.0
    depth = program["depth"]
    center_x, center_y = program["center"]
    tool_radius = config["tool_diameter"] / 2.0
    radius_correction = program.get("radius_correction", "outer")

    # Berechne Anzahl der Passes
    num_passes = math.ceil(depth / config["depth_per_pass"])

    # Bestimme Display-Text
    if radius_correction == "outer" or radius_correction == "aussen":
        display_correction = "aussen"
    else:
        display_correction = "innen"

    f.write(f"; Durchmesser: {diameter:.1f}mm, Tiefe: {depth:.1f}mm\n")
    f.write(f"; Radiuskorrektur: {display_correction}\n")
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
        if radius_correction == "outer" or radius_correction == "aussen":
            # Aussen: Werkzeug ist ausserhalb des Kreises
            start_radius = radius + tool_radius
        else:  # innen / inner
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

def generate_program(program_id, program_spec, config):
    """Generiert ein NC-Programm"""

    filename = program_spec["filename"]
    output_path = f'd:\\Arduino\\force-sensor\\messplatte-ir-160-p\\{filename}'

    # Normalisiere Parameter für Funktionen
    normalized = program_spec.copy()

    # Vereinheitliche Depth-Parameter
    if "pocket_depth" in normalized:
        normalized["depth"] = normalized["pocket_depth"]
    if "hole_depth" in normalized:
        normalized["depth"] = normalized["hole_depth"]

    # Vereinheitliche Distance-Parameter
    if "distance_from_center" in normalized:
        normalized["distance"] = normalized["distance_from_center"]

    # Vereinheitliche Positions-Parameter
    if "positions" in normalized:
        angles = normalized["positions"]
        distance = normalized.get("distance_from_center", 0)

        # Speichere die ursprünglichen Winkel
        normalized["angles"] = angles

        # Konvertiere Winkel zu (x, y) Koordinaten
        positions = []
        for angle in angles:
            rad = math.radians(angle)
            x = distance * math.cos(rad)
            y = distance * math.sin(rad)
            positions.append((x, y))
        normalized["positions"] = positions

    # Für single-center Programme: center = positions[0] oder (0, 0)
    if "positions" in normalized and len(normalized["positions"]) > 0:
        normalized["center"] = normalized["positions"][0]
    elif "distance_from_center" in normalized:
        normalized["center"] = (0, 0)

    with open(output_path, 'w') as f:
        f.write("; ============================================\n")
        f.write(f"; {program_spec['description']}\n")
        f.write(f"; ID: {program_id}\n")
        f.write("; Generated for MACH3\n")
        f.write("; ============================================\n\n")

        generate_header(f)

        # Unterscheide zwischen verschiedenen Typen
        prog_type = program_spec.get("type", "").strip()
        if prog_type == "pocket_square":
            generate_pocket(f, normalized, config)
        elif prog_type == "circle_pocket":
            generate_circle_pocket(f, normalized, config)
        elif prog_type == "circle":
            # Nutze radius_correction Parameter um zu entscheiden
            radius_corr = normalized.get("radius_correction", "keine").lower()
            if radius_corr in ("aussen", "outer"):
                normalized["radius_correction"] = "aussen"
                generate_circle_with_correction(f, normalized, config)
            elif radius_corr in ("innen", "inner"):
                normalized["radius_correction"] = "innen"
                generate_circle_with_correction(f, normalized, config)
            else:
                # keine Radiuskorrektur - verwende circle_pocket
                generate_circle_pocket(f, normalized, config)
        elif prog_type == "ring_pocket":
            generate_ring_pocket(f, normalized, config)
        elif prog_type == "multi_circle_drill":
            generate_multi_circle_pockets(f, normalized, config)
        else:
            generate_pocket(f, normalized, config)

    print(f"NC file created: {output_path}")

# Main
if __name__ == "__main__":
    PROGRAMS = parse_spec_cnc('spec_cnc.md')
    for program_id, program_spec in PROGRAMS.items():
        generate_program(program_id, program_spec, CONFIG)

    print("\nAll NC files generated successfully!")
