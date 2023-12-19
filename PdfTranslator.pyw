VERSION = "1.0.0"

import os
import PyPDF2
import pytesseract
import PySimpleGUI as sg
import subprocess, os, platform
import datetime
import hashlib
import sys, getopt

sg.theme("SystemDefault1")

supported_languages = {
    "Arabisch": "ar", 
    "Aserbaidschanisch": "az", 
    "Chinesisch": "zh", 
    "Dänisch": "da", 
    "Deutsch": "de", 
    "Englisch": "en", 
    "Esperanto": "eo", 
    "Finnisch": "fi", 
    "Französisch": "fr", 
    "Griechisch": "el", 
    "Hebräisch": "he", 
    "Hindi": "hi", 
    "Indonesisch": "id", 
    "Irisch": "ga", 
    "Italienisch": "it", 
    "Japanisch": "ja", 
    "Koreanisch": "ko", 
    "Niederländisch": "nl", 
    "Persisch": "fa", 
    "Polnisch": "pl", 
    "Portugiesisch": "pt", 
    "Russisch": "ru", 
    "Schwedisch": "sv", 
    "Slowakisch": "sk", 
    "Spanisch": "es", 
    "Tschechisch": "cs", 
    "Türkisch": "tr", 
    "Ukrainisch": "uk",
    "Ungarisch": "hu"
}

class Logger(object):

    def __init__(self, text_field):
        self.text_field = text_field

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            try:
                # Beim Beenden gibt es das Fenster nicht mehr, daher kann es zu einer Exception kommen
                self.text_field.print(line.rstrip())
            finally:
                pass

    def flush(object):
        pass

def InstallPackages():
    global window
    os.environ["ARGOS_PACKAGES_DIR"] = "./data/argos-translate/packages"
    import argostranslate.package
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    max_value = len(available_packages)
    for i in range(max_value):
        package = available_packages[i]
        window["-OUTPUT-"].print("Lade " + package.from_code + "-" + package.to_code + " herunter ...")
        window["-PROGRESSBAR-"].update(i, max_value)
        download_path = package.download()
        argostranslate.package.install_from_path(download_path)
    window["-OUTPUT-"].print("Übersetzungsdaten heruntergeladen.")

def TranslateAsync():
    global window, values, protokoll
    start_time = datetime.datetime.utcnow()
    argos_translate_version = "1.8.1"
    file_path = values["-FILENAME-"]
    source_language_key = supported_languages[values["-SOURCELANGUAGE-"]]
    target_language_key = supported_languages[values["-TARGETLANGUAGE-"]]
    protokoll = [
        "Programminformationen",
        "=====================",
        f"Programm: PdfTranslator.pyw, Version {VERSION}",
        "Quelle: https://github.com/hilderonny/pdf-translator",
        f"Übersetzung  mit: Argos Translate, Version {argos_translate_version}",
        "Gerät: CPU",
        f"Datei: {file_path}",
        f"PDF-Sprache: {values['-SOURCELANGUAGE-']} ({source_language_key})",
        f"Ausgabesprache: {values['-TARGETLANGUAGE-']} ({target_language_key})"
    ]
    # Argos Translate vorbereiten
    os.environ["ARGOS_PACKAGES_DIR"] = "./data/argos-translate/packages"
    os.environ["ARGOS_DEVICE_TYPE"] = "cpu"
    window["-OUTPUT-"].print(f"Lade Argos Translate {argos_translate_version} für {values['-SOURCELANGUAGE-']} - {values['-TARGETLANGUAGE-']}")
    import argostranslate.translate
    window["-OUTPUT-"].print(f"{source_language_key} - {target_language_key}")
    argos_translation = argostranslate.translate.get_translation_from_codes(source_language_key, target_language_key)
    # PDF Datei laden
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # In Seiten separieren
        num_pages = len(pdf_reader.pages)
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            window["-OUTPUT-"].print("")
            window["-OUTPUT-"].print(f"Verarbeite Seite {i + 1} von {num_pages}")
            window["-OUTPUT-"].print("============================================")
            window["-PROGRESSBAR-"].update(i, num_pages)
            protokoll.append("")
            protokoll.append(f"Seite {i + 1} von {num_pages}")
            protokoll.append("=============================")
            # Text extrahieren
            direct_text = page.extract_text().replace("  ", " ") # Doppelte Leerzeichen entfernen
            window["-OUTPUT-"].print("")
            window["-OUTPUT-"].print("Originaltext")
            window["-OUTPUT-"].print("------------")
            window["-OUTPUT-"].print(direct_text)
            # Text übersetzen
            translated_text = argos_translation.translate(direct_text)
            window["-OUTPUT-"].print("")
            window["-OUTPUT-"].print("Übersetzung")
            window["-OUTPUT-"].print("-----------")
            window["-OUTPUT-"].print(translated_text)
            # Protokoll schreiben
            protokoll.append("")
            protokoll.append("Originaltext"),
            protokoll.append("------------"),
            protokoll.append(direct_text)
            protokoll.append("")
            protokoll.append("Übersetzung"),
            protokoll.append("-----------"),
            protokoll.append(translated_text)
            # Bilder extrahieren
            for image in page.images:
                # OCR auf Bild ausführen
                image_text = pytesseract.image_to_string(image.data).replace("  ", " ") # Doppelte Leerzeichen entfernen
                window["-OUTPUT-"].print("")
                window["-OUTPUT-"].print("Originaltext")
                window["-OUTPUT-"].print("------------")
                window["-OUTPUT-"].print(image_text)
                # Text übersetzen
                translated_text = argos_translation.translate(image_text)
                window["-OUTPUT-"].print("")
                window["-OUTPUT-"].print("Übersetzung")
                window["-OUTPUT-"].print("-----------")
                window["-OUTPUT-"].print(translated_text)
                # Protokoll schreiben
                protokoll.append("")
                protokoll.append("Originaltext"),
                protokoll.append("------------"),
                protokoll.append(direct_text)
                protokoll.append("")
                protokoll.append("Übersetzung"),
                protokoll.append("-----------"),
                protokoll.append(translated_text)
    stop_time = datetime.datetime.utcnow()
    duration = stop_time - start_time
    protokoll.append("")
    protokoll.append("Statistik")
    protokoll.append("=========")
    protokoll.append(f"Beginn: {start_time.isoformat()}")
    protokoll.append(f"Ende: {stop_time.isoformat()}")
    protokoll.append(f"Dauer: {duration}")

def main(argv):
    opts, _ = getopt.getopt(argv, "v", ["version"])
    for o, _ in opts:
        if o in ("-v", "--version"):
            print(VERSION)
            exit()
    global window, values, protokoll
    layout = [
        [
            sg.InputText(key="-FILENAME-", readonly=True, expand_x=True, enable_events=True), 
            sg.FileBrowse(button_text="Datei auswählen ...", target="-FILENAME-")
        ],
        [
            sg.Text("Sprache der PDF-Datei:"),
            sg.Combo(list(supported_languages.keys()), auto_size_text=True, default_value="Englisch", readonly=True, key="-SOURCELANGUAGE-"),
            sg.Text("Ausgabesprache:"),
            sg.Combo(list(supported_languages.keys()), auto_size_text=True, default_value="Deutsch", readonly=True, key="-TARGETLANGUAGE-"),
        ],
        [
            sg.Button(button_text="Verarbeitung starten", key="-STARTEN-", disabled=True)
        ],
        [
            sg.ProgressBar(max_value=6, orientation="horizontal", size=(20, 20), key="-PROGRESSBAR-", expand_x=True)
        ],
        [
            sg.Multiline(size=(45, 5), key="-OUTPUT-", expand_x=True, expand_y=True, font=("Courier New", 12))
        ],
        [
            sg.InputText(key="-SPEICHERN-", do_not_clear=False, enable_events=True, visible=False), 
            sg.FileSaveAs(button_text="Protokoll speichern unter ...", target="-SPEICHERN-", file_types=(("Text", ".txt"),))
        ]
    ]
    window = sg.Window(title="PDF Translator - " + VERSION, layout=layout, size=(1000,800), resizable=True, element_justification="center", finalize=True)
    # Konsolenausgabe umleiten
    old_stout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = Logger(window["-OUTPUT-"])
    sys.stderr = sys.stdout

    # Prüfen, ob Modelle für Argos Translate vorhanden sind
    if not os.path.isdir("./data/argos-translate/packages/en_de"):
        sg.popup_ok("Übersetzungsdaten müssen heruntergeladen werden. Stellen Sie sicher, dass dafür eine Internetverbindung besteht!", title="Fehlende Übersetzungsdaten")
        window.perform_long_operation(func=InstallPackages, end_key="-INSTALLDONE-")

    protokoll = ""
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            sys.stdout = old_stout
            sys.stderr = old_stderr
            break
        elif event == "-FILENAME-":
            window["-STARTEN-"].Update(disabled=False)
        elif event == "-STARTEN-":
            window.perform_long_operation(func=TranslateAsync, end_key="-TRANSLATIONDONE-")
        elif event == "-SPEICHERN-":
            file_path = values["-SPEICHERN-"]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(protokoll))
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(file_path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', file_path))
        elif event == "-TRANSLATIONDONE-":
            window["-OUTPUT-"].Update("\n".join(protokoll))
            pass
    window.close()

if __name__ == '__main__':
    main(sys.argv[1:])