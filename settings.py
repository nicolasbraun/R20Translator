def init():
    global campaign_name
    campaign_name = ""
    global zip_file_path
    zip_file_path = ""
    global split_markers
    split_markers = []
    global keys_to_process
    keys_to_process = []
    global ignore_list
    ignore_list = []
    global target_language
    target_language = ""
    global working_dir
    working_dir = ""
    global translations_path
    translations_path = ""
    global verbose
    verbose = False
    global translations_errors
    translations_errors = {}

    global translations_mapping
    translations_mapping = {}

    # Custom translations
    global custom_translations_folder
    custom_translations_folder = None
    global custom_translations
    custom_translations = {}
    global use_embedded_custom_translations
    use_embedded_custom_translations = False
    global display_original_values_in_parenthesis
    display_original_values_in_parenthesis = False

    # Proper nouns that might be interesting to translate manually
    global proper_nouns
    proper_nouns = []
