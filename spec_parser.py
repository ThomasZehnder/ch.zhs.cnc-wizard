#!/usr/bin/env python3
"""
Gemeinsamer Parser für spec_cnc.md
Wird von generate_nc_from_spec.py und generate_dxf_from_spec.py verwendet
"""
import re
import math


def normalize_corner_radius(value):
    """Normalisiert Eckradius: Default 3mm wenn nicht vorhanden oder null/0"""
    if value is None or value == 0:
        return 3.0
    return value


def parse_spec_cnc(filename):
    """Parst die standardisierte spec_cnc.md und generiert NC-Programme Dictionary"""
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
            filename_prog = None
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
                    filename_prog = line.split(':', 1)[1].strip().strip('*').strip()
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
            if identifier and filename_prog:
                program = {
                    "filename": filename_prog,
                    "description": description,
                    "type": prog_type,
                }
                program.update(params)
                programs[identifier] = program

            continue

        i += 1

    return programs


def parse_dxf_spec(filename):
    """Parst die DXF-Spezifikation aus spec_cnc.md"""
    dxf_spec = {}

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrahiere DXF-Spezifikation
    dxf_section = re.search(r'## DXF-Spezifikation(.*?)## G-Code Header', content, re.DOTALL)
    if not dxf_section:
        return None

    dxf_text = dxf_section.group(1)

    # Allgemeine Parameter
    filename_match = re.search(r'\*\*Filename:\*\*\s+(.+)', dxf_text)
    if filename_match:
        dxf_spec['filename'] = filename_match.group(1).strip()

    format_match = re.search(r'\*\*Format:\*\*\s+(.+)', dxf_text)
    if format_match:
        dxf_spec['format'] = format_match.group(1).strip()

    # Kreis-Labels
    circle_labels_section = re.search(r'#### Kreis-Labels(.*?)(?:####|$)', dxf_text, re.DOTALL)
    if circle_labels_section:
        section = circle_labels_section.group(1)
        dxf_spec['circle_labels'] = {}

        diameter_match = re.search(r'- Durchmesser: (.+)', section)
        if diameter_match:
            diameter_str = diameter_match.group(1).strip()
            diameters = [int(re.sub(r'[^0-9]', '', x)) for x in diameter_str.split(',')]
            dxf_spec['circle_labels']['diameters'] = diameters

        distance_match = re.search(r'- Abstand zum Kreis: ([\d.]+)mm', section)
        if distance_match:
            dxf_spec['circle_labels']['distance'] = float(distance_match.group(1))

        position_match = re.search(r'- Position: (\d+)°', section)
        if position_match:
            dxf_spec['circle_labels']['position'] = int(position_match.group(1))

        fontsize_match = re.search(r'- Schriftgröße: ([\d.]+)mm', section)
        if fontsize_match:
            dxf_spec['circle_labels']['fontsize'] = float(fontsize_match.group(1))

    # Titel
    title_section = re.search(r'#### Titel-Label(.*?)(?:####|$)', dxf_text, re.DOTALL)
    if title_section:
        section = title_section.group(1)
        dxf_spec['title'] = {}

        text_match = re.search(r'- Text: "(.+?)"', section)
        if text_match:
            dxf_spec['title']['text'] = text_match.group(1)

        position_match = re.search(r'- Position: (\d+)°', section)
        if position_match:
            dxf_spec['title']['position'] = int(position_match.group(1))

        distance_match = re.search(r'- Abstand vom Zentrum: ([\d.]+)mm', section)
        if distance_match:
            dxf_spec['title']['distance'] = float(distance_match.group(1))

        fontsize_match = re.search(r'- Schriftgröße: ([\d.]+)mm', section)
        if fontsize_match:
            dxf_spec['title']['fontsize'] = float(fontsize_match.group(1))

    return dxf_spec
