# 50ohm.de

50ohm.de ist die Ausbildungsplattform des DARC e.V. 

Dieses Repository enthält den Generator für die Seite [50ohm.de](https://50ohm.de), der mit einer Directus-Datenbank als Quelle arbeitet.

## Überblick

Die Ausbildungsmaterialien von 50ohm.de werden in einem erweiterten Marcdownformat geschrieben, intern als Darcdown bezeichnet. Kern des Generators ist ein Parser, der auf [mistletoe](https://github.com/miyuchina/mistletoe) basiert und um zusätzliche Syntax und Ausgabeformate erweitert wurde.

Die möglichen Ausgabeformate sind:
- HTML: [`fifty_ohm_html_renderer.py`](renderer/fifty_ohm_html_renderer.py)
- LaTeX: [`fifty_ohm_latex_renderer`](renderer/fifty_ohm_latex_renderer.py)
- HTML für Slides mit reveal.js: [`fifty_ohm_html_slide_renderer.py`](renderer/fifty_ohm_html_slide_renderer.py)

Prinzipiell lassen sich diese Generatoren auch losgelöst vom Directus einsetzen. Der zweite Teil des Generators liegt in `src`, unterteilt in die Prozessschritte Herunderladen ([`download.py`](src/download.py)) und Seite Bauen ([`build.py`](src/build.py)).

Hier werden alle Inhalte aus der Datenbank heruntergeladen und strukturiert in verschiedenen JSON-Dateien abgelegt. Diese dienen im Build-Prozess als Quelle für Abschnitte, Kapitelstruktur und weitere Inhalte.

In der `build.py` finden sich außerdem weitere Begleitfunktionen zum Renderprozess, z.B. das Übersetzen von Fragennummern in Fragen oder das Kopieren von Assets.

## Mitmachen

Aktuell wird 50ohm durch ein kleines ehrenamtliches Entwicklerteam beim DARC e.V. betreut und weiterentwickelt. Falls du einen Fehler oder einen Funktionswunsch hast, schreibe gerne ein Issue. Auch über einen PR freuen wir uns!

Wenn du inhaltliche Beiträge hast, wende dich bitte an das 50ohm-Autorenteam.

### Python einrichten und Abhängigkeiten installieren

Dieses Projekt wurde mit [`uv`](https://docs.astral.sh/uv/) aufgesetzt, ist aber genauso mit `pip` und `venv` kompatibel.

Wichtig ist, mit der richtigen Python-Version aus der `.python-version` zu arbeiten. Mit `uv` geht das ganz einfach:
```console
[50ohm]$ uv venv
[50ohm]$ source .venv/bin/activate
```

Die Dependencies müssen aus der `requirements.txt` installiert werden:
```console
[50ohm]$ uv pip sync requirements.txt
```

### Ausführen

Um 50ohm ausführen zu können, wird in den meisten Fällen ein Zugang zu passenden Directus-Instanzen benötigt. Diese können über eine `config/config.json` konfiguriert werden.

Die 50ohm.de-Website wird mit folgendem Befehl vollständig gebaut:

```console
[50ohm]$ python3 ./build.py
```

Anschließend ist der Einstiegspunkt in `build/index.html` zu finden.