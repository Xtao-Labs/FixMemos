import traceback
from typing import Optional

from bs4 import BeautifulSoup

from httpx import URL

from persica.factory.component import AsyncInitializingComponent

from src import template_env
from src.api.api import ApiClient
from src.api.models import Memo
from src.error import ArticleNotFoundError


class RenderArticle(AsyncInitializingComponent):
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self.home_template = template_env.get_template("home.jinja2")
        self.template = template_env.get_template("article.jinja2")
        self.channel_map = {"https://memos.cx.ms": "cxplayworld", "https://memos.xtao.de": "chainwon_channel"}

    @staticmethod
    def find_title(soup: "BeautifulSoup") -> str:
        h = ["h1", "h2", "h3", "h4", "h5"]
        for tag in h:
            title = soup.find(tag)
            if title:
                return title.text.strip()
        return ""

    @staticmethod
    def find_img(soup: "BeautifulSoup") -> Optional[str]:
        img = soup.find("img")
        if img:
            return img["src"]
        return None

    def process_article_data(self, host: str, post_info: "Memo") -> dict:
        soup = BeautifulSoup(post_info.html, "lxml")
        data = {
            "published_time": post_info.createTime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "channel": self.channel_map.get(host, "chainwon_channel"),
            "title": self.find_title(soup),
            "img": self.find_img(soup),
        }
        return data

    @staticmethod
    def get_host_from_url(url: str) -> str:
        parsed_url = URL(url)
        return f"{parsed_url.scheme}://{parsed_url.host}"

    async def process_article(self, path: str) -> str:
        host = self.get_host_from_url(path)
        parse_memo, memo_id = False, None
        if "/memos/" in path:
            memo_id = path.split("/")[-1]
            parse_memo = True
        instance = await self.api_client.get_instance_info(host)
        if parse_memo:
            try:
                memo = await self.api_client.get_memo_info(host, memo_id)
            except Exception as e:
                traceback.print_exc()
                raise ArticleNotFoundError(memo_id) from e
            user = await self.api_client.get_user_info(host, memo.creator_id)
            return self.template.render(
                host=host,
                url=path,
                author=user,
                post=memo,
                instance=instance,
                **self.process_article_data(host, memo),
            )
        owner = await self.api_client.get_instance_owner_id(host)
        user = await self.api_client.get_user_info(host, owner)
        return self.home_template.render(
            url=path,
            author=user,
            instance=instance,
        )
