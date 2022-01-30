# Проект чат-клиента

Данный проект состоит из 2-х частей: "отправитель" и "получатель".  
для запуска "получателя" используется main.py - позоволяет отобразить в консоль все отправляемые сообщения в чат.  
для запуска "отправителя" используется write_message.py с ключом -m - позовляет отправить произвольное сообщение в чат/зарегистрироваться/войти в систему.  

## Как установить

Для разработки использовался Python версии 3.10 (возможно будет работать с более низкой, но не гарантируется - зависит от поддержки asyncio).

```bash
pip install -r requirements.txt
```

## Как запустить

```bash
--- для запуса получателя
python main.py

--- для запуска отправителя
python write_messages.py -m 'Some message'
```


