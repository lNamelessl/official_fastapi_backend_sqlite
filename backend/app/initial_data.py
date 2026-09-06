import logging

from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    settings.log_bootstrap_password_once(logger)
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
