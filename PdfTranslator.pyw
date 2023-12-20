# Siehe https://skeptric.com/python-offline-translation/

# CUDA Installation laut https://pytorch.org/get-started/locally/ : pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

VERSION = "1.0.0"

import os
import PyPDF2
from typing import Sequence
import PySimpleGUI as sg
import subprocess, os, platform
import datetime
import hashlib
import sys, getopt
import re

os.environ['HF_HOME'] = "./data/transformers_cache"
from transformers import MarianMTModel, MarianTokenizer

os.environ['STANZA_RESOURCES_DIR'] = "./data/stanza"
import stanza

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

class Translator:
    def __init__(self, source_lang: str, dest_lang: str, use_gpu: bool=False) -> None:
        self.use_gpu = use_gpu
        self.model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{dest_lang}'
        self.model = MarianMTModel.from_pretrained(self.model_name)
        if use_gpu:
            self.model = self.model.cuda()
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        
    def translate(self, texts: Sequence[str]) -> Sequence[str]:
        tokens = self.tokenizer(list(texts), return_tensors="pt", padding=True)
        if self.use_gpu:
            tokens = {k:v.cuda() for k, v in tokens.items()}
        translate_tokens = self.model.generate(**tokens)
        return [self.tokenizer.decode(t, skip_special_tokens=True) for t in translate_tokens]

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

def TranslateAsync():
    global window, values, protokoll
    start_time = datetime.datetime.utcnow()
    file_path = values["-FILENAME-"]
    use_gpu = values["-USEGPU-"]
    source_language_key = supported_languages[values["-SOURCELANGUAGE-"]]
    target_language_key = supported_languages[values["-TARGETLANGUAGE-"]]
    protokoll = [
        "Programminformationen",
        "=====================",
        f"Programm: PdfTranslator.pyw, Version {VERSION}",
        "Quelle: https://github.com/hilderonny/pdf-translator",
        "Übersetzung  mit MarianMT (https://huggingface.co/docs/transformers/model_doc/marian)",
        f"GPU verwendet: {use_gpu}",
        f"Datei: {file_path}",
        f"PDF-Sprache: {values['-SOURCELANGUAGE-']} ({source_language_key})",
        f"Ausgabesprache: {values['-TARGETLANGUAGE-']} ({target_language_key})"
    ]
    # Sätze-Parser vorbereiten
    window["-OUTPUT-"].print(f"Lade Stanza für {values['-SOURCELANGUAGE-']}")
    stanza.download(source_language_key)
    nlp = stanza.Pipeline(source_language_key, processors="tokenize", use_gpu=use_gpu)
    # Translator vorbereiten
    window["-OUTPUT-"].print(f"Lade Translator für {values['-SOURCELANGUAGE-']} - {values['-TARGETLANGUAGE-']}")
    translator = Translator(source_language_key, target_language_key, use_gpu)
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
            direct_text = page.extract_text()
            window["-OUTPUT-"].print("")
            window["-OUTPUT-"].print("Originaltext")
            window["-OUTPUT-"].print("------------")
            window["-OUTPUT-"].print(direct_text)
            # Text übersetzen
            nlp_result = nlp.process(direct_text)
            detected_sentences = list(map(lambda sentence: sentence.text, nlp_result.sentences))
            sentences_to_process = []
            # Aufteilung nach grammatisch erkannten Sätzen
            for sentence in detected_sentences:
                if len(sentence) < 600:
                    if len(sentence) > 1:
                        sentences_to_process.append(sentence)
                else:
                    # Sätze erscheinen zu lang. Aufteilung nach Punktuation
                    for sentence_part in re.split("\.|\?|\!|\:", sentence):
                        if len(sentence_part) > 600:
                            # Immernoch zu lang, Aufteilung nach Zeilenumbrüchen
                            for line in sentence_part.splitlines():
                                if len(line) > 1:
                                    sentences_to_process.append(line)
                        elif len(sentence_part) > 1:
                            sentences_to_process.append(sentence_part)
            translated_text = "\n".join(translator.translate(sentences_to_process))
            #translated_text = "\n".join(translator.translate([direct_text]))
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
    window["-PROGRESSBAR-"].update(1, 1)

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
            sg.FileBrowse(button_text="Datei auswählen ...", target="-FILENAME-", file_types=(("PDF Dokumente", "*.pdf"),))
        ],
        [
            sg.Checkbox("GPU verwenden", default=True, key="-USEGPU-"),
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

    protokoll = []
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