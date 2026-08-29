#!/usr/bin/env python3
"""
Formatiert alle generierten .nc Dateien: Floats auf 6 Dezimalstellen, mindestens 1 Dezimalstelle
"""
import re
import glob

def format_float(value_str):
    """Formatiert einen Zahlen-String auf 6 Dezimalstellen, mindestens 1 Dezimalstelle"""
    try:
        value = float(value_str)
        # Runde auf 6 Dezimalstellen
        rounded = round(value, 6)
        # Formatiere mit mindestens 1 Dezimalstelle
        if rounded == int(rounded):
            return f"{int(rounded)}.0"
        else:
            formatted = f"{rounded:.6f}".rstrip('0')
            # Stelle sicher, dass mindestens .0 vorhanden ist
            if '.' not in formatted:
                formatted += '.0'
            return formatted
    except:
        return value_str

def format_nc_file(filepath):
    """Formatiert alle Zahlen in einer NC-Datei"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Regex für Zahlen nach G-Code-Befehlen: X, Y, Z, I, J, F, S
    # Pattern: (X|Y|Z|I|J|F|S)(-?\d+\.?\d*)
    def replace_number(match):
        prefix = match.group(1)  # X, Y, Z, I, J, F, S
        number = match.group(2)  # die Zahl
        # F und S nicht formatieren (Feed und Spindle sind Ganzzahlen)
        if prefix in ('F', 'S'):
            return match.group(0)
        return f"{prefix}{format_float(number)}"

    # Ersetze Zahlen nach G-Code-Präfixen
    formatted = re.sub(r'([XYZIJF])(-?\d+\.?\d*)', replace_number, content)

    with open(filepath, 'w') as f:
        f.write(formatted)

    print(f"Formatiert: {filepath}")

# Formatiere alle .nc Dateien
for nc_file in glob.glob('*.nc'):
    if nc_file != 'empty.nc':
        format_nc_file(nc_file)

print("Alle NC-Dateien formatiert!")
