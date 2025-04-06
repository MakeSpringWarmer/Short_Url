from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select, SQLModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from models import URL, URLCreate, URLResponse
from database import engine, get_session
from utils import validate_public_url, generate_unique_short_id


@asynccontextmanager
async def lifespan(app: FastAPI):

    SQLModel.metadata.create_all(engine)
    yield

    engine.dispose()


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    ),
)


@app.post("/shorten", response_model=URLResponse)
@limiter.limit("5/minute")
def create_short_url(
    request: Request, url_create: URLCreate, session: Session = Depends(get_session)
):
    if len(url_create.original_url) > 2048:
        return URLResponse(success=False, reason="URL too long")

    validation_result = validate_public_url(url_create.original_url)
    if not validation_result["success"]:
        return URLResponse(success=False, reason=validation_result["reason"])

    short_id = generate_unique_short_id(session)
    expiration_date = datetime.now() + timedelta(days=30)

    url_entry = URL(
        id=short_id,
        original_url=url_create.original_url,
        expiration_date=expiration_date,
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
