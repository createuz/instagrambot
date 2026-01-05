from aiogram.types import BotCommand
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.utils.yaml import YAMLSettings, find_assets_sources


class Assets(YAMLSettings):
    commands: dict[str, list[BotCommand]] = Field(default_factory=dict)

    model_config = SettingsConfigDict(
        yaml_file_encoding="utf-8",
        yaml_file=find_assets_sources(),
    )
