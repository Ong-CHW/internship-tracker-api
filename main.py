from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select

from database import Base, engine, get_db
from models import Application
from schemas import ApplicationCreate, ApplicationRead
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
  "message": "Welcome to my Internship Tracker API"
}

@app.post(
    "/applications",
    response_model=ApplicationRead,
    status_code=201
)
def create_application(
        application: ApplicationCreate,
        db: Session = Depends(get_db)
):
    new_application = Application(**application.model_dump())

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application

@app.get(    "/applications",
    response_model=list[ApplicationRead])
def get_applications(db: Session = Depends(get_db)):
    applications = db.scalars(select(Application)).all()
    return applications

@app.get(
    "/applications/{application_id}",
    response_model=ApplicationRead
)
def get_application(
        application_id: int,
        db: Session = Depends(get_db)
):

    application = db.get(Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail = "Application not found"
        )
    return application

@app.put(
    "/applications/{application_id}",
    response_model=ApplicationRead
)
def update_application(
        application_id: int,
        updated_data: ApplicationCreate,
        db: Session = Depends(get_db)
):
    application = db.get(Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    application.company = updated_data.company
    application.position = updated_data.position
    application.status = updated_data.status
    application.application_date = updated_data.application_date
    application.location = updated_data.location
    application.job_url = updated_data.job_url
    application.notes = updated_data.notes

    db.commit()
    db.refresh(application)

    return application

@app.delete(
    "/applications/{application_id}",
    status_code=204
)
def delete_application(
        application_id: int,
        db: Session = Depends(get_db)
):
    application = db.get(Application, application_id)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

