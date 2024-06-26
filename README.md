1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365
5. sudo nano .env
    FLASK_APP_KEY="randomkey"
    MYSQL_HOST="localhost"
    MYSQL_USER="root"
    MYSQL_PASSWORD="root"
    MYSQL_DB="pythonlogin"
6. python main.py
