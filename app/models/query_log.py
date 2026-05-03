from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, Text

from app.db.database import Base


class QueryLog(Base):
    __tablename__='query_logs'

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    question=Column(Text,nullable=False)
    final_answer=Column(Text,nullable=True)
    sources=Column(JSON,nullable=True)
    hallucination_score=Column(Float,nullable=True)
    web_search_used=Column(Boolean,default=False,nullable=False)
    response_time=Column(Float,nullable=True)
    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        nullable=False
    )
