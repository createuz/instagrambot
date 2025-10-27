from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

ASSETS_SOURCE_DIR = Path(__file__).resolve().parent.parent / "telegram" / "assets"


class YAMLSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


def find_assets_sources() -> list[Path | str]:
    return list(ASSETS_SOURCE_DIR.rglob("*.yml"))
