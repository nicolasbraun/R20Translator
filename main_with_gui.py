import main
import sys

sys.path.insert(0, "/Users/nicolasbraun/Sources/Gooey")
from gooey import Gooey
from gooey import GooeyParser

@Gooey(
    program_name="R20Translator",
    program_description="Translate ZIP Exports from R20Exporter",
    menu=[
        {
            "name": "About",
            "items": [
                {
                    "menuTitle": "About",
                    "type": "AboutDialog",
                    "name ": "R20Translator",
                    "description": "Automated translation for R20Exporter",
                    "website": "https://github.com/nicolasbraun/R20Translator",
                }
            ],
        }
    ],
    disable_progress_bar_animation=True,
    clear_before_run=True,
    default_size=(610, 530),
    required_cols=1
)
def launchGUI():
    main.process()        
if __name__ == "__main__":
    launchGUI()

