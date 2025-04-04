from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select, SQLModel
from models import URL, URLCreate, URLResponse
from database import engine, get_session
import uuid
from datetime import datetime, timedelta


@asynccontextmanager
async def lifespan(app: FastAPI):

    SQLModel.metadata.create_all(engine)
    yield

    engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/shorten", response_model=URLResponse)
def create_short_url(request: URLCreate, session: Session = Depends(get_session)):
    if len(request.original_url) > 2048:
        return URLResponse(success=False, reason="URL too long")

    short_id = str(uuid.uuid4())[:8]
    expiration_date = datetime.now() + timedelta(days=30)

    url_entry = URL(
        id=short_id, original_url=request.original_url, expiration_date=expiration_date
    )
    session.add(url_entry)
    session.commit()

    short_url = f"http://localhost:8000/{short_id}"
    return URLResponse(
        short_url=short_url, expiration_date=expiration_date, success=True
    )


@app.get(
    "/{short_id}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_class=RedirectResponse,
)
def redirect_to_original(short_id: str, session: Session = Depends(get_session)):
    statement = select(URL).where(URL.id == short_id)
    url_entry = session.exec(statement).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if datetime.now() > url_entry.expiration_date:
        raise HTTPException(status_code=410, detail="Short URL expired")

    return url_entry.original_url
