import warnings
from typing import Literal, Self

from pydantic import (
    EmailStr,
    HttpUrl,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "sqlite:///./app.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    FASTAPI_ENV: Literal["development"] | None = None

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None

    # Location of the SQLite database file. Accepts, in order:
    # - a SQLAlchemy SQLite URL (sqlite:///./app.db or sqlite:////data/app.db)
    # - a bare file path, absolute or relative (e.g. /data/app.db on a mounted
    #   volume, as commonly injected by platforms like Railway)
    # Remote database URLs (postgres, mysql, ...) are rejected: this template
    # is SQLite-only.
    DATABASE_URL: str = DEFAULT_DATABASE_URL

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_sqlite_url(cls, value: object) -> str:
        database_url = str(value or "").strip()
        if database_url.startswith("sqlite"):
            return database_url
        if "://" in database_url:
            scheme = database_url.split("://", 1)[0]
            raise ValueError(
                f"This template is SQLite-only: DATABASE_URL must be a SQLite "
                f"URL or a file path, got a '{scheme}://' URL."
            )
        if not database_url:
            return DEFAULT_DATABASE_URL
        # sqlite:/// + "/data/app.db" yields the 4-slash absolute form
        # (sqlite:////data/app.db); sqlite:/// + "app.db" yields the
        # 3-slash relative form (sqlite:///app.db).
        return f"sqlite:///{database_url}"

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.FASTAPI_ENV == "development":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore # ty: ignore[unused-ignore-comment]
