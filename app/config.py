import datetime

from envparse import env

TELEGRAM_TOKEN = env.str("TELEGRAM_TOKEN")
BOT_PUBLIC_PORT = env.int("BOT_PUBLIC_PORT", default=8080)
SUPER_USER_ID = env.int("SUPER_USER_ID", default=0)
URBAN_DP_ID = env.int("URBAN_DP_ID", default=0)

REDIS_HOST = env.str("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_DB_FSM = env.int("REDIS_DB_FSM", default=0)
REDIS_DB_JOBSTORE = env.int("REDIS_DB_JOBSTORE", default=1)
REDIS_DB_JOIN_LIST = env.int("REDIS_DB_JOIN_LIST", default=2)


JOIN_CONFIRM_DURATION = datetime.timedelta(minutes=5)
JOIN_NO_MEDIA_DURATION = datetime.timedelta(minutes=1)

SUPERUSER_STARTUP_NOTIFIER = env.bool("SUPERUSER_STARTUP_NOTIFIER", default=False)

RULES_MSG_LINK = "https://t.me/212"
