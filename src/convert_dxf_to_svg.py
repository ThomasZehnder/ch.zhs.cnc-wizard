#!/usr/bin/env python3
"""
Konvertiert DXF-Dateien zu SVG
"""
import sys
import os
import glob
from pathlib import Path

def convert_dxf_to_svg_ezdxf(dxf_file):
    """Konvertiert DXF zu SVG mittels ezdxf DxfSvgProxy"""
    import ezdxf

    dxf_file = os.path.abspath(dxf_file)
    if not os.path.exists(dxf_file):
        print(f"  Error: DXF file not found: {dxf_file}")
        return False

    svg_file = str(Path(dxf_file).with_suffix('.svg'))
    if os.path.exists(svg_file):
        os.remove(svg_file)

    try:
        # Versuche DxfSvgProxy zu importieren
        try:
            from ezdxf.addons.dxf2svg import DxfSvgProxy
        except ImportError as e:
            return False

        # Lade DXF-Datei
        dxf = ezdxf.readfile(dxf_file)

        # Konvertiere zu SVG
        proxy = DxfSvgProxy(dxf)
        svg_document = proxy.to_svg_document()

        # Schreibe SVG-Datei
        with open(svg_file, 'wb') as f:
            f.write(svg_document.tostring())

        print(f"  ✓ SVG file created: {svg_file}")
        return True

    except Exception as e:
        # Fehler - fallback wird versucht
        return False

def convert_dxf_to_svg_fallback(dxf_file):
    """Fallback: Erstelle einfache SVG basierend auf DXF-Struktur"""
    import ezdxf

    dxf_file = os.path.abspath(dxf_file)
    svg_file = str(Path(dxf_file).with_suffix('.svg'))

    if os.path.exists(svg_file):
        os.remove(svg_file)

    try:
        dxf = ezdxf.readfile(dxf_file)
        msp = dxf.modelspace()

        # Erstelle einfaches SVG mit Grundstruktur
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="400" height="400" viewBox="-250 -250 500 500">
  <rect width="400" height="400" fill="white"/>
  <g stroke="black" fill="none" stroke-width="1">
'''

        # Verarbeite alle Entities
        for entity in msp:
            try:
                if entity.dxftype() == 'CIRCLE':
                    cx = entity.dxf.center[0]
                    cy = entity.dxf.center[1]
                    r = entity.dxf.radius
                    svg_content += f'    <circle cx="{cx}" cy="{cy}" r="{r}"/>\n'
                elif entity.dxftype() == 'LINE':
                    x1, y1 = entity.dxf.start[0], entity.dxf.start[1]
                    x2, y2 = entity.dxf.end[0], entity.dxf.end[1]
                    svg_content += f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'
                elif entity.dxftype() == 'ARC':
                    cx = entity.dxf.center[0]
                    cy = entity.dxf.center[1]
                    r = entity.dxf.radius
                    svg_content += f'    <circle cx="{cx}" cy="{cy}" r="{r}"/>\n'
                elif entity.dxftype() == 'TEXT':
                    x = entity.dxf.insert[0]
                    y = entity.dxf.insert[1]
                    text = entity.dxf.text
                    svg_content += f'    <text x="{x}" y="{y}" font-size="10">{text}</text>\n'
                elif entity.dxftype() == 'POINT':
                    x = entity.dxf.location[0]
                    y = entity.dxf.location[1]
                    svg_content += f'    <circle cx="{x}" cy="{y}" r="2" fill="black"/>\n'
            except:
                pass  # Ignoriere Entities die nicht verarbeitet werden können

        svg_content += '''  </g>
</svg>
'''

        with open(svg_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        print(f"  ✓ SVG file created (fallback): {svg_file}")
        return True
    except Exception as e:
        print(f"  ✗ Fallback error: {type(e).__name__}: {e}")
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

        # Versuche mit ezdxf DxfSvgProxy, fallback auf einfaches SVG
        if convert_dxf_to_svg_ezdxf(dxf_file):
            success_count += 1
        elif convert_dxf_to_svg_fallback(dxf_file):
            success_count += 1
        else:
            print(f"  ✗ Failed to convert {basename}")

    print(f"\nConversion complete! {success_count}/{len(dxf_files)} files converted successfully.")
