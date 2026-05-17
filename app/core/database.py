from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.utils.logging_system import log_errors, system_logger

engine = create_engine(
    settings.database_url,
    connect_args={} if "postgresql" in settings.database_url else {"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@log_errors(system_logger)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
