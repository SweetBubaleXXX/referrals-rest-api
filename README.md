## Deployment

Following environmental variables are required:

- SECRET_KEY
- DB_USER
- DB_PASSWORD
- EMAIL_HUNTER_API_KEY

Place them in `.env.prod` file.

To deploy run:

```
docker compose --env-file .env.prod up -d
```

## Development

Install dependencies:

```
poetry install --no-root
```

Run tests:

```
poetry run pytest
```
