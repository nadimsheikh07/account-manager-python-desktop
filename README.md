## Automatically generate requirements.txt from your current environment 
```bash
pip freeze > requirements.txt
```


## install dependencies from requirements.txt
```bash
python -m pip install -r requirements.txt
```

## make migrations
```bash
python -m alembic revision --autogenerate -m "Initial migration"
```