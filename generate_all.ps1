# Generiert alle Dateien (NC + DXF), erhält aber Dateien die mit a_ beginnen

cd "d:\Arduino\force-sensor\messplatte-ir-160-p"

# Lösche nur .nc Dateien die NICHT mit a_ beginnen
Get-ChildItem -Filter "*.nc" -File | Where-Object { -not $_.Name.StartsWith("a_") } | Remove-Item -Force

# Lösche alte DXF-Dateien (nur messplatte_*.dxf, nicht andere)
Remove-Item "messplatte_*.dxf" -Force -ErrorAction SilentlyContinue

# Generiere NC-Dateien
python generate_nc_from_spec.py

# Formatiere NC-Dateien
python format_nc_files.py

# Generiere DXF-Datei aus Spezifikation
python generate_dxf_from_spec.py
