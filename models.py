from datetime import date

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    company: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30))
    application_date: Mapped[date]

    location: Mapped[str | None] = mapped_column(String(100))
    job_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)

