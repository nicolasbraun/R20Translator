import settings
import json
from deep_translator import GoogleTranslator
import zipfile
import re
import custom_translations


def load_translations_mapping():
    try:
        with open(settings.translations_path, "r") as json_file:
            # Parse the JSON data from the file
            settings.translations_mapping = json.load(json_file)
    except FileNotFoundError:
        return {}


def translate_text(text):
    try:
        value = translator.translate(text)
        return value
    except Exception as e:
        if e.message not in settings.translations_errors:
            settings.translations_errors[e.message] = 1
        else:
            settings.translations_errors[e.message] += 1
        print("Error while translating text:", e.message)
        return None


def translate_value(value):
    value = value.strip()
    translated_value = None
    # Already translated
    if value in settings.translations_mapping:
        return
    # In custom
    if value in settings.custom_translations:
        return
    # This is a bit of a hack but it appear some references are in the JSON with the / even though those are 2 separared folders.
    if "/" in value and not any([x in value for x in ["http", "</"]]):
        translated_parts = []
        for part in value.split("/"):
            translated_part = translate_value(part)
            if translated_part:
                translated_parts.append(translated_part)
        if len(translated_parts) > 0:
            translated_value = "/".join(translated_parts)

    # To big for Google API/ Translate splitted
    elif len(value) > 4999:
        translated_value = process_chunked_value(value)
    else:
        translated_value = translate_text(value)
    if translated_value:
        settings.translations_mapping[value] = translated_value


def process_chunk(chunk):
    if len(chunk) == 0:
        return None
    if chunk in settings.split_markers:
        return chunk
    # check it contains at least one letter
    pattern = r"[a-zA-Z]"
    if not re.search(pattern, chunk):
        return chunk
    translation = translate_text(chunk)
    if translation:
        return translation
    else:
        print("Failed to translate chunk:", chunk)
        return chunk


def process_chunked_value(value):
    translated_chunks = []
    current_chunk = ""
    # We go from char to char until a split marker is found, then translate.
    for char in value:
        current_chunk += char
        if any(marker in current_chunk for marker in settings.split_markers):
            translated_chunk = process_chunk(current_chunk)
            if translated_chunk is not None:
                translated_chunks.append(translated_chunk)
            current_chunk = ""
    else:
        # TODO: Ensure the remaining part is not 5000 event if it means chunking randomly
        translated_chunk = process_chunk(current_chunk)
        if translated_chunk is not None:
            translated_chunks.append(translated_chunk)
    return "".join(translated_chunks) if translated_chunks else value


def process_json(data):
    global translations_count
    if isinstance(data, dict):
        for key, value in data.items():
            translations_count += 1
            if translations_count % 10000 == 0:
                print(
                    f" {translations_count} translations made. Still processing, please wait"
                )
            if key in settings.ignore_list:
                continue
            if key in settings.keys_to_process and isinstance(value, str) and value:
                translate_value(value)
            elif isinstance(value, (dict, list)):
                process_json(value)
    elif isinstance(data, list):
        for item in data:
            process_json(item)


def translate_zip():
    global translator
    translator = GoogleTranslator("en", settings.target_language)
    global translations_count
    translations_count = 0
    custom_translations.load_custom_translations()
    try:
        with zipfile.ZipFile(settings.zip_file_path, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(".json") and not file_name.startswith("__MACOSX"):
                    print("Processing file:", file_name)
                    json_data = zip_ref.read(file_name).decode("utf-8")
                    json_data = json.loads(json_data)
                    process_json(json_data)
    finally:
        with open(settings.translations_path, "w") as json_file:
            json.dump(settings.translations_mapping, json_file, indent=4)
