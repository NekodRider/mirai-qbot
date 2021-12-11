# mirai-http-api 及 sentry 设置
app_configs = {
    "account": "88888888",
    "authKey": "12345678",
    "host": "http://localhost:23333",
    "websocket": True,
    "sentry_sdk": {
        "dsn": "https://xxxxx.sentry.io/xxxx",
        "traces_sample_rate": 1
    }
}

# bot 设置
bot_configs = {
    "debug": False,
    "prefix": "/",
}
