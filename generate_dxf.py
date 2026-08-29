#!/usr/bin/env python3
import math

output_path = r'd:\Arduino\force-sensor\messplatte-ir-160-p\messplatte.dxf'

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

    # Circles: 200mm, 160mm, 110mm, 50mm diameter
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

    # Label circles with diameter at 60°, 2mm from circle edge
    for diameter in circle_diameters:
        radius = diameter / 2.0
        label_distance = radius + 2.0
        angle_rad = math.radians(60.0)
        x = label_distance * math.cos(angle_rad)
        y = label_distance * math.sin(angle_rad)
        f.write(f"""  0
TEXT
  8
0
 10
{x}
 20
{y}
 40
3.0
  1
{int(diameter)}mm
""")


    # Boreholes as circles (4mm diameter = 2mm radius): 4x at 45°/135°/225°/315°, distance 100mm and 50mm from center
    hole_radius = 2.0
    hole_angles = [45.0, 135.0, 225.0, 315.0]

    for hole_distance in [100.0, 50.0]:
        for angle_deg in hole_angles:
            angle_rad = math.radians(angle_deg)
            x = hole_distance * math.cos(angle_rad)
            y = hole_distance * math.sin(angle_rad)
            f.write(f"""  0
CIRCLE
  8
0
 10
{x}
 20
{y}
 40
{hole_radius}
""")

    # Center borehole (4mm diameter = 2mm radius)
    f.write(f"""  0
CIRCLE
  8
0
 10
0.0
 20
0.0
 40
{hole_radius}
""")

    radius_pos = 50.0
    positions = [
        (0, radius_pos),           # top
        (radius_pos, 0),           # right
        (0, -radius_pos),          # bottom
        (-radius_pos, 0),          # left
    ]

    def create_rounded_square(cx, cy, size, radius):
        """Create a rounded square: 4 lines + 4 arcs"""
        h = size / 2.0

        # Side lines (offset by radius)
        # Top
        f.write(f"""  0
LINE
  8
0
 10
{cx - h + radius}
 20
{cy + h}
 11
{cx + h - radius}
 21
{cy + h}
""")

        # Right
        f.write(f"""  0
LINE
  8
0
 10
{cx + h}
 20
{cy + h - radius}
 11
{cx + h}
 21
{cy - h + radius}
""")

        # Bottom
        f.write(f"""  0
LINE
  8
0
 10
{cx + h - radius}
 20
{cy - h}
 11
{cx - h + radius}
 21
{cy - h}
""")

        # Left
        f.write(f"""  0
LINE
  8
0
 10
{cx - h}
 20
{cy - h + radius}
 11
{cx - h}
 21
{cy + h - radius}
""")

        # Arcs at corners
        # Top-right
        f.write(f"""  0
ARC
  8
0
 10
{cx + h - radius}
 20
{cy + h - radius}
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
{cx + h - radius}
 20
{cy - h + radius}
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
{cx - h + radius}
 20
{cy - h + radius}
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
{cx - h + radius}
 20
{cy + h - radius}
 40
{radius}
 50
90.0
 51
180.0
""")

    # First set: 35x35mm, Radius 10mm (id: mulde35x35)
    # Add metadata/ID layer comment
    f.write(f"""  0
TEXT
  8
0
 10
-150.0
 20
-150.0
 40
0.1
  1
ID:mulde35x35
""")

    for x, y in positions:
        create_rounded_square(x, y, 35.0, 10.0)

    # Second set: 27x27mm, Radius 4mm
    for x, y in positions:
        create_rounded_square(x, y, 27.0, 4.0)

    # Label drawing at 45°, 110mm from center
    title_distance = 110.0
    title_angle_rad = math.radians(45.0)
    title_x = title_distance * math.cos(title_angle_rad)
    title_y = title_distance * math.sin(title_angle_rad)
    f.write(f"""  0
TEXT
  8
0
 10
{title_x}
 20
{title_y}
 40
5.0
  1
Messplatte IR160-P
""")

    f.write("""  0
ENDSEC
  0
EOF
""")

print(f"DXF file created: {output_path}")
