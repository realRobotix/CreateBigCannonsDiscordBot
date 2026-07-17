from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from typing import Literal, Set

import tomllib
from dotenv import dotenv_values
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH = PROJECT_ROOT / ".env"
CONFIG_DIR = PROJECT_ROOT / "config"

def _config_path() -> Path:
    return PROJECT_ROOT / "settings.toml"


def _read_secret_file(field_name: str) -> str | None:
    env_file_key = f"CBCBOT_{field_name}_FILE"
    env_file_value = os.getenv(env_file_key)
    if env_file_value:
        secret_path = Path(env_file_value)
        if secret_path.exists():
            return secret_path.read_text().strip()
    docker_secret_path = Path("/run/secrets") / field_name.lower()
    if docker_secret_path.exists():
        return docker_secret_path.read_text().strip()
    return None


class TomlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings], toml_path: Path) -> None:
        super().__init__(settings_cls)
        self._toml_path = toml_path
        self._data = self._load()

    def _load(self) -> dict[str, object]:
        if not self._toml_path.exists():
            return {}
        return tomllib.loads(self._toml_path.read_text())

    def get_field_value(self, field: str, field_name: str) -> tuple[object | None, str, bool]:
        if field_name not in self._data:
            return None, field_name, False
        return self._data[field_name], field_name, True

    def __call__(self) -> dict[str, object]:
        return dict(self._data)


class SecretFileSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        self._data = self._load()

    def _load(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for field_name in self.settings_cls.model_fields:
            secret_value = _read_secret_file(field_name)
            if secret_value is not None:
                values[field_name] = secret_value
        return values

    def get_field_value(self, field: str, field_name: str) -> tuple[object | None, str, bool]:
        if field_name not in self._data:
            return None, field_name, False
        return self._data[field_name], field_name, True

    def __call__(self) -> dict[str, object]:
        return dict(self._data)


class Settings(BaseSettings):

    BOT_DISCORD_TOKEN: str
    BOT_DEVELOPERS: Set[int]
    BOT_AUTO_RELOAD: bool = False
    BOT_AUTO_LOAD: Set[str] = Field(default_factory=set)
    BOT_TEST_GUILDS: Set[int] = Field(default_factory=set)

    MOD_LATEST_MC_VERSION: str

    GH_API_URL: str
    GH_API_USER: str
    GH_API_TOKEN: str

    CF_API_MOD_ID: str
    CF_API_KEY: str

    STARS_VOTE_CHANNEL_IDS: Set[int]
    STARS_REPOST_CHANNEL_ID: int
    STARS_THRESHOLD: int = 1
    STARS_BYPASS: Set[int] = Field(default_factory=set)

    QUICKSAND_ENABLED: bool = False
    QUICKSAND_WATCH_CHANNEL_IDS: Set[int] = Field(default_factory=set)
    QUICKSAND_REPORT_CHANNEL_ID: int = 0
    QUICKSAND_MUTED_ROLE_ID: int = 0
    QUICKSAND_MIN_MATCHES: int = 3
    QUICKSAND_WINDOW_SECONDS: int = 60
    QUICKSAND_SIMILARITY_THRESHOLD: float = 0.9
    QUICKSAND_ACTION_TIMEOUT_SECONDS: int = 3600
    QUICKSAND_EXEMPT_ROLE_IDS: Set[int] = Field(default_factory=set)
    QUICKSAND_EXEMPT_USER_IDS: Set[int] = Field(default_factory=set)

    model_config = SettingsConfigDict(
        env_prefix="CBCBOT_",
        env_file=str(DOTENV_PATH),
        case_sensitive=True,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        toml_source = TomlConfigSettingsSource(settings_cls, _config_path())
        secret_source = SecretFileSettingsSource(settings_cls)
        return (
            init_settings,
            secret_source,
            env_settings,
            dotenv_settings,
            toml_source,
            file_secret_settings,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
