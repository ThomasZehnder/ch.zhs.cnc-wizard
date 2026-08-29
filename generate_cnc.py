#!/usr/bin/env python3
import math

output_path = r'd:\Arduino\force-sensor\messplatte-ir-160-p\mulde35x35.nc'

# Parameters
square_size = 35.0
corner_radius = 10.0
pocket_depth = 6.0
tool_diameter = 3.15
tool_radius = tool_diameter / 2.0
feed_rate = 450  # mm/min
spindle_speed = 4000  # RPM
safety_height = 5.0

# Zustellung pro Pass: 80% Überdeckung des Werkzeuges
depth_per_pass = tool_diameter * 0.8  # 2.52mm

# Quadrat positions (center at 0° distance 50mm)
quad_center_x = 0.0
quad_center_y = 50.0
half_square = square_size / 2.0

with open(output_path, 'w') as f:
    f.write("; ============================================\n")
    f.write("; Mulde Sensor 35x35\n")
    f.write("; Tiefe: 6mm, Fraesmaschine Durchmesser: 3.15mm\n")
    f.write("; Generated for MACH3\n")
    f.write("; ============================================\n\n")

    # Header
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
    f.write(f"S{spindle_speed}                        ; Spindle speed: {spindle_speed} RPM\n")
    f.write("M3                           ; Spindle ON (clockwise)\n")
    f.write("G4 P2.0                      ; Dwell 2 seconds\n\n")

    # Safe Z
    f.write("; ============================================\n")
    f.write("; POCKET CLEARING\n")
    f.write("; ============================================\n")
    f.write(f"G0 Z{safety_height}\n")
    f.write(f"G0 X{quad_center_x} Y{quad_center_y}\n\n")

    # Calculate number of passes
    num_passes = math.ceil(pocket_depth / depth_per_pass)

    f.write(f"; Passes: {num_passes}, Zustellung pro Pass: {depth_per_pass:.2f}mm\n\n")

    for pass_num in range(1, num_passes + 1):
        current_depth = pass_num * depth_per_pass
        if current_depth > pocket_depth:
            current_depth = pocket_depth

        z_depth = -current_depth

        f.write(f"; Pass {pass_num}: Z = {z_depth:.2f}mm\n")

        # Rapid to Z above the pocket
        f.write(f"G0 Z{safety_height}\n")

        # Position over pocket (center of quadrat)
        x_center = quad_center_x
        y_center = quad_center_y
        f.write(f"G0 X{x_center} Y{y_center}\n")

        # Lower to cut depth
        f.write(f"G1 Z{z_depth:.2f} F{feed_rate}\n")

        # Raster pattern to clear entire pocket
        x_min = quad_center_x - half_square + tool_radius
        x_max = quad_center_x + half_square - tool_radius
        y_min = quad_center_y - half_square + tool_radius
        y_max = quad_center_y + half_square - tool_radius

        # Horizontal raster pattern (zigzag) with tool diameter spacing
        raster_spacing = tool_diameter * 0.8  # 80% overlap = 2.52mm
        y_current = y_min

        while y_current <= y_max:
            if int((y_current - y_min) / raster_spacing) % 2 == 0:
                # Left to right
                f.write(f"G1 X{x_min} Y{y_current:.2f} F{feed_rate}\n")
                f.write(f"G1 X{x_max} Y{y_current:.2f} F{feed_rate}\n")
            else:
                # Right to left
                f.write(f"G1 X{x_max} Y{y_current:.2f} F{feed_rate}\n")
                f.write(f"G1 X{x_min} Y{y_current:.2f} F{feed_rate}\n")

            y_current += raster_spacing

        f.write("\n")

    # Finish
    f.write("; ============================================\n")
    f.write("; PROGRAM ENDE\n")
    f.write("; ============================================\n")
    f.write(f"G0 Z{safety_height}\n")
    f.write("G0 X0 Y0\n")
    f.write("M5                           ; Spindle OFF\n")
    f.write("M30                          ; Program end\n")

print(f"CNC file created: {output_path}")
print(f"Depth per pass: {depth_per_pass:.2f}mm (80% tool overlap)")
print(f"Number of passes: {num_passes}")
