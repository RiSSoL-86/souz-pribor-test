# souz-pribor

Генерация B2B-карточки измерительного прибора из JSON через OpenAI.

## Запуск

```bash
cp src/.env.example src/.env      # вписать OPENAI_API_KEY и OPENAI_PROXY
docker volume create db_data
make compose.dev
```

`OPENAI_PROXY` нужен там, где OpenAI недоступен напрямую (из РФ отвечает 403): `http://user:pass@host:port`.

Swagger: http://localhost:8000/api/docs/

## Документация

- [API](docs/api.md)
- [Как устроено, промпт, ограничения](docs/design.md)
