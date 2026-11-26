from fastapi import Response

from app.application.services.auth_service import REFRESH_TOKEN_DAYS

REFRESH_COOKIE = "refresh_token"
REFRESH_COOKIE_PATH = "/auth"


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=REFRESH_TOKEN_DAYS * 86400,
        path=REFRESH_COOKIE_PATH,
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)