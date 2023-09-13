# What is this for?

This app or script is used to automatically Google Translate a ZIP export from [R20Exporter](https://chrome.google.com/webstore/detail/r20exporter/apbhfinbjilbkljgcnjjagecnciphnoi)

# App usage

## Basic usage

- Launch the app
- Select you original ZIP file
- Select the lang to translate to
- Run

The processing will take a while (can take several hours for big campaign) and a new ZIP will be created in the same folder as the source one.

## Using custom translations

### Your own translations

You can select a folder containing as many CSV files as you like.
The CSV must be a 2 columns CSV with the english value in the first column and the translated one in the second.

```csv
Giant Bear, Ours Géant
Neverwinter, Padhiver
```

💡 Note that you should also include plurals.

💡 When you run the app it will also output a file name `$campaign_proper_nous_$lang.csv` this is a tentative to export the propers nouns in the campaign. You can use this as a template and move it in your custom translations folder.

On a second run it'll be much faster as the translations are stored.

### Embedded translations

The app embarks some generic DnD translation in [`translations_db/$lang`](./translations_db/). You can opt-in to also use those.

Feel free to make a PR to add some !

# Troubleshooting

If some translations fail an error will be displayed, indicating that the translated ZIP might partially translated.

It mostly can occur on:

- random errors
- some kind on limit reached on Google Translate.
- Since we cut text to translate smaller part we might have tried to translate some special characters

You can scroll the logs to see what when wrong and decide if you want to relaunch the process. It will complete the translations (if possible) and recreate the ZIP file.

💡 If you reached some kind of Google Limit, you might need to wait one day, otherwise translations will continue to fail.

# How to use (dev)

1. You must have Python installed. Setup your usual venv.
2. If you intend to use the GUI, install Gooey fork manually. It is a fork from Gooey that better handles dark mode.

```
> pip install git+https://github.com/nicolasbraun/Gooey.git@feat/better_dark_mode#egg=gooey

```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the script commands.

```python
> python3 main.py $OPTIONS # CLI
> python3 main_with_gui.py # GUI
```

Note: The translations might fail if you reach some kind off limit on Google side (or any other error).
It that case the translated ZIP will be created but is partially translated.
Simply relaunch the process until all translations have passed and the ZIP is created.

# Possible enhancements

- [ ] Use DnD offical translation packages
- [ ] What was a script grew bigger. Could use some refactoring

# How to build for x86 on an ARM machine (Mac)

- Need to have install python from the official packager with universal2 architectures
- Create a venv using the x86_64 python executable

```
python3-intel64 -m venv venv
```

- activate

```
source venv/bin/activate
```

- In the venv

```bash
# install requirements
> python -m pip install 'git+https://github.com/nicolasbraun/Gooey.git@feat/better_dark_mode#egg=gooey'
> python -m pip install -r requirements.txt
# Then use the pyinstaller command
> pyinstaller --onefile --windowed --target-arch x86_64 -n R20Translator_mac_x86_64 main_with_gui.py

```
