from typing import Optional, Any

import httpx

from persica.factory.component import AsyncInitializingComponent

from src.api.models import Author, Instance, Memo


class ApiClient(AsyncInitializingComponent):
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def shutdown(self):
        if self.client.is_closed:
            return
        await self.client.aclose()

    async def req(self, url: str) -> dict[str, Any]:
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_instance_owner_id(self, host: str) -> str:
        url = f"{host}/api/v1/workspace/profile"
        data = await self.req(url)
        return data["owner"].split("/")[-1]

    async def get_instance_info(self, host: str) -> Instance:
        url = f"{host}/api/v1/workspace/settings/GENERAL"
        data = await self.req(url)
        return Instance(host=host, **data["generalSetting"]["customProfile"])

    async def get_user_info(self, host: str, user_id: str) -> Author:
        url = f"{host}/api/v1/users/{user_id}"
        data = await self.req(url)
        return Author(**data)

    async def get_memo_info(self, host: str, memo_id: str) -> Memo:
        url = f"{host}/api/v1/memos/{memo_id}"
        data = await self.req(url)
        return Memo(**data)
