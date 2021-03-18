from typing import Dict, List, Optional

import httpx
import xmltodict

from .channels import Channel
from .exceptions import MirthLoginError
from .models import Event


class MirthAPI:
    def __init__(self, url: str, verify_ssl: bool = True) -> None:
        self.base = url.rstrip("/")

        self._dict_constructor = dict
        self.session = httpx.AsyncClient(verify=verify_ssl)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def close(self):
        await self.session.aclose()

    def parse(self, response: httpx.Response, **kwargs) -> Dict:
        kwargs.setdefault("dict_constructor", self._dict_constructor)
        if response.text:
            parsed = xmltodict.parse(response.text, **kwargs) or {}
            return parsed
        return {}

    async def post(
        self, url: str, content_type: Optional[str] = None, **kwargs
    ) -> httpx.Response:
        path: str = self.base + url

        if content_type:
            if not "headers" in kwargs:
                kwargs["headers"] = {"Content-Type": content_type}
            else:
                kwargs["headers"].setdefault("Content-Type", content_type)

        return await self.session.post(path, **kwargs)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        path: str = self.base + url
        return await self.session.get(path, **kwargs)

    async def login(self, user: str, password: str):
        r = await self.post(
            "/users/_login", data={"username": user, "password": password}
        )
        response: Dict[str, str] = self.parse(r).get(
            "com.mirth.connect.model.LoginStatus"
        )
        if response and response.get("status") == "SUCCESS":
            return response
        else:
            raise MirthLoginError("Unable to log in")

    async def get_channels(self, name: Optional[str] = None) -> List[Channel]:
        r = await self.get("/channels")

        channel_objects: List[Channel] = []
        channel_dicts = self.parse(r, force_list=("channel",))["list"]["channel"]
        for channel in channel_dicts:
            channel_objects.append(
                Channel(
                    self,
                    channel.get("id"),
                    channel.get("name"),
                    channel.get("description"),
                    channel.get("revision"),
                )
            )

        if name:
            channel_objects = [
                channel for channel in channel_objects if channel.name == name
            ]

        return channel_objects

    async def get_channel(self, id_: str):
        r = await self.get("/channels", params={"channelId": id_})
        channel = self.parse(r)["list"]["channel"]
        if not channel:
            return None
        return Channel(
            self,
            channel.get("id"),
            channel.get("name"),
            channel.get("description"),
            channel.get("revision"),
        )

    async def get_events(
        self,
        limit: int = 20,
        offset: int = 0,
        level: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> List[Event]:
        params = {"limit": limit, "offset": offset}

        if level:
            params["level"] = level
        if outcome and outcome in ("SUCCESS", "FAILURE"):
            params["outcome"] = outcome

        r = await self.get("/events", params=params)
        response = (self.parse(r, force_list=("event",)).get("list", {}) or {}).get(
            "event", []
        )
        return [Event(**event) for event in response]
