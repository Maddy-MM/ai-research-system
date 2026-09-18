from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from src.config import get_settings

settings = get_settings()

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import src.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            if engine.dialect.name == "postgresql":
                conn.execute(
                    text(
                        "ALTER TABLE research_reports ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE research_reports ADD COLUMN IF NOT EXISTS execution_time_seconds FLOAT;"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE research_reports ADD COLUMN IF NOT EXISTS agent_timings_json TEXT;"
                    )
                )
                conn.commit()
            elif engine.dialect.name == "sqlite":
                res = conn.execute(
                    text("PRAGMA table_info(research_reports)")
                ).fetchall()
                cols = [r[1] for r in res]
                if cols and "user_id" not in cols:
                    conn.execute(
                        text(
                            "ALTER TABLE research_reports ADD COLUMN user_id INTEGER REFERENCES users(id);"
                        )
                    )
                    conn.commit()
                if cols and "execution_time_seconds" not in cols:
                    conn.execute(
                        text(
                            "ALTER TABLE research_reports ADD COLUMN execution_time_seconds FLOAT;"
                        )
                    )
                    conn.commit()
                if cols and "agent_timings_json" not in cols:
                    conn.execute(
                        text(
                            "ALTER TABLE research_reports ADD COLUMN agent_timings_json TEXT;"
                        )
                    )
                    conn.commit()
    except Exception:
        pass


from src.models import User  # noqa: E402, F401
