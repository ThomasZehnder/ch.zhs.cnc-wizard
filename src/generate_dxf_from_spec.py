#!/usr/bin/env python3
"""
DXF-Generator basierend auf spec_cnc.md
Parst die Spezifikation und generiert die DXF-Zeichnung
"""
import math
import re
from spec_parser import parse_spec_cnc, parse_dxf_spec, normalize_corner_radius

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
                    # Normalisiere Eckradius (Default 3mm wenn nicht vorhanden oder null)
                    radius = normalize_corner_radius(prog.get('corner_radius'))

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
    import sys
    import os

    # Akzeptiere Projekt-Verzeichnis als Argument
    project_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    spec_file = os.path.join(project_dir, 'spec_cnc.md')
    output_dir = os.path.join(project_dir, 'outputs')

    # Erstelle outputs-Verzeichnis falls nötig
    os.makedirs(output_dir, exist_ok=True)

    # Parse NC-Programme (für Mulden)
    nc_programs = parse_spec_cnc(spec_file)

    # Parse DXF-Spezifikation
    dxf_spec = parse_dxf_spec(spec_file)

    if dxf_spec:
        # Modifiziere output_path für DXF, um im output_dir zu speichern
        original_filename = dxf_spec.get('filename', 'demo.dxf')
        dxf_spec['filename'] = os.path.join(output_dir, original_filename)

        # Generiere DXF
        generate_dxf(dxf_spec, nc_programs)
        print("DXF generation complete!")
    else:
        print("Error: DXF specification not found in spec_cnc.md")
