# tickers

## Подготовка к запуску

- Установить зависимости: python3.6, postgresql-9.5, postgresql-client-9.5
- Установить пакеты: `pip3.6 install -r requirements.txt`

## Запуск
```
usage: tickers [-h] -d DB_NAME -u DB_USER -p DB_PASS [--db-host DB_HOST]
               [--db-port DB_PORT] [--host HOST] [--port PORT]
               [--tickers-file TICKERS_FILE] [--threads-count THREADS_COUNT]
               [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -d DB_NAME, --db-name DB_NAME
                        Database name
  -u DB_USER, --db-user DB_USER
                        Postgres user
  -p DB_PASS, --db-pass DB_PASS
                        Postgres user' password
  --db-host DB_HOST     Postgres host
  --db-port DB_PORT     Postgres port
  --host HOST           Listen on this address
  --port PORT           Listen on this port
  --tickers-file TICKERS_FILE
                        Path to the file wih tickers
  --threads-count THREADS_COUNT
                        Parsing threads count
  --debug               Enable debug mode
```

Запуск без парсинга цен на акции:
```
python3.6 main.py -d tickers -u user -p pass
```

Запуск с парсингом цен на акции:
```
python3.6 main.py -d tickers -u user -p pass --tickers-file <path-to-tickers-file> --threads-count 4
```

## API
Запросы с префиксом `/api` возвращают данные в виде JSON.

- `/` или `/api` - получить список акций
- `/%TICKER%` или `/api/%TICKER%` - получить таблицу цен за последние 3 месяца на заданную акцию
- `/%TICKER%/insider` или `/api/%TICKER%/insider` - получить таблицу с данными торговли владельцев компании
- `/%TICKER%/insider/%NAME%` или `/api/%TICKER%/insider/%NAME%` - получить таблицу с данными торговли заданного владельца компании
- `/%TICKER%/analytics?date_from=..&date_to=..` или `/api/%TICKER%/analytics?date_from=..&date_to=..` - данные о ранице цен в заданных датах
- `/%TICKER/delta?value=N&type=(open/high/low/close)` или `/api/%TICKER/delta?value=N&type=(open/high/low/close)` - информация о минимальном периоде, когда указанная цена менялась на заданное значение
