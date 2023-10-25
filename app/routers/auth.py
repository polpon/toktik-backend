from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Response, status, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.engine import SessionLocal, engine
from app.db import models, schemas, crud

from app.models.tokenModel import Token, TokenData
from app.utils.utils import create_access_token#, authenticate_user   #new
from app.utils.auth import OAuth2PasswordBearerWithCookie
from app.db.crud import authenticate_user, get_user_by_username

from jose import JWTError, jwt

router = APIRouter()
SECRET_KEY = "a87fa0c0149a26f02696619942c15a588794b8abe1fdb9ff55b6aac08ec4b0c7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/whoami")   #changed to use our implementation

@router.post("/register", response_model=Token)
def create_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    db_user = crud.get_user_by_username(db, username=form_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="username already existed")

    crud.create_user(db=db, user=form_data)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    ## set HttpOnly cookie in response
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/login", response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    ## set HttpOnly cookie in response
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/whoami", response_model=schemas.User)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@router.delete("/logout")
async def signout(response: Response):
    response.delete_cookie(key="access_token")
    return True


@router.get("/get_videos")
async def getVideo(db: Session = Depends(get_db)):
    return crud.get_videos(db)


@router.get("/get_videos/{user_id}")
async def getVideo(user_id: str, db: Session = Depends(get_db)):
    return crud.get_videos_by_user(db, user_id)