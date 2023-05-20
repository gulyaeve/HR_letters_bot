from environs import Env, EnvError

env = Env()
env.read_env()


class Config:
    try:
        proxy_url = env.str("PROXY_URL")
    except EnvError:
        proxy_url = ""
    # Telegram auth:
    telegram_token = env.str("TELEGRAM_API_TOKEN")

    # Bot admins
    bot_admins = env.list("BOT_ADMINS")

    # Email auth:
    class Email:
        email_server = env.str("EMAIL_SERVER")
        email_port = env.int("EMAIL_PORT")
        sender_email = env.str("SENDER_EMAIL")
        email_login = env.str("EMAIL_LOGIN")
        email_password = env.str("EMAIL_PASSWORD")

    # PostgreSQL
    class DBConfig:
        DB_USER = env.str("DB_USER")
        DB_PASS = env.str("DB_PASS")
        DB_HOST = env.str("DB_HOST")
        DB_PORT = env.int("DB_PORT")
        DB_NAME = env.str("DB_NAME")

    # Redis
    REDIS_HOST = env.str("REDIS_HOST")
    REDIS_PORT = env.int("REDIS_PORT")

    POSTCARDS_HOST = env.str("POSTCARDS_HOST")

    # Confluence
    confluence_url = env.str("CONFLUENCE_URL")
    confluence_login = env.str("CONFLUENCE_LOGIN")
    confluence_pass = env.str("CONFLUENCE_PASS")
    confluence_page_id = env.int("PAGE_ID")
