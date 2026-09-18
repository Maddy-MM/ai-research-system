import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)

    reports = relationship(
        "ResearchReport", back_populates="user", cascade="all, delete-orphan"
    )


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    request_id = Column(String(64), unique=True, index=True, nullable=False)
    username = Column(String(128), index=True, nullable=False, default="admin")
    topic = Column(Text, nullable=False)
    report = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    verification = Column(Text, nullable=True)
    clarifying_question = Column(Text, nullable=True)
    critic_score = Column(Float, nullable=True)
    iteration_count = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    sub_questions_json = Column(Text, nullable=True)
    agent_timings_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="reports")

    @property
    def sub_questions(self) -> list[str] | None:
        if self.sub_questions_json:
            try:
                return json.loads(self.sub_questions_json)
            except Exception:
                return None
        return None

    @sub_questions.setter
    def sub_questions(self, value: list[str] | None) -> None:
        if value is not None:
            self.sub_questions_json = json.dumps(value)
        else:
            self.sub_questions_json = None

    @property
    def agent_timings(self) -> dict | None:
        if self.agent_timings_json:
            try:
                return json.loads(self.agent_timings_json)
            except Exception:
                return None
        return None

    @agent_timings.setter
    def agent_timings(self, value: dict | None) -> None:
        if value is not None:
            self.agent_timings_json = json.dumps(value)
        else:
            self.agent_timings_json = None
