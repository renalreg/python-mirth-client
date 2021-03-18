import logging
from typing import Dict, List, Optional

import httpx
import xmltodict

from .channels import Channel
from .exceptions import MirthLoginError
from .models import (
    ChannelList,
    ChannelModel,
    LoginResponse,
    EventList,
    EventModel,
)


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

        login_status = LoginResponse.parse_raw(r.text, content_type="xml")
        if login_status and login_status.status == "SUCCESS":
            return login_status
        else:
            raise MirthLoginError("Unable to log in")

    async def get_channels(self, name: Optional[str] = None) -> List[Channel]:
        r = await self.get("/channels")

        channels = ChannelList.parse_raw(
            r.text, content_type="xml", force_list=("channel",)
        )

        channel_objects: List[Channel] = []

        for channel in channels.channel:
            # Create functional Channel objects from response data
            channel_objects.append(
                Channel(
                    self,
                    channel.id,
                    channel.name,
                    channel.description,
                    channel.revision,
                )
            )

        if name:
            channel_objects = [
                channel for channel in channel_objects if channel.name == name
            ]

        return channel_objects

    async def get_channel(self, id_: str):
        r = await self.get(f"/channels/{id_}")

        channel = ChannelModel.parse_raw(r.text, content_type="xml")

        return Channel(
            self,
            channel.id,
            channel.name,
            channel.description,
            channel.revision,
        )

    async def get_events(
        self,
        limit: int = 20,
        offset: int = 0,
        level: Optional[str] = None,
        outcome: Optional[str] = None,
    ):
        params: Dict[str, str] = {"limit": str(limit), "offset": str(offset)}

        if level:
            params["level"] = level
        if outcome and outcome in ("SUCCESS", "FAILURE"):
            params["outcome"] = outcome

        r = await self.get("/events", params=params)

        events = EventList.parse_raw(r.text, content_type="xml", force_list=("event",))

        return events.event

    async def get_event(self, id_: str):

        r = await self.get(f"/events/{id_}")
        event = EventModel.parse_raw(r.text, content_type="xml")

        return event
