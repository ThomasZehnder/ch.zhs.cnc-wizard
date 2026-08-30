# Generiert alle Dateien (NC + DXF), erhält aber Dateien die mit a_ beginnen


# Lösche nur .nc Dateien die NICHT mit a_ beginnen
Get-ChildItem -Filter "*.nc" -File | Where-Object { -not $_.Name.StartsWith("a_") } | Remove-Item -Force

# Lösche alte DXF-Dateien die NICHT mit a_ beginnen
Get-ChildItem -Filter "*dxf" -File | Where-Object { -not $_.Name.StartsWith("a_") } | Remove-Item -Force

# Generiere und formatiere NC-Dateien (Formatierung ist eingebettet)
python generate_nc_from_spec.py

# Generiere DXF-Datei aus Spezifikation
python generate_dxf_from_spec.py
