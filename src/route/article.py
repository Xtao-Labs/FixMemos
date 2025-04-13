from pathlib import Path
from persica.factory.component import AsyncInitializingComponent
from starlette.requests import Request
from starlette.responses import HTMLResponse, FileResponse, RedirectResponse

from .base import get_redirect_response

from src.api.render import RenderArticle

from src.core.web_app import WebApp
from src.error import ArticleError, ResponseException
from src.log import logger


class ArticlePlugin(AsyncInitializingComponent):
    def __init__(self, web_app: WebApp, render: RenderArticle):
        self.render = render
        web_app.app.add_api_route("/favicon.ico", self.icon)
        web_app.app.add_api_route("/{path:path}", self.parse_article)

    @staticmethod
    async def icon():
        return FileResponse(Path("src")/ "res" / "favicon.ico")

    async def parse_article(self, path: str, request: Request):
        if not path:
            return RedirectResponse(url="https://xtao.de", status_code=302)
        try:
            return HTMLResponse(await self.render.process_article(path))
        except ResponseException as e:
            logger.warning(e.message)
            return get_redirect_response(request)
        except ArticleError as e:
            logger.warning(e.msg)
            return get_redirect_response(request)
        except Exception as _:
            logger.exception("Failed to get article url[%s]", path)
            return get_redirect_response(request)
