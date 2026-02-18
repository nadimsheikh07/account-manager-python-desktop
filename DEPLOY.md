## Install Dependencies

```bash
pip install PySide6 pyinstaller bcrypt
```

## Create Executable with PyInstaller

Basic Build

```bash
pyinstaller --onefile --windowed app.py
```

## Include Database and Other Resources

```bash
pyinstaller --onefile --windowed --add-data "users.db;." --icon=icon.ico app.py
```

## Clean build:

```bash
pyinstaller --clean --onefile --windowed app.py
```

## Debug mode:

```bash
pyinstaller --onefile --windowed --debug app.py
```
