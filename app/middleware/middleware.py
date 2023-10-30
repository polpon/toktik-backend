from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.auth import OAuth2PasswordBearerWithCookie

allowed_endpoints = {"logout","openapi.json", "whoami" ,"docs", "login", "register", "process-completed", "refresh"}

class MyMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # ignore if its an allowed endpoint
        if request.url.path.split("/")[-1] not in allowed_endpoints:

            # do something with the request object, for example
            try:
                await OAuth2PasswordBearerWithCookie(tokenUrl=request.url.path)(request)
            except Exception as e:
                print(e)
                return JSONResponse("Not Authenticated", 401, {"WWW-Authenticate": "Bearer"})

        # process the request and get the response
        response = await call_next(request)

        return response