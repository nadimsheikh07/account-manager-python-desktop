Deployment Guide for PySide6 App (Enhanced Version)

This guide covers building and deploying the PySide6 login app with hashed passwords, session persistence, and instructions to create a Windows executable (.exe).

1. Prerequisites

Python 3.10+ installed

Pip installed

Recommended: virtual environment for dependencies
```bash
python -m venv venv
source venv/Scripts/activate   # Windows
# or
source venv/bin/activate       # macOS/Linux
```
2. Install Dependencies
```bash
pip install PySide6 pyinstaller bcrypt
```

PySide6 → GUI framework

PyInstaller → create executables

bcrypt → secure password hashing

3. Project Structure
```bash
my_app/
│
├─ app.py         # main entry point
├─ login.py       # login form
├─ users.db       # SQLite database
├─ deploy.md      # deployment instructions
├─ icon.ico       # optional application icon
└─ README.md
```

4. Database Setup

Use bcrypt to store hashed passwords.

Example:
```bash
import sqlite3
import bcrypt

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)")
password_hash = bcrypt.hashpw("1234".encode(), bcrypt.gensalt())
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", password_hash))
conn.commit()
conn.close()
```

The app will authenticate using bcrypt.checkpw(password.encode(), stored_hash).

Session persistence:

cursor.execute("CREATE TABLE IF NOT EXISTS session (username TEXT UNIQUE)")


When a user logs in, insert their username into session; clear it on logout.

5. Create Executable with PyInstaller
Basic Build
```bash
pyinstaller --onefile --windowed app.py
```

--onefile → single .exe

--windowed → GUI only, no console

The executable will be in:

dist/app.exe

Include Database and Other Resources
```bash
pyinstaller --onefile --windowed --add-data "users.db;." --icon=icon.ico app.py
```        

--add-data "users.db;." → ensures SQLite database is bundled

On macOS/Linux, replace ; with :

Optional Enhancements

Clean build:
```bash
pyinstaller --clean --onefile --windowed app.py
```

Debug mode:
```bash
pyinstaller --onefile --windowed --debug app.py
```
6. Running the App

Open dist/app.exe.

The app will check the session table:

If a session exists → main app opens

If not → login form appears

Logout clears the session, returning the user to login.

7. Updating the App

Make changes to Python files (app.py, login.py).

Re-run PyInstaller build command.

Replace the old .exe with the new one in distribution.

8. Security Notes

Passwords: Always store hashed passwords (bcrypt). Never store plain text.

Sessions: Currently stored in SQLite; consider encrypting session data for production.

Distribution: Test .exe on a clean Windows environment to ensure all dependencies are included.

Database Backup: If users are stored locally, back up users.db or use a more robust storage solution for multi-user apps.

This setup gives you:

Secure login with hashed passwords

Session persistence across app launches

Ready-to-distribute .exe with all resources bundled