from datetime import datetime

import mistune
from pydantic import BaseModel

m = mistune.create_markdown(escape=False, plugins=["url", "strikethrough", "footnotes", "table", "speedup"])


class Instance(BaseModel):
    host: str
    title: str
    description: str
    logoUrl: str


class Author(BaseModel):
    name: str
    username: str
    nickname: str
    avatarUrl: str
    description: str

    @property
    def url(self) -> str:
        return f"/u/{self.username}"

    @property
    def user_id(self) -> str:
        return self.name.split("/")[-1]


class Memo(BaseModel):
    name: str
    creator: str

    createTime: datetime
    updateTime: datetime
    displayTime: datetime

    content: str
    tags: list[str]
    snippet: str

    @property
    def html(self) -> str:
        return m(self.content)

    @property
    def memo_id(self) -> str:
        return self.name.split("/")[-1]

    @property
    def creator_id(self) -> str:
        return self.creator.split("/")[-1]
