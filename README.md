# Проект чат-клиента

Данный проект представляет собой "оконный" чат-клиент. Прилагающиеся скрипты позволяют авторизоваться и вести переписку с dvmn.org

## Как установить

Для разработки использовался Python версии 3.10 (возможно будет работать с более низкой, но не гарантируется - зависит от поддержки asyncio).

```bash
pip install -r requirements.txt
```

## Как запустить

```bash
--- для регистрации пользователя
python create_token.py

--- для запуска программы
python worker.py
```


