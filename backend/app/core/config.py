import json
import os
import secrets
import warnings
from pathlib import Path
from typing import Literal, Self

from pydantic import (
    EmailStr,
    HttpUrl,
    PrivateAttr,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "sqlite:///./app.db"
DEFAULT_PROJECT_NAME = "FastAPI Backend SQLite"
DEFAULT_FIRST_SUPERUSER = "admin@example.com"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    # Leave unset (empty) to auto-generate a key on first boot, persisted next
    # to the SQLite database so it survives restarts and tokens keep working.
    SECRET_KEY: str = ""
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    FASTAPI_ENV: Literal["development"] | None = None

    PROJECT_NAME: str = DEFAULT_PROJECT_NAME
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
    # Leave FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD unset (empty) to
    # bootstrap an admin with a placeholder email and a generated password
    # (persisted next to the database and logged once on first boot).
    # A custom FIRST_SUPERUSER is validated when the superuser is created.
    FIRST_SUPERUSER: str = ""
    FIRST_SUPERUSER_PASSWORD: str = ""

    _password_generated: bool = PrivateAttr(default=False)

    def _sqlite_db_dir(self) -> Path | None:
        """Directory that holds the SQLite database file, if any."""
        rest = self.DATABASE_URL[len("sqlite:") :]
        if rest.startswith("////"):
            db_path = Path(rest[3:])
        elif rest.startswith("///"):
            db_path = Path(rest[3:])
        else:
            # In-memory or unusual URL: nowhere to persist generated secrets
            return None
        return db_path.resolve().parent

    def _resolve_bootstrap_secrets(self) -> None:
        """Fill unset credentials so a fresh deployment needs zero environment
        variables. Generated values are stored in a file next to the SQLite
        database (on the mounted volume in deployments) so they survive
        restarts; explicitly set environment variables always win."""
        db_dir = self._sqlite_db_dir()
        if db_dir is not None:
            db_dir.mkdir(parents=True, exist_ok=True)
        secrets_file = db_dir / ".bootstrap_secrets.json" if db_dir else None

        stored: dict[str, str] = {}
        if secrets_file and secrets_file.exists():
            try:
                loaded = json.loads(secrets_file.read_text())
                if isinstance(loaded, dict):
                    stored = {
                        str(k): str(v)
                        for k, v in loaded.items()
                        if isinstance(v, str)
                    }
            except (OSError, ValueError):
                stored = {}

        generated: dict[str, str] = {}
        if not self.SECRET_KEY:
            if stored.get("secret_key"):
                self.SECRET_KEY = stored["secret_key"]
            else:
                self.SECRET_KEY = secrets.token_hex(32)
                generated["secret_key"] = self.SECRET_KEY
        if not self.FIRST_SUPERUSER:
            self.FIRST_SUPERUSER = DEFAULT_FIRST_SUPERUSER
        if not self.FIRST_SUPERUSER_PASSWORD:
            if stored.get("first_superuser_password"):
                self.FIRST_SUPERUSER_PASSWORD = stored["first_superuser_password"]
            else:
                self.FIRST_SUPERUSER_PASSWORD = secrets.token_urlsafe(12)
                generated["first_superuser_password"] = self.FIRST_SUPERUSER_PASSWORD
                self._password_generated = True

        if generated and secrets_file:
            payload = {**stored, **generated}
            tmp_file = secrets_file.with_name(".bootstrap_secrets.json.tmp")
            tmp_file.write_text(json.dumps(payload, indent=2))
            os.replace(tmp_file, secrets_file)
            try:
                os.chmod(secrets_file, 0o600)
            except OSError:
                pass

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
        self._resolve_bootstrap_secrets()
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore # ty: ignore[unused-ignore-comment]
