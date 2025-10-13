# MLOps commands cheatsheet

### UV

```bash
uv add pre-commit

uv run pytest tests -rP

uv run uvicorn app:app --reload --port=8000
```

### Pre-commit

```bash
pre-commit clean

pre-commit install

pre-commit run
```

### Docker

```bash
docker build [--no-cache] -t ml-app .

docker compose up
docker compose down
```

### Others

`http://127.0.0.1:8000/docs` - Swagger UI
