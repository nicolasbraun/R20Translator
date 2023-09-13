import settings
import csv
import os
import utils
import hashlib
import re

# empirically google does not translation uppercased string that do not mean anything
# We replace words we want to translate, for example Orcs, with R20TRANSLATOR_ORCS
# We then translate and replace back.


def load_custom_translations():
    custom_translations_files = []
    if settings.custom_translations_folder:
        for f in os.listdir(settings.custom_translations_folder):
            file_path = os.path.join(settings.custom_translations_folder, f)

            if os.path.isfile(file_path):
                utils.printVerbose(f"Using: {file_path}")
                custom_translations_files.append(file_path)
    print(
        f"Found {len(custom_translations_files)} custom translations files in {settings.custom_translations_folder}"
    )
    if settings.use_embedded_custom_translations:
        print(f"Also using embedded translations for lang {settings.target_language}")
        embedded_translations_path = f"translations_db/{settings.target_language}"
        for f in os.listdir(embedded_translations_path):
            file_path = os.path.join(embedded_translations_path, f)

            if os.path.isfile(file_path) and f.endswith(".csv"):
                utils.printVerbose(f"Using: {file_path}")
                custom_translations_files.append(file_path)
    for f in custom_translations_files:
        parseCSV(f)


def parseCSV(path):
    try:
        with open(path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    original_value, translated_value = row
                    if len(translated_value) > 0:
                        original_value = original_value.strip()
                        translated_value = translated_value.strip()
                        pl = placeholder(original_value)
                        settings.custom_translations[original_value] = {
                            "placeholder": pl,
                            "translation": translated_value,
                        }
                        # We also consider the lowercase. For example in a sentence like the wolf attacks it will be replace
                        settings.custom_translations[original_value.lower()] = {
                            "placeholder": placeholder(original_value.lower()),
                            "translation": translated_value.lower(),
                        }
                        # We add custom translations to the mapping.
                        settings.translations_mapping[pl] = translated_value
    except FileNotFoundError:
        print(f"Custom translation file not found: {path}")


# This method replaces the custom translations found with a pattern that will not be translated by Google


def add_placeholders(string):
    # We build a sorted hash of custom translation so we replace firest the longest words
    # For example Orcs will be replaced before Orc is processed
    sorted_keys = sorted(settings.custom_translations, key=len, reverse=True)

    for key in sorted_keys:
        pattern = r"\b" + re.escape(key) + r"\b"
        string = re.sub(
            pattern, settings.custom_translations[key].get("placeholder"), string
        )
    return string


def remove_placeholders(string):
    if not string:
        print("string none")
    new_string = string
    for key in settings.custom_translations:
        value = settings.custom_translations[key].get("translation")
        new_string = new_string.replace(
            settings.custom_translations[key].get("placeholder"),
            value,
        )
    return new_string


def placeholder(word):
    placeholder = f"R20_{hashlib.shake_256(word.encode('utf-8')).hexdigest(4).upper()}"
    return placeholder
