import os

MAIL_USERNAME = os.environ.get("MAIL_USERNAME", 'dockd883@gmail.com')
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", 'ybvsneebzblmwoxl')
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_DEFAULT_SENDER = MAIL_USERNAME