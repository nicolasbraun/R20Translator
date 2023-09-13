import translate
import replace
import settings
import utils

from appdirs import *
from pathlib import Path
from deep_translator import GoogleTranslator

# # For local Gooey dev
# sys.path.insert(0, "/Users/nicolasbraun/Sources/Gooey")
from gooey import GooeyParser

APPNAME = "R20Translator"
APP_AUTHOR = "Nicolas Braun"
VERSION = "1.0.0"


def parseArgs():
    parser = GooeyParser(description="Translate ZIP Exports from R20Exporter")

    mandatory_group = parser.add_argument_group(
        "Mandatory Parameters",
    )
    mandatory_group.add_argument(
        "-z",
        "--zip",
        default="campaign.zip",
        help="Path to the ZIP file for R20Exporter.",
        widget="FileChooser",
        gooey_options={"full_width": True},
        required=True,
    )
    mandatory_group.add_argument(
        "-l",
        "--target_lang",
        choices=[
            GoogleTranslator().get_supported_languages(as_dict=True)[k]
            for k in GoogleTranslator().get_supported_languages(as_dict=True)
        ],
        help="The lang to translate to",
        widget="FilterableDropdown",
        gooey_options={"full_width": True},
        required=True,
    )
    translations_group = parser.add_argument_group(
        "Translations",
    )
    translations_group.add_argument(
        "-c",
        "--custom_translations_folder",
        help="The folder with all the CSV. Refer to the doc for the format.",
        gooey_options={"full_width": True},
        widget="DirChooser",
    )
    translations_group.add_argument(
        "--use_embedded",
        help="If checked some premade translations (monsters, spells) will be used. You can check the code repository to know which ones",
        action="store_true",
    )

    translations_group.add_argument(
        "--display_original_values_in_parenthesis",
        help="Words translated with custom/embedded translation will be display like this Translated Value (English Value)",
        action="store_true",
    )

    optional_group = parser.add_argument_group(
        "Optional Parameters",
        "Uses this if for some reason you need to modify the app behavior. Mostly if the json format changed",
    )
    optional_group.add_argument(
        "--keys_to_process",
        default="notes,gmnotes,n,name,bio",
        help="The keys in the JSON to translate.",
        gooey_options={"full_width": True},
    )
    optional_group.add_argument(
        "--keys_to_ignore",
        default="attributes",
        help="Some hash in the json contains the key to process but they should not be processed. As the value is a ForgeVTT key (like spell) ",
        gooey_options={"full_width": True},
    )
    optional_group.add_argument(
        "--split_markers",
        default="\\n,. ,<br>,</td>,<hr>,</span>",
        help="Used to split text where it seems the most relevant because Google only allows 5000 chars.",
        gooey_options={"full_width": True},
    )
    optional_group.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    return args


def process():
    settings.init()
    args = parseArgs()
    print(args)

    settings.zip_file_path = args.zip
    settings.campaign_name = utils.sanitize(Path(settings.zip_file_path).stem).lower()
    settings.split_markers = args.split_markers.split(",")
    settings.keys_to_process = args.keys_to_process.split(",")
    settings.ignore_list = args.keys_to_ignore.split(",")
    settings.target_language = args.target_lang
    settings.verbose = bool(args.verbose)
    settings.custom_translations_folder = args.custom_translations_folder
    settings.use_embedded_custom_translations = args.use_embedded
    settings.display_original_values_in_parenthesis = (
        args.display_original_values_in_parenthesis
    )
    # Define the dir where app data will be stored.
    settings.working_dir = (
        f"{user_data_dir(APPNAME, APP_AUTHOR)}/{settings.campaign_name}"
    )
    print(f"Working dir: {settings.working_dir}")
    if not os.path.exists(settings.working_dir):
        os.makedirs(settings.working_dir)

    settings.translations_path = f"{settings.working_dir}/{settings.campaign_name}_translations_mapping_{settings.target_language}.json"

    translate.load_translations_mapping()

    print("➡️ Step 1: Translating")
    translate.translate_zip()

    print("➡️ Step 2: Replacing")
    replace.replace_in_zip()

    # Display error if some translations failed
    if settings.translations_errors:
        print("❌ Some errors where encountered while translating the campaign")
        print("❌ The generated ZIP might be partially translated")
        print("❌ To fix you can wait and relaunch the program to retry")
        print(
            "❌ According to Google, you are allowed to make up to 200k requests per day"
        )
        print("❌ Errors details:")
        for error in settings.translations_errors:
            print(f"{error}: {settings.translations_errors[error]} occurrences")


if __name__ == "__main__":
    process()
