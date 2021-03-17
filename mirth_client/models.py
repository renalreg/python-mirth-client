from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


def _to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class MirthBaseModel(BaseModel):
    class Config:
        alias_generator = _to_camel


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
