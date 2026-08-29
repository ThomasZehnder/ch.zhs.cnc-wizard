# CNC Fräsprogramm-Generator

Automatisierte Generierung von MACH3-kompatiblen CNC-Fräsprogrammen basierend auf strukturierter Markdown-Spezifikation.

## Übersicht

Dieses Projekt generiert automatisch G-Code für eine Messplatte (IR160-P) mit verschiedenen Fräsoperationen:
- Abgerundete quadratische Taschen (Mulden)
- Runde Taschen/Bohrungen
- Ringe (annuläre Regionen)
- Kreise mit Radiuskorrektur (Außen-/Innenkontur)
- Mehrfach-Bohrungen an definierten Positionen

## Struktur

```
spec_cnc.md                    # Spezifikation aller NC-Programme (Single Source of Truth)
spec_parser.py                 # Gemeinsamer Parser für MD-Spezifikation
generate_nc_from_spec.py       # NC-Generator (nutzt spec_parser)
generate_dxf_from_spec.py      # DXF-Generator (nutzt spec_parser)
format_nc_files.py             # Formatierung für numerische Genauigkeit
generate_all.ps1               # Orchestrierungsskript
```

## Architektur

Die Lösung verwendet eine **Single Source of Truth** Architektur:

1. **spec_cnc.md** – Zentrale Spezifikation mit allen NC-Programmen und DXF-Geometrien
2. **spec_parser.py** – Gemeinsamer Parser, der Markdown in strukturierte Daten konvertiert
   - `parse_spec_cnc()` – Extrahiert NC-Programmdefinitionen
   - `parse_dxf_spec()` – Extrahiert DXF-Spezifikationen
3. **Generatoren** – Nutzen den gemeinsamen Parser
   - `generate_nc_from_spec.py` – Erstellt G-Code-Dateien
   - `generate_dxf_from_spec.py` – Erstellt DXF-Zeichnungen

Diese Struktur vermeidet Duplikation und stellt sicher, dass beide Generatoren immer synchron sind.

## Verwendung

### Schnellstart: Alle Dateien regenerieren (NC + DXF)

```powershell
powershell -ExecutionPolicy Bypass -File generate_all.ps1
```

Das Skript generiert:
1. **NC-Dateien** aus `spec_cnc.md` (alle 9 NC-Programme)
2. **DXF-Zeichnung** aus `spec_cnc.md` (Kreise, Labels, Mulden)
3. Formatiert alle Zahlen konsistent (6 Dezimalstellen, mindestens 1 nach dem Komma)
4. Erhält alle Dateien mit `a_` Präfix (z.B. `a_go_home_position.nc`)

### Manuelle Schritte

1. Bearbeite `spec_cnc.md` und definiere die NC-Programme
2. Führe Generator aus: `python generate_nc_from_spec.py`
3. Formatiere die Ausgabe: `python format_nc_files.py`
4. Die generierten `.nc` Dateien sind MACH3-ready

### Dateien mit a_ Präfix

Dateien die mit `a_` beginnen (z.B. `a_go_home_position.nc`) werden von der Regenerierung ausgenommen und erhalten bleiben.

## NC-Program-Typen

### 1. pocket_square
**Spiralförmiges Fräsen von abgerundeten Quadraten**

Verwendet für quadratische Taschen mit abgerundeten Ecken. Das Werkzeug fahrt spiralförmig von außen nach innen, wobei mehrere Konturen gleichzeitig bearbeitet werden können.

**Typische Anwendung:** Sensormulden, Aufnahmetaschen

**Erforderliche Parameter:**
- `Anzahl Konturen` – Wie viele Quadrate (z.B. 4)
- `Kontur Groesse` – Seitenlänge in mm
- `Eckradius` – Radius der abgerundeten Ecken
- `Positionen` – Winkel-Positionen (0°, 90°, 180°, 270°)
- `Abstand vom Zentrum` – Entfernung vom Mittelpunkt
- `Taschentiefe` – Frästiefe

**Beispiel:**
```
**Type:** pocket_square
- Kontur Groesse: 35mm
- Eckradius: 10mm
- Taschentiefe: 6mm
```

---

### 2. circle_pocket
**Spiralförmiges Fräsen von runden Taschen/Bohrungen**

Kreisförmige Vertiefungen mit konzentrisch einwärts fahrenden Kreisen. Ideal für tiefe Bohrungen.

**Typische Anwendung:** Tiefe Bohrungen, Zentrierbohrungen

**Erforderliche Parameter:**
- `Durchmesser` – Lochdurchmesser in mm
- `Abstand vom Zentrum` – Position (meist 0 für zentral)
- `Taschentiefe` – Frästiefe

**Beispiel:**
```
**Type:** circle_pocket
- Durchmesser: 50mm
- Taschentiefe: 12mm
```

---

### 3. circle
**Fräsen eines Kreises mit Radiuskorrektur**

Fahrt einen einzelnen Kreis pro Pass. Die Radiuskorrektur bestimmt, ob das Werkzeug außen oder innen am Kreis läuft – damit wird automatisch der Werkzeugradius kompensiert.

**Typische Anwendung:** Außen-/Innenkontur-Fräsen (Finishing)

**Erforderliche Parameter:**
- `Durchmesser` – Kreisdurchmesser in mm
- `Abstand vom Zentrum` – Position
- `Taschentiefe` – Frästiefe
- `Radiuskorrektur` – **keine** | **innen** | **aussen**

**Radiuskorrektur erklär:**
- **aussen**: Werkzeug fährt außerhalb des Kreises → tatsächlicher Durchmesser = Durchmesser + 2×Werkzeugradius
- **innen**: Werkzeug fährt innerhalb des Kreises → tatsächlicher Durchmesser = Durchmesser - 2×Werkzeugradius
- **keine**: Kein Offset → Werkzeug fährt genau auf der Position

**Beispiel:**
```
**Type:** circle
- Durchmesser: 200mm
- Radiuskorrektur: aussen
- Taschentiefe: 12mm
```

---

### 4. ring_pocket
**Fräsen eines Ringes (annuläre Region)**

Fräst die Region zwischen zwei konzentrischen Kreisen (innerer und äußerer Durchmesser). Kombiniert innere und äußere Spirale.

**Typische Anwendung:** Ring-förmige Nuten, Abstufungen

**Erforderliche Parameter:**
- `Durchmesser Innen` – Innerer Durchmesser
- `Durchmesser Aussen` – Äußerer Durchmesser
- `Abstand vom Zentrum` – Position
- `Taschentiefe` – Frästiefe

**Beispiel:**
```
**Type:** ring_pocket
- Durchmesser Innen: 110mm
- Durchmesser Aussen: 160mm
- Taschentiefe: 6mm
```

---

### 5. multi_circle_drill
**Senkrechte Bohrungen an mehreren Positionen**

Bohrt mehrere Löcher senkrecht (nur Z-Achse) an definierten Winkelpositionen. Keine Spirale, keine XY-Bewegung während des Bohrens.

**Typische Anwendung:** Befestigungsbohrungen, Positionierungsbohrungen

**Erforderliche Parameter:**
- `Anzahl Bohrungen` – Wie viele Löcher
- `Positionen` – Winkel (z.B. 45°, 135°, 225°, 315°)
- `Abstand vom Zentrum` – Radius der Bohrungspositionen
- `Bohrungstiefe` – Bohrtiefe

**Beispiel:**
```
**Type:** multi_circle_drill
- Anzahl Bohrungen: 4
- Positionen: 45°, 135°, 225°, 315°
- Abstand vom Zentrum: 50mm
- Bohrungstiefe: 6mm
```

---

## Allgemeine Einstellungen

Alle Programme verwenden folgende Standardwerte (in `spec_cnc.md` konfigurierbar):

- **Vorschubgeschwindigkeit:** F450 mm/min
- **Spindelgeschwindigkeit:** S4000 RPM
- **Werkzeugdurchmesser:** 3.15 mm
- **Sicherheitshöhe Z:** 2 mm
- **Zustellung pro Pass:** 4 mm
- **Raster-Überdeckung:** 80% (2.52 mm Abstand)

## Spezifikationsformat

Jedes NC-Programm in `spec_cnc.md` hat diese Struktur:

```markdown
### Programm-Name

**Identifier:** eindeutige-id
**Filename:** output.nc
**Type:** circle|circle_pocket|pocket_square|ring_pocket|multi_circle_drill
**Description:** Beschreibung

**Parameters:**
- Parameter1: Wert1
- Parameter2: Wert2
```

## Output

Die generierten `.nc` Dateien sind:
- MACH3-kompatibel (G-Code Standard)
- Mit Kommentaren versehen
- Mit automatischen Werkzeugradius-Korrektionen
- Mit multi-pass Fräsungen (4mm pro Pass)

## Beispiel-Workflow

1. DXF-Zeichnung öffnen: `messplatte.dxf`
2. Spezifikation in `spec_cnc.md` definieren
3. Generator ausführen: `python generate_nc_from_spec.py`
4. NC-Dateien in CAM-Software laden
5. Mit MACH3 fräsen

---

**Hinweis:** Der Parser ist robust gegen verschiedene Formatierungsvarianten in der Markdown-Datei (Leerzeichen, Komma-/Schrägstrich-Trennung, etc.).
