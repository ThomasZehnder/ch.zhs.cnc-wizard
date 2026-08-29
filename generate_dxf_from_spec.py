#!/usr/bin/env python3
"""
DXF-Generator basierend auf spec_cnc.md
Parst die Spezifikation und generiert die DXF-Zeichnung
"""
import math
import re

# Importiere den Parser aus generate_nc_from_spec
import sys
sys.path.insert(0, '.')
from generate_nc_from_spec import parse_spec_cnc

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

def generate_dxf(dxf_spec, nc_programs):
    """Generiert DXF-Datei basierend auf Spezifikation"""
    output_path = dxf_spec.get('filename', 'messplatte_160P.dxf')

    with open(output_path, 'w') as f:
        f.write("""  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  0
ENDSEC
  0
SECTION
  2
TABLES
  0
TABLE
  2
LAYER
 70
1
  0
LAYER
  2
0
 70
0
 62
7
  6
CONTINUOUS
  0
ENDTAB
  0
ENDTAB
  0
ENDSEC
  0
SECTION
  2
BLOCKS
  0
ENDBLK
  0
ENDBLK
  0
ENDSEC
  0
SECTION
  2
ENTITIES
""")

        # Kreise: 200mm, 160mm, 110mm, 50mm
        circle_diameters = [200.0, 160.0, 110.0, 50.0]
        for diameter in circle_diameters:
            radius = diameter / 2.0
            f.write(f"""  0
CIRCLE
  8
0
 10
0.0
 20
0.0
 40
{radius}
""")

        # Kreis-Labels
        if 'circle_labels' in dxf_spec:
            labels = dxf_spec['circle_labels']
            diameters = labels.get('diameters', circle_diameters)
            distance = labels.get('distance', 2.0)
            position_deg = labels.get('position', 60)
            fontsize = labels.get('fontsize', 3.0)

            position_rad = math.radians(position_deg)
            for diameter in diameters:
                radius = diameter / 2.0
                label_distance = radius + distance
                x = label_distance * math.cos(position_rad)
                y = label_distance * math.sin(position_rad)
                f.write(f"""  0
TEXT
  8
0
 10
{x}
 20
{y}
 40
{fontsize}
  1
{int(diameter)}mm
""")

        # Bohrungen als Punkte
        bohrung_programs = ['bohrung50', 'bohrung_4x50', 'bohrung_4x100', 'bohrung_zentrum']
        for prog_id in bohrung_programs:
            if prog_id in nc_programs:
                prog = nc_programs[prog_id]
                if prog.get('type') == 'circle_pocket':
                    # Einzelne Bohrung (z.B. bohrung50)
                    # Zeichne als Punkt im Zentrum
                    f.write(f"""  0
POINT
  8
0
 10
0.0
 20
0.0
 30
0.0
""")
                elif prog.get('type') == 'multi_circle_drill':
                    # Mehrere Bohrungen an Positionen
                    angles = prog.get('positions', [])
                    distance = prog.get('distance_from_center', 0)

                    for angle in angles:
                        rad = math.radians(angle)
                        x = distance * math.cos(rad)
                        y = distance * math.sin(rad)
                        # Zeichne Bohrung als Punkt
                        f.write(f"""  0
POINT
  8
0
 10
{x}
 20
{y}
 30
0.0
""")

        # Mulden aus NC-Programmen
        for prog_id in ['mulde35x35', 'mulde27x27']:
            if prog_id in nc_programs:
                prog = nc_programs[prog_id]
                if prog.get('type') == 'pocket_square':
                    # Generiere abgerundete Quadrate basierend auf NC-Parametern
                    size = prog.get('contour_size', 35.0)
                    # Default 3mm für Eckradius wenn nicht vorhanden oder null
                    radius = prog.get('corner_radius')
                    if radius is None or radius == 0:
                        radius = 3.0

                    # Konvertiere Winkel zu (x, y) Koordinaten
                    angles = prog.get('positions', [])
                    distance = prog.get('distance_from_center', 60)
                    positions = []
                    for angle in angles:
                        rad = math.radians(angle)
                        x = distance * math.cos(rad)
                        y = distance * math.sin(rad)
                        positions.append((x, y))

                    for center_x, center_y in positions:
                        # Generiere Linien und Arcs für abgerundetes Quadrat
                        h = size / 2.0

                        # TOP LINE
                        f.write(f"""  0
LINE
  8
0
 10
{center_x - h + radius}
 20
{center_y + h}
 11
{center_x + h - radius}
 21
{center_y + h}
""")

                        # RIGHT LINE
                        f.write(f"""  0
LINE
  8
0
 10
{center_x + h}
 20
{center_y + h - radius}
 11
{center_x + h}
 21
{center_y - h + radius}
""")

                        # BOTTOM LINE
                        f.write(f"""  0
LINE
  8
0
 10
{center_x + h - radius}
 20
{center_y - h}
 11
{center_x - h + radius}
 21
{center_y - h}
""")

                        # LEFT LINE
                        f.write(f"""  0
LINE
  8
0
 10
{center_x - h}
 20
{center_y - h + radius}
 11
{center_x - h}
 21
{center_y + h - radius}
""")

                        # ARCS at corners
                        # Top-right
                        f.write(f"""  0
ARC
  8
0
 10
{center_x + h - radius}
 20
{center_y + h - radius}
 40
{radius}
 50
0.0
 51
90.0
""")

                        # Bottom-right
                        f.write(f"""  0
ARC
  8
0
 10
{center_x + h - radius}
 20
{center_y - h + radius}
 40
{radius}
 50
270.0
 51
360.0
""")

                        # Bottom-left
                        f.write(f"""  0
ARC
  8
0
 10
{center_x - h + radius}
 20
{center_y - h + radius}
 40
{radius}
 50
180.0
 51
270.0
""")

                        # Top-left
                        f.write(f"""  0
ARC
  8
0
 10
{center_x - h + radius}
 20
{center_y + h - radius}
 40
{radius}
 50
90.0
 51
180.0
""")

        # Titel
        if 'title' in dxf_spec:
            title = dxf_spec['title']
            text = title.get('text', 'Messplatte IR160-P')
            position_deg = title.get('position', 45)
            distance = title.get('distance', 110.0)
            fontsize = title.get('fontsize', 5.0)

            position_rad = math.radians(position_deg)
            x = distance * math.cos(position_rad)
            y = distance * math.sin(position_rad)
            f.write(f"""  0
TEXT
  8
0
 10
{x}
 20
{y}
 40
{fontsize}
  1
{text}
""")

        f.write("""  0
ENDSEC
  0
EOF
""")

    print(f"DXF file created: {output_path}")

# Main
if __name__ == "__main__":
    # Parse NC-Programme (für Mulden)
    nc_programs = parse_spec_cnc('spec_cnc.md')

    # Parse DXF-Spezifikation
    dxf_spec = parse_dxf_spec('spec_cnc.md')

    if dxf_spec:
        # Generiere DXF
        generate_dxf(dxf_spec, nc_programs)
        print("DXF generation complete!")
    else:
        print("Error: DXF specification not found in spec_cnc.md")
