#!/usr/bin/env python3
"""
Konvertiert DXF-Dateien zu SVG
"""
import sys
import os
import glob
from pathlib import Path

def convert_dxf_to_svg_ezdxf(dxf_file):
    """Konvertiert DXF zu SVG mittels ezdxf"""
    import ezdxf
    from ezdxf.addons.drawing import Frontend, RenderContext
    # WICHTIG: Das .svg und layout Untermodul explizit importieren
    from ezdxf.addons.drawing import svg, layout

    dxf_file = os.path.abspath(dxf_file)
    if not os.path.exists(dxf_file):
        print(f"  Error: DXF file not found: {dxf_file}")
        return False

    svg_file = str(Path(dxf_file).with_suffix('.svg'))
    if os.path.exists(svg_file):
        os.remove(svg_file)

    try:
        # 1. Load the DXF document
        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()


        # GLOBALEN PUNKT-STIL DEFINIEREN (Behebt die Sichtbarkeit)
        doc.header['$PDMODE'] = 32   # 32 = Zeichnet einen Kreis um den Punkt (Alternative: 3 für ein 'X')
        doc.header['$PDSIZE'] = 5.0  # Setzt den Radius/Grösse des Punkts in CAD-Einheiten (z.B. 5mm)

        # FARBE ALLER PUNKTE REINIGEN/ÄNDERN
        for point in msp.query('POINT'):
            point.dxf.color = 1  # 1 = Rot (AutoCAD Color Index)

        # 2. SVGBackend aus dem korrekten Untermodul instanziieren
        backend = svg.SVGBackend()
        frontend = Frontend(RenderContext(doc), backend)

        # 3. Inhalt rendern
        frontend.draw_layout(msp)

        # 4. SEITEN-LAYOUT DEFINIEREN (Behebt deinen Fehler)
        # Option A: Automatische Grösse basierend auf dem Inhalt (empfohlen für SVG)
        page = layout.Page(width=0, height=0, units=layout.Units.mm)

        # 5. Die Seite beim Generieren des SVG-Strings übergeben
        svg_string = backend.get_string(page)

        # 6. Save the SVG data to a file
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_string)

        print(f"  ✓ SVG file created: {svg_file}")
        return True

    except Exception as e:
        print(f" Exception: {e}")
        return False



# Main
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_dxf_to_svg.py <project_dir>")
        print("Example: python convert_dxf_to_svg.py ./projects/demo")
        sys.exit(1)

    project_dir = sys.argv[1]
    output_dir = os.path.join(project_dir, 'outputs')

    if not os.path.exists(output_dir):
        print(f"Error: Output directory not found: {output_dir}")
        sys.exit(1)

    # Finde alle DXF-Dateien (ausser die mit a_ beginnen)
    dxf_files = glob.glob(os.path.join(output_dir, '*.dxf'))
    dxf_files = [f for f in dxf_files if not os.path.basename(f).startswith('a_')]

    if not dxf_files:
        print(f"No DXF files found in {output_dir}")
        sys.exit(0)

    success_count = 0
    for dxf_file in dxf_files:
        basename = os.path.basename(dxf_file)
        print(f"Converting {basename}...")

        if convert_dxf_to_svg_ezdxf(dxf_file):
            success_count += 1
        else:
            print(f"  ✗ Failed to convert {basename}")

    print(f"\nConversion complete! {success_count}/{len(dxf_files)} files converted successfully.")
