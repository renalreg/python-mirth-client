import requests
import xmltodict
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
import pydantic


class MirthLoginError(RuntimeError):
    pass


class Event(pydantic.BaseModel):
    id: int
    level: str
    name: str
    outcome: str
    attributes: Dict
    userId: Optional[str] = pydantic.Field(None, alias="user_id")
    ipAddress: Optional[str] = pydantic.Field(None, alias="ip_address")
    dateTime: datetime


class Channel:
    def __init__(
        self, mirth: "MirthAPI", id: str, name: str, description: str, revision: int
    ) -> None:
        self.mirth: "MirthAPI" = mirth
        self.id = UUID(id)
        self.name = name
        self.description = description
        self.revision = revision

    def get_statistics(self):
        path: str = f"/channels/{self.id}/statistics"
        r = self.mirth.get(path)
        return self.mirth.parse(r).get("channelStatistics")


class MirthAPI:
    def __init__(self, url: str, verify_ssl: bool = True) -> None:
        self.base = url.rstrip("/")
        self.verify_ssl = verify_ssl

        self._dict_constructor = dict
        self.session = requests.session()

    def parse(self, response: requests.Response, **kwargs) -> Dict:
        kwargs.setdefault("dict_constructor", self._dict_constructor)
        if response.text:
            return xmltodict.parse(response.text, **kwargs) or {}
        return {}

    def post(self, url: str, **kwargs) -> requests.Response:
        path: str = self.base + url
        kwargs.setdefault("verify", self.verify_ssl)
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

    def get_channels(self, channel_id: Optional[str] = None) -> List[Channel]:
        if channel_id:
            r = self.get("/channels", params={"channelId": channel_id})
        else:
            r = self.get("/channels")

        channel_objects: List[Channel] = []
        channel_dicts = self.parse(r)["list"]["channel"]
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
        return channel_objects

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
        response = (self.parse(r).get("list", {}) or {}).get("event", [])
        return [Event(**event) for event in response]
