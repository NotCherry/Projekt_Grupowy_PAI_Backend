# Instrukcja uruchomienia projektu FastAPI na Windows

### Wymagania
- Python 3.8 lub nowszy zainstalowany i dostępny w PATH
- PowerShell (domyślny na Windows)
- Folder projektu z plikami `main.py`, `database.py`, `models.py`, `requirements.txt` i folderze `images/` z obrazkami

### Kroki uruchomienia

1. **Wejdź do folderu projektu**

```
cd ścieżka\do\projektu
```


2. **Utwórz i aktywuj środowisko wirtualne**

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Po aktywacji konsola powinna mieć przedrostek `(venv)`.

3. **Zainstaluj wymagane pakiety**

```
pip install -r requirements.txt
```

To zainstaluje FastAPI, Uvicorn i SQLAlchemy zgodnie z listą w `requirements.txt`.

4. **Uruchom serwer FastAPI**
```
python -m uvicorn main:app --reload --port 9000
```

- `--reload` powoduje automatyczne przeładowanie serwera przy zmianach kodu  
- Serwer będzie dostępny pod adresem http://localhost:9000  

5. **Sprawdź działanie**

Otwórz w przeglądarce:

- http://localhost:9000/docs — dokumentacja API  
- http://localhost:9000/flowers — endpoint zwracający listę kwiatów  

### Dodatkowe uwagi

- Jeżeli pojawi się błąd wykonania `Activate.ps1`, zmień politykę uruchamiania PowerShell (jako administrator):

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- W razie problemów z poleceniem `uvicorn`, uruchom je przez Pythona:
```
python -m uvicorn main:app --reload --port 9000
```
