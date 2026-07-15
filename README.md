## Create a virtual environment for your project:
```bash
python -m venv venv
```
## Activate it:

### Windows
```bash
venv\Scripts\activate
```

### Linux/macOS
```bash
source venv/bin/activate
```

## Automatically generate requirements.txt from your current environment 
```bash
python -m pip freeze > requirements.txt
```


## install dependencies from requirements.txt
```bash
python -m pip install -r requirements.txt
```

## make migrations
```bash
python -m alembic revision --autogenerate -m "Initial migration"
```