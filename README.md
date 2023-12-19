# pdf-translator

Mit diesem Tool können PDF-Dokumente übersetzt werden.

![](images/application.png)

[Download](https://github.com/hilderonny/pdf-translator/releases)

[![Building release](https://github.com/hilderonny/pdf-translator/actions/workflows/PyInstaller.yml/badge.svg)](https://github.com/hilderonny/pdf-translator/actions/workflows/PyInstaller.yml)

## Benutzung

Einfach die neueste ZIP-Datei von [hier](https://github.com/hilderonny/pdf-translator/releases) herunterladen, entpacken und die Datei **PdfTranslator.exe** ausführen. Das Programm benötigt keine Installation.

Wenn das Programm läuft, wählt man eine Datei, die darin enthaltene Sprache und die Zielsprache aus und startet die Übersetzung.

Nach Abschluss wird im Anwendungsfenster ein Protokoll der Übersetzung angezeigt, welches in einer Textdatei gespeichert werden kann.

## Einrichtung der Entwicklungsumgebung

1. Python mit der Version 3.11.6 mit der Erweiterung "TCL/TK" installiert werden. https://www.python.org/downloads/windows/
1. Repository klonen
1. `pip install -r requirements.txt`
1. Argos Translate Modelle in Unterverzeichnis `./data/argos-translate/packages` kopieren, alternativ mit `python ./download_argos_models.py` herunterladen
