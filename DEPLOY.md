## Install Dependencies

```bash
pip install PySide6 PyInstaller bcrypt
```

## Create Executable with PyInstaller

Basic Build

```bash
python -m PyInstaller --name="Khabir Hisab" --onefile --windowed app.py --icon=icon.ico
```

## Include Database and Other Resources

```bash
python -m PyInstaller --name="Khabir Hisab" --onefile --windowed --add-data "users.db;." --icon=icon.ico app.py
```

## Clean build:

```bash
python -m PyInstaller --name="Khabir Hisab" --clean --onefile --windowed app.py
```

## Debug mode:

```bash
python -m PyInstaller --name="Khabir Hisab" --onefile --windowed --debug app.py
```
