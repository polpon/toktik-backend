from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Response, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.models.tokenModel import Token, TokenData
from app.utils.utils import create_access_token, authenticate_user, get_user    #new
from app.utils.auth import OAuth2PasswordBearerWithCookie

from jose import JWTError, jwt

router = APIRouter()
SECRET_KEY = "a87fa0c0149a26f02696619942c15a588794b8abe1fdb9ff55b6aac08ec4b0c7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/whoami")   #changed to use our implementation

@router.post("/login", response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
    ):

    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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

@router.get("/whoami")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@router.delete("/logout")
async def signout(response: Response):
    response.delete_cookie(key="access_token")

    return True