# Generiert alle Dateien (NC + DXF), erhält aber Dateien die mit a_ beginnen

# Cleanup alte Dateien in outputs-Verzeichnissen
@("./projects/demo/outputs", "./projects/messplatte-ir-160-p/outputs") | ForEach-Object {
    if (Test-Path $_) {
        # Lösche .nc Dateien die NICHT mit a_ beginnen
        Get-ChildItem $_ -Filter "*.nc" -File | Where-Object { -not $_.Name.StartsWith("a_") } | Remove-Item -Force

        # Lösche .dxf und .svg Dateien die NICHT mit a_ beginnen
        Get-ChildItem $_ -Filter "*.dxf" -File | Where-Object { -not $_.Name.StartsWith("a_") } | Remove-Item -Force
    }
}

# Generiere und formatiere NC-Dateien (Formatierung ist eingebettet)
python src/generate_nc_from_spec.py "./projects/demo"
python src/generate_nc_from_spec.py "./projects/messplatte-ir-160-p"

# Generiere DXF-Datei aus Spezifikation
python src/generate_dxf_from_spec.py "./projects/demo"
python src/generate_dxf_from_spec.py "./projects/messplatte-ir-160-p"

# Konvertiere DXF zu SVG
python src/convert_dxf_to_svg.py "./projects/demo"
python src/convert_dxf_to_svg.py "./projects/messplatte-ir-160-p"
