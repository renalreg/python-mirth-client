import requests
import xmltodict
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
import pydantic
import re


def _to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class MirthBaseModel(pydantic.BaseModel):
    class Config:
        alias_generator = _to_camel


class MirthLoginError(RuntimeError):
    pass


class Event(MirthBaseModel):
    id: int
    level: str
    name: str
    outcome: str
    attributes: Dict
    user_id: Optional[str]
    ip_address: Optional[str]
    date_time: datetime


class ChannelStatistics(MirthBaseModel):
    server_id: UUID
    channel_id: UUID
    received: int
    sent: int
    error: int
    filtered: int
    queued: int


class ConnectorMessageData(MirthBaseModel):
    channel_id: UUID
    content: Optional[str]
    content_type: str
    data_type: str
    encrypted: bool
    message_id: str
    message_data_id: Optional[str]


class ConnectorMessage(MirthBaseModel):
    chain_id: str
    server_id: UUID
    channel_id: str
    channel_name: str
    connector_name: str

    message_id: str
    error_code: str
    send_attempts: int

    raw: Optional[ConnectorMessageData]
    encoded: Optional[ConnectorMessageData]


class ChannelMessage(MirthBaseModel):
    message_id: str
    server_id: UUID
    processed: bool

    connector_messages: List[ConnectorMessage]


def parse_channel_message(xml_dict: Dict):

    message_dict = {
        "messageId": xml_dict.get("messageId"),
        "serverId": xml_dict.get("serverId"),
        "processed": xml_dict.get("processed"),
        "connectorMessages": [
            entry.get("connectorMessage")
            for entry in xml_dict.get("connectorMessages", {}).get("entry", [])
        ],
    }
    return ChannelMessage(**message_dict)


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
        r = self.mirth.get(f"/channels/{self.id}/statistics")
        return ChannelStatistics(**self.mirth.parse(r).get("channelStatistics"))

    def get_messages(
        self, limit: int = 20, offset: int = 0, include_content: bool = True
    ):
        params = {"limit": limit, "offset": offset, "includeContent": include_content}
        r = self.mirth.get(f"/channels/{self.id}/messages", params=params)
        return [
            parse_channel_message(message_dict)
            for message_dict in self.mirth.parse(r).get("list", {}).get("message", [])
        ]

    def get_message(
        self, id_: str, limit: int = 20, offset: int = 0, include_content: bool = True
    ):
        params = {"limit": limit, "offset": offset, "includeContent": include_content}
        r = self.mirth.get(f"/channels/{self.id}/messages/{id_}", params=params)
        return parse_channel_message(self.mirth.parse(r).get("message"))


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
