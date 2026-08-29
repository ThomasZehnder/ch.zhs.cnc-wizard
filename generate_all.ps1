# Generiert alle NC-Dateien, erhält aber Dateien die mit a_ beginnen

cd "d:\Arduino\force-sensor\messplatte-ir-160-p"

# Lösche nur .nc Dateien die NICHT mit a_ beginnen
Get-ChildItem -Filter "*.nc" -File | Where-Object { -not $_.Name.StartsWith("a_") } | Remove-Item -Force

# Generiere NC-Dateien
python generate_nc_from_spec.py

# Formatiere die Dateien
python format_nc_files.py
