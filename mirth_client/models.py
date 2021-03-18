import xml
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Set,
    Iterable,
    Type,
    TypeVar,
    Union,
)
from uuid import UUID

import xmltodict
from pydantic import (
    BaseModel,
    Protocol,
    StrBytes,
    ValidationError,
    root_validator,
    validator,
)
from pydantic.error_wrappers import ErrorWrapper

if TYPE_CHECKING:
    Model = TypeVar("Model", bound="BaseModel")
    IntStr = Union[int, str]
    SetIntStr = Set[IntStr]
    DictIntStrAny = Dict[IntStr, Any]


def _to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class MirthBaseModel(BaseModel):
    class Config:
        alias_generator = _to_camel


class XMLBaseModel(MirthBaseModel):
    __root_element__ = ""

    @root_validator(pre=True)
    def strip_xml_root(cls, value):
        if cls.__root_element__ and cls.__root_element__ in value:
            return value[cls.__root_element__]
        return value

    @classmethod
    def parse_raw(
        cls: Type["Model"],
        b: StrBytes,
        *,
        content_type: str = None,
        encoding: str = "utf8",
        proto: Protocol = None,
        allow_pickle: bool = False,
        force_list: Optional[Iterable[str]] = None,
    ) -> "Model":
        try:
            if content_type and content_type.endswith("xml"):
                obj = xmltodict.parse(
                    b,
                    force_list=force_list,
                    encoding="utf-8" if encoding == "utf8" else encoding,
                    dict_constructor=dict,
                )
                return cls.parse_obj(obj)
        except (
            ValueError,
            TypeError,
            UnicodeDecodeError,
            xml.parsers.expat.ExpatError,
        ) as e:
            raise ValidationError([ErrorWrapper(e, loc="__obj__")], cls) from e
        return super().parse_raw(  # type: ignore
            b,
            content_type=content_type,
            encoding=encoding,
            proto=proto,
            allow_pickle=allow_pickle,
        )

    def xml(
        self,
        *,
        include: Union["SetIntStr", "DictIntStrAny"] = None,
        exclude: Union["SetIntStr", "DictIntStrAny"] = None,
        by_alias: bool = True,
        skip_defaults: bool = False,
    ) -> str:
        xml_dict = {
            self.__class__.__root_element__
            or self.__class__.__name__: self.__config__.json_loads(
                self.json(
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                )
            )
        }
        return xmltodict.unparse(xml_dict)


# XML data models


class ChannelModel(XMLBaseModel):
    __root_element__ = "channel"
    id: str
    name: str
    description: Optional[str]
    revision: str


class ChannelList(XMLBaseModel):
    __root_element__ = "list"
    channel: List[ChannelModel]


class LoginResponse(XMLBaseModel):
    __root_element__ = "com.mirth.connect.model.LoginStatus"
    status: str
    message: Optional[str] = None
    updated_username: Optional[str] = None


class EventModel(XMLBaseModel):
    __root_element__ = "event"
    id: int
    level: str
    name: str
    outcome: str
    attributes: Dict
    user_id: Optional[str]
    ip_address: Optional[str]
    date_time: datetime


class EventList(XMLBaseModel):
    __root_element__ = "list"
    event: List[EventModel]


class ChannelStatistics(XMLBaseModel):
    __root_element__ = "channelStatistics"
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


class ConnectorMessageModel(XMLBaseModel):
    __root_element__ = "connectorMessage"
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


class ChannelMessageModel(XMLBaseModel):
    __root_element__ = "message"
    message_id: str
    server_id: UUID
    processed: bool

    connector_messages: List[ConnectorMessageModel]

    @validator("connector_messages", pre=True)
    def strip_connector_messages_roots(cls, value):
        """
        Extract the actual connectorMessage elements from the parsed-XML dictionary.
        The 'connectorMessages' element contains an element 'entry', which contains
        a list of ConnectorMessageModel elements which we actually want.
        """
        return value["entry"]


class ChannelMessageList(XMLBaseModel):
    __root_element__ = "list"
    message: List[ChannelMessageModel]
