import settings
from utils import printVerbose
import json
import os
import re
import proper_nouns
import zipfile
import custom_translations
from shutil import rmtree


# Apply translations to data based on mapping and keys
def apply_translations(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in settings.ignore_list:
                continue
            if key in settings.keys_to_process and isinstance(value, str) and value:
                # We strip here as sometimes exporter exports with trailing space and creates folder duplicates
                value = value.strip()
                data[key] = translation(value)
            elif isinstance(value, (dict, list)):
                apply_translations(value)
    elif isinstance(data, list):
        for item in data:
            apply_translations(item)


def translation(value):
    new_value = value
    if value in settings.translations_mapping:
        new_value = settings.translations_mapping[value]
    else:
        value_with_placeholders = custom_translations.add_placeholders(value)
        if value_with_placeholders in settings.translations_mapping:
            new_value = custom_translations.remove_placeholders(
                settings.translations_mapping[value_with_placeholders]
            )
            if settings.display_original_values_in_parenthesis:
                new_value += f" ({value})"
    return new_value


# Process JSON file, applying translations
def process_json(file_path):
    with open(file_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    apply_translations(json_data)
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)


def rename(path):
    base_name = os.path.basename(path)
    isPng = base_name.endswith(".png")
    base_name = base_name.replace(".png", "").strip()
    # If the element is in characters or pages folders it might be a proper noun
    can_be_proper_noun = any(ele in path for ele in ["characters", "pages"])
    # Usually folder or PNG follow the format XXX - NAME, where name is in the JSON
    matches = re.match(r"((\d+\s*-\s*)(.+))", base_name)
    new_name = None
    if matches:
        name = matches.group(3).strip()
        if can_be_proper_noun:
            proper_nouns.add(name)
        translated_name = translation(name)
        new_name = f"{matches.group(2)}{translated_name}"
    # in some odd cases the name is directly the one from the json, without the numbers.
    else:
        new_name = translation(base_name)
    if new_name != base_name:
        try:
            new_path = os.path.join(os.path.dirname(path), new_name)
            if isPng:
                new_path = new_path + ".png"
            os.rename(path, new_path)
        except Exception as e:
            if settings.verbose:
                print(e)
                print(
                    "Could not rename folder, happens when there is duplicated folders:",
                    path,
                )
                print("Everything should work has expected")


# Process a folder, including subfolders, applying translations
def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".json"):
                process_json(file_path)
            # Rename PNGs
            if file.endswith(".png"):
                rename(file_path)

        # Rename folder
        rename(root)


def replace_in_zip():
    temp_folder = f"{settings.working_dir}/temp_{settings.campaign_name}_{settings.target_language}"
    with zipfile.ZipFile(settings.zip_file_path, "r") as zip_ref:
        zip_ref.extractall(temp_folder)
    try:
        process_folder(temp_folder)

        zip_output_path = settings.zip_file_path.replace(
            ".zip", f"_{settings.target_language}.zip"
        )
        # Remove any previous run ZIP
        if os.path.exists(zip_output_path):
            os.remove(zip_output_path)
        with zipfile.ZipFile(zip_output_path, "w") as zip_ref:
            for foldername, _, filenames in os.walk(temp_folder):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, temp_folder)
                    zip_ref.write(file_path, arcname)
        proper_nouns.save()
    except Exception as e:
        print("❌ Something went wrong while translating campaign.")
        print("❌ You can try again by relaunching the program")
        print("❌ If the problem persists open an issue on Github")
        print("❌ https://github.com/nicolasbraun/R20Translator/issues")
        print("❌ Here is the error")
        print(e)
    else:
        print("✅Translated campaign has been saved to:", zip_output_path)
    finally:
        try:
            rmtree(temp_folder)
        except Exception as e:
            print("⚠️ Something when wrong whole cleaning temp data.")
            print(f"⚠️ You can remove it by yoursellf at path:${temp_folder}")
