O projeto já traz os modelos treinados em `backend/models/`, então você não precisa treinar nada para testar. O que precisa instalar é isto:

- **Python 3.11+** (a `.venv` do zip parece ter sido criada com Python 3.13)
- Extensão **Python** no VS Code
- Extensão **Live Server** no VS Code, ou um servidor simples para abrir o HTML
- As dependências do back-end listadas em `backend/requirements.txt`

As dependências são estas:

```
fastapi
uvicorn[standard]
pydantic
joblib
xgboost
numpy
pandas
scikit-learn
```


### Como subir no VS Code

1. Abra a pasta `EDUMAP` no VS Code.
2. Crie e ative um ambiente virtual dentro de `backend`:

```
cd backend
```

```
python -m venv .venv
```


3. Instale as dependências:

```
pip install -r requirements.txt
```

4. rode a API:
```
uvicorn app.main:app --reload --port 8000
```

5. No front-end, abra `index.html` com o **Live Server** ou com um servidor local.
(No meu eu só abrir o Live Server e já funcionou)
```
python -m http.server 5500
```