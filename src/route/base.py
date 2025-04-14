import re
from typing import TYPE_CHECKING

from persica.factory.component import BaseComponent
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from src.core.web_app import WebApp
from src.env import env_config

if TYPE_CHECKING:
    from starlette.middleware.base import RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response


def check_redirect(request: "Request") -> bool:
    new = request.url.path
    if not new:
        return False
    new = re.sub(r':/(?!/)', "://", new)
    if new in ["/", "/favicon.ico"]:
        return False
    return True


def get_redirect_response(request: "Request") -> RedirectResponse:
    new = request.url.path[1:]
    new = re.sub(r':/(?!/)', "://", new)
    return RedirectResponse(url=new, status_code=302)


class UserAgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: "Request", call_next: "RequestResponseEndpoint"
    ) -> "Response":
        user_agent = request.headers.get("User-Agent")
        need_redirect = check_redirect(request)
        if need_redirect and ((not user_agent) or ("bot" not in user_agent.lower())):
            return get_redirect_response(request)
        return await call_next(request)


class BaseRoutePlugin(BaseComponent):
    def __init__(self, web_app: WebApp):
        if not env_config.DEBUG:
            web_app.app.add_middleware(UserAgentMiddleware)
