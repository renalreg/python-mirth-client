from typing import Dict, List, Optional

import requests
import xmltodict

from .channels import Channel
from .exceptions import MirthLoginError
from .models import Event


class MirthAPI:
    def __init__(self, url: str, verify_ssl: bool = True) -> None:
        self.base = url.rstrip("/")
        self.verify_ssl = verify_ssl

        self._dict_constructor = dict
        self.session = requests.session()

    def parse(self, response: requests.Response, **kwargs) -> Dict:
        kwargs.setdefault("dict_constructor", self._dict_constructor)
        if response.text:
            parsed = xmltodict.parse(response.text, **kwargs) or {}
            return parsed
        return {}

    def post(
        self, url: str, content_type: Optional[str] = None, **kwargs
    ) -> requests.Response:
        path: str = self.base + url
        kwargs.setdefault("verify", self.verify_ssl)

        if content_type:
            if not "headers" in kwargs:
                kwargs["headers"] = {"Content-Type": content_type}
            else:
                kwargs["headers"].setdefault("Content-Type", content_type)

        return self.session.post(path, **kwargs)

    def get(self, url: str, **kwargs) -> requests.Response:
        path: str = self.base + url
        kwargs.setdefault("verify", self.verify_ssl)
        return self.session.get(path, **kwargs)

    def login(self, user: str, password: str):
        r = self.post("/users/_login", data={"username": user, "password": password})
        response: Dict[str, str] = self.parse(r).get(
            "com.mirth.connect.model.LoginStatus"
        )
        if response and response.get("status") == "SUCCESS":
            return response
        else:
            raise MirthLoginError("Unable to log in")

    def get_channels(self, name: Optional[str] = None) -> List[Channel]:
        r = self.get("/channels")

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

    def get_channel(self, id_: str):
        r = self.get("/channels", params={"channelId": id_})
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

    def get_events(
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

        r = self.get("/events", params=params)
        response = (self.parse(r, force_list=("event",)).get("list", {}) or {}).get(
            "event", []
        )
        return [Event(**event) for event in response]
