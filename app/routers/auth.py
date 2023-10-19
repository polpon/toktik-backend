from datetime import timedelta

from fastapi import Depends, HTTPException, Response, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.models.tokenModel import Token
from app.utils.utils import OAuth2PasswordBearerWithCookie, create_access_token, authenticate_user    #new

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/token", response_model=Token)
def login_for_access_token(fake_users_db, response: Response,form_data: OAuth2PasswordRequestForm = Depends()):  #added response as a function parameter
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
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)  #set HttpOnly cookie in response
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")   #changed to use our implementation