from datetime import date

from pydantic import BaseModel, ConfigDict, Field

class ApplicationCreate(BaseModel):
    company : str = Field(min_length=1)
    position: str = Field(min_length=1)
    status: str = "Applied"
    application_date: date

    location: str | None = None
    job_url: str | None = None
    notes: str | None = None

class ApplicationRead(ApplicationCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
