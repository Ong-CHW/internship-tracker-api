from datetime import date
from typing import Literal
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    position: str = Field(min_length=1, max_length=100)

    status: Literal[
        "Applied",
        "Interview",
        "Offer",
        "Rejected"
    ] = "Applied"

    application_date: date

    location: str | None = Field(default=None, max_length=100)
    job_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @field_validator("company", "position")
    @classmethod
    def non_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Cannot be blank or spaces only")

        return value

    @field_validator("job_url")
    @classmethod
    def validate_job_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        parsed = urlparse(value)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("job_url must be an HTTP or HTTPS URL")

        return value


class ApplicationRead(ApplicationCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)