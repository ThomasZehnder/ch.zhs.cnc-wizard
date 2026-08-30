#!/usr/bin/env python3
"""
DXF-Generator basierend auf spec_cnc.md
Parst die Spezifikation und generiert die DXF-Zeichnung mit ezdxf
"""
import math
import ezdxf
from spec_parser import parse_spec_cnc, parse_dxf_spec, normalize_corner_radius


def normalize_dxf_headers(dxf_file):
    """Standardisiert DXF-Header um Git-Diffs zu vermeiden"""
    try:
        doc = ezdxf.readfile(dxf_file)
        doc.header['$TDCREATE'] = 0.0
        doc.header['$TDUPDATE'] = 0.0
        doc.header['$FINGERPRINTGUID'] = '{00000000-0000-0000-0000-000000000000}'
        doc.header['$VERSIONGUID'] = '{00000000-0000-0000-0000-000000000001}'
        doc.saveas(dxf_file)
    except Exception as e:
        print(f"Warning: Could not normalize DXF headers: {e}")

def generate_dxf(dxf_spec, nc_programs):
    """Generiert DXF-Datei basierend auf Spezifikation"""
    output_path = dxf_spec.get('filename', 'messplatte_160P.dxf')

    # Erstelle DXF-Dokument
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Kreise: 200mm, 160mm, 110mm, 50mm
    circle_diameters = [200.0, 160.0, 110.0, 50.0]
    for diameter in circle_diameters:
        radius = diameter / 2.0
        msp.add_circle((0, 0), radius)

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
            msp.add_text(f"{int(diameter)}mm", dxfattribs={
                'insert': (x, y),
                'height': fontsize,
            })

    # Bohrungen als Punkte
    bohrung_programs = ['bohrung50', 'bohrung_4x50', 'bohrung_4x100', 'bohrung_zentrum']
    for prog_id in bohrung_programs:
        if prog_id in nc_programs:
            prog = nc_programs[prog_id]
            if prog.get('type') == 'circle_pocket':
                # Einzelne Bohrung (z.B. bohrung50)
                msp.add_point((0.0, 0.0))
            elif prog.get('type') == 'multi_circle_drill':
                # Mehrere Bohrungen an Positionen
                angles = prog.get('positions', [])
                distance = prog.get('distance_from_center', 0)

                for angle in angles:
                    rad = math.radians(angle)
                    x = distance * math.cos(rad)
                    y = distance * math.sin(rad)
                    msp.add_point((x, y))

    # Mulden aus NC-Programmen
    for prog_id in ['mulde35x35', 'mulde27x27']:
        if prog_id in nc_programs:
            prog = nc_programs[prog_id]
            if prog.get('type') == 'pocket_square':
                # Generiere abgerundete Quadrate basierend auf NC-Parametern
                size = prog.get('contour_size', 35.0)
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
                    # Generiere abgerundetes Quadrat
                    h = size / 2.0

                    # Zeichne vier Linien und vier Bögen
                    # Top line
                    msp.add_line(
                        (center_x - h + radius, center_y + h),
                        (center_x + h - radius, center_y + h)
                    )

                    # Right line
                    msp.add_line(
                        (center_x + h, center_y + h - radius),
                        (center_x + h, center_y - h + radius)
                    )

                    # Bottom line
                    msp.add_line(
                        (center_x + h - radius, center_y - h),
                        (center_x - h + radius, center_y - h)
                    )

                    # Left line
                    msp.add_line(
                        (center_x - h, center_y - h + radius),
                        (center_x - h, center_y + h - radius)
                    )

                    # Corner arcs
                    # Top-right
                    msp.add_arc(
                        (center_x + h - radius, center_y + h - radius),
                        radius, 0, 90
                    )

                    # Bottom-right
                    msp.add_arc(
                        (center_x + h - radius, center_y - h + radius),
                        radius, 270, 360
                    )

                    # Bottom-left
                    msp.add_arc(
                        (center_x - h + radius, center_y - h + radius),
                        radius, 180, 270
                    )

                    # Top-left
                    msp.add_arc(
                        (center_x - h + radius, center_y + h - radius),
                        radius, 90, 180
                    )

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
        msp.add_text(text, dxfattribs={
            'insert': (x, y),
            'height': fontsize,
        })

    # Speichere DXF-Datei
    doc.saveas(output_path)
    # Normalisiere Header-Variablen
    normalize_dxf_headers(output_path)
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
        original_filename = dxf_spec.get('filename', 'messplatte_160P.dxf')
        dxf_spec['filename'] = os.path.join(output_dir, original_filename)

        # Generiere DXF
        generate_dxf(dxf_spec, nc_programs)
        print("DXF generation complete!")
    else:
        print("Error: DXF specification not found in spec_cnc.md")
