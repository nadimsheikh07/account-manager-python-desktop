## Install Dependencies

```bash
pip install PySide6 pyinstaller bcrypt
```

## Create Executable with PyInstaller

Basic Build

```bash
pyinstaller --name="Account Manager" --onefile --windowed app.py --icon=icon.ico
```

## Include Database and Other Resources

```bash
pyinstaller --name="Account Manager" --onefile --windowed --add-data "users.db;." --icon=icon.ico app.py
```

## Clean build:

```bash
pyinstaller --name="Account Manager" --clean --onefile --windowed app.py
```

## Debug mode:

```bash
pyinstaller --name="Account Manager" --onefile --windowed --debug app.py
```
