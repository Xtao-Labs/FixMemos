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


def get_redirect_response(request: "Request") -> RedirectResponse:
    new = request.path_params.get("path")
    return RedirectResponse(url=new, status_code=302)


class UserAgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: "Request", call_next: "RequestResponseEndpoint"
    ) -> "Response":
        user_agent = request.headers.get("User-Agent")
        if (not user_agent) or ("telegram" not in user_agent.lower()):
            return get_redirect_response(request)
        return await call_next(request)


class BaseRoutePlugin(BaseComponent):
    def __init__(self, web_app: WebApp):
        if not env_config.DEBUG:
            web_app.app.add_middleware(UserAgentMiddleware)
