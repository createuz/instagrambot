import os
from dataclasses import dataclass, field
from urllib.parse import urlunparse

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = os.getenv("PG_HOST")
    port: int = int(os.getenv("PG_PORT"))
    user: str = os.getenv("PG_USER")
    password: str = os.getenv("PG_PASSWORD")
    name: str = os.getenv("PG_NAME")
    driver: str = os.getenv("DRIVER")
    db_system: str = os.getenv("DB_SYSTEM")

    def build_db_url(self) -> str:
        return URL.create(
            drivername=f"{self.db_system}+{self.driver}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)


@dataclass
class RedisConfig:
    db: int = int(os.getenv("REDIS_DATABASE"))
    host: str = os.getenv("REDIS_HOST")
    port: int = int(os.getenv("REDIS_PORT"))
    password = None
    # password: str | None = os.getenv("REDIS_PASSWORD")
    username: str | None = os.getenv("REDIS_USERNAME")
    state_ttl: int = int(os.getenv("REDIS_TTL_STATE"))
    data_ttl: int = int(os.getenv("REDIS_TTL_DATA"))

    def build_redis_url(self) -> str:
        credentials = (f"{self.username}:{self.password}@" if self.username and self.password else "")
        return urlunparse(("redis", f"{credentials}{self.host}:{self.port}", f"/{self.db}", "", "", ""))


@dataclass
class CacheConfig:
    enabled: bool = bool(os.getenv("USE_CACHE"))
    host: str = os.getenv("CACHE_HOST")
    port: int = int(os.getenv("CACHE_PORT"))
    password: str = os.getenv("CACHE_PASSWORD")

    def build_cache_url(self) -> str:
        credentials = (f"{self.password}@" if self.password else "")
        return urlunparse(("redis", f"{credentials}{self.host}:{self.port}", "", "", "", ""))


@dataclass
class WebhookConfig:
    enabled: bool = bool(os.getenv("USE_WEBHOOK"))
    url: str = os.getenv("WEBHOOK_URL")
    secret_token: str = os.getenv("WEBHOOK_SECRET_TOKEN")
    host: str = os.getenv("WEBHOOK_HOST")
    port: int = int(os.getenv("WEBHOOK_PORT"))
    max_updates_in_queue: int = int(os.getenv("MAX_UPDATES_IN_QUEUE"))


@dataclass
class CustomApiServerConfig:
    enabled: bool = bool(os.getenv("USE_CUSTOM_API_SERVER"))
    is_local: bool = bool(os.getenv("CUSTOM_API_SERVER_IS_LOCAL"))
    base_url: str = os.getenv("CUSTOM_API_SERVER_BASE")
    file_url: str = os.getenv("CUSTOM_API_SERVER_FILE")


@dataclass
class BotConfig:
    token: str = os.getenv("BOT_TOKEN")
    logging_level: int = int(os.getenv("LOGGING_LEVEL"))


@dataclass
class AppConfig:
    debug: bool = bool(int(os.getenv("LOGGING_LEVEL")))
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)
    custom_api_server: CustomApiServerConfig = field(default_factory=CustomApiServerConfig)
    bot_token: BotConfig = field(default_factory=BotConfig)


ADMIN = 5383531061

conf: AppConfig = AppConfig()
bot: Bot = Bot(token=conf.bot_token.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# print("Database URL:", conf.db.build_db_url())


" https://f0ea-92-63-205-165.ngrok-free.app/bot/7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg"
get_webhook_info = "https://api.telegram.org/bot7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg/getWebhookInfo"
set_webhook = "https://api.telegram.org/bot7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg/setWebhook?url=https://f0ea-92-63-205-165.ngrok-free.app/bot/7189528230:AAEayeWCvI0Jv7YufsMLW8CmqcLPQObbxyg&secret_token=4411f20d872535bf80ab94eaf2c84238bca388352fce0af0a2244bddcc9306d5"
