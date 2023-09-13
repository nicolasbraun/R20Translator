import settings
import csv


def add(string):
    # This has already been given as a custom translation.
    if settings.custom_translations.get(string) is not None:
        return
    if string in settings.proper_nouns:
        return
    settings.proper_nouns.append(string)


def save():
    try:
        proper_nouns_output_path = settings.zip_file_path.replace(
            ".zip", f"_proper_nouns_{settings.target_language}.csv"
        )
        with open(proper_nouns_output_path, "w") as csvfile:
            writer = csv.writer(
                csvfile,
            )
            for k in settings.proper_nouns:
                writer.writerow([k, None])
    except IOError:
        print("Proper nouns CSV could not be saved")
