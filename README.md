# АВТОТРЕЙД: сайт + Python backend (версия 2)

Что нового: отклики сначала сохраняются в базу, Telegram стал необязательным уведомлением.
Менеджер работает на странице /admin (вход по ключу ADMIN_KEY): смотрит отклики, отмечает
«обработан», модерирует отзывы, скачивает CSV для Excel.

Файлы: main.py, admin.html, requirements.txt, site/ (index.html, style.css, script.js),
autotrade.service, Caddyfile.

## Локально (Windows PowerShell, в папке проекта)
1. Один раз: python -m venv venv, затем venv\Scripts\python.exe -m pip install -r requirements.txt
2. Старую базу тестов удалить: del data.db
3. $env:ADMIN_KEY="длинный_ключ_от_12_символов"
   (по желанию Telegram: $env:BOT_TOKEN="..." и $env:CHAT_ID="...")
4. venv\Scripts\python.exe -m uvicorn main:app --port 8000
5. Сайт: http://127.0.0.1:8000   Админка: http://127.0.0.1:8000/admin

## Сервер (Ubuntu)
1. apt update && apt install -y python3-venv caddy
2. mkdir -p /opt/autotrade, скопировать туда main.py, admin.html, requirements.txt и папку site
3. cd /opt/autotrade && python3 -m venv venv && venv/bin/pip install -r requirements.txt
4. Вписать ключ в autotrade.service, положить в /etc/systemd/system/, затем systemctl enable --now autotrade
5. /etc/caddy/Caddyfile из этого архива (подставить домен), затем systemctl restart caddy
6. Проверка Telegram с сервера (необязательно):
   curl -m 10 -s -o /dev/null -w "%{http_code}\n" https://api.telegram.org   (302 = доступен)

## Резервная копия
Копируйте файл data.db, например раз в сутки через cron.
