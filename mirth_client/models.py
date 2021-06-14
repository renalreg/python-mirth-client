"""
Pydantic models for parsing Mirth XML responses
and converting returned data into Python objects
"""

import xml
from collections import OrderedDict
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
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
from typing_extensions import TypedDict

if TYPE_CHECKING:
    Model = TypeVar("Model", bound="BaseModel")
    IntStr = Union[int, str]
    SetIntStr = Set[IntStr]
    DictIntStrAny = Dict[IntStr, Any]


def _to_camel(snake_str: str) -> str:
    """Convert a string from snake_case to JSON-style camelCase

    Args:
        snake_str (str): Input string

    Returns:
        str: Camel case formatted string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class MirthBaseModel(BaseModel):
    """
    Base model which defaults to creating camelCase aliases for all fields
    """

    class Config:
        """Pydantic config class to set alias generator"""

        alias_generator = _to_camel


class XMLDict(OrderedDict):
    """Custom class used to differentiate general OrderedDict
    from dictionaries coming directly from xmltodict.

    Functionally, this is just an alias of OrderedDict
    """


class XMLBaseModel(MirthBaseModel):
    """
    Base model for parsing and serialising to XML data.
    Defaults to creating camelCase aliases, and additionally supports
    parsing and generating XML strings.
    """

    __root_element__ = ""

    @root_validator(pre=True)
    def strip_xml_root(cls, value):
        """Strips out the root key of a parsed XML message,
        if one is defined on the model.

        E.g. an XML document <request><contents>Message</contents></message>
        could have the root key `message`. When parsed to a dictionary,
        we want to strip the top level `requests` key and be left with
        `{"contents": "Message"}`, so we define `__root_element__ = "request"`.
        This validator then checks if the parsed dictionary contains this key,
        and passes only the child data to the next stage of validation.

        Args:
            value (dict): Input dictionary

        Returns:
            dict: Dictionary without root key
        """
        if cls.__root_element__ and cls.__root_element__ in value:
            return value[cls.__root_element__]
        return value

    @classmethod
    def parse_raw(  # pylint: disable=arguments-differ
        cls: Type["Model"],
        b: StrBytes,
        *,
        content_type: str = None,
        encoding: str = "utf8",
        proto: Protocol = None,
        allow_pickle: bool = False,
        force_list: Optional[Iterable[str]] = None,
    ) -> "Model":
        """Parse raw data into a Pydantic object.

        By passing `content_type="xml"` to `XMLBaseModel.parse_raw` with an
        XML formatted input string, the XML is parsed to a dictionary object
        and send for validation by the Pydantic model.

        Raises:
            ValidationError: Invalid XML or XML can not be validated against the model

        Returns:
            XMLBaseModel: Pydantic object from the parsed data
        """
        try:
            if content_type and content_type.endswith("xml"):
                obj = xmltodict.parse(
                    b,
                    force_list=force_list,
                    encoding="utf-8" if encoding == "utf8" else encoding,
                    dict_constructor=XMLDict,
                )
                return cls.parse_obj(obj)
        except (
            ValueError,
            TypeError,
            UnicodeDecodeError,
            xml.parsers.expat.ExpatError,  # pylint: disable=no-member
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
        exclude_unset: bool = False,
    ) -> str:
        """Convert the Pydantic object into an XML string"""
        xml_dict = {
            self.__class__.__root_element__
            or self.__class__.__name__: self.__config__.json_loads(
                self.json(
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                )
            )
        }
        return xmltodict.unparse(xml_dict)


# XML data models

_RawHashMapTypes = Union["OrderedDict[Any, Any]", List["OrderedDict[Any, Any]"]]


class _MirthDateTimeMap(TypedDict):
    time: Optional[int]
    timezone: Optional[str]


class MirthDatetime(datetime):
    """
    Model and validator to convert a Mirth XML timestamp object
    into a Python datetime.datetime instance
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: _MirthDateTimeMap):
        """Extract timestamp and convert to a datetime"""
        if not isinstance(value, cls):
            timestamp = value.get("time")
            if not timestamp:
                raise ValueError("No `time` attribute found in input")
            return cls.fromtimestamp(int(timestamp) / 1000)
        return value


class GroupChannel(XMLBaseModel):
    """Minimal Mirth API Channel description, used in Groups"""

    id: UUID
    revision: str


class ChannelGroup(XMLBaseModel):
    """Mirth API ChannelGroup object"""

    __root_element__ = "channelGroup"
    id: UUID
    name: str
    description: Optional[str]
    revision: str

    channels: List[GroupChannel]

    @validator("channels", pre=True)
    def strip_channels_roots(cls, value):  # pylint: disable=no-self-use
        """
        Extract the actual GroupChannel elements from the parsed-XML dictionary.
        The 'GroupChannel' element contains an element 'channel', which contains
        a list of GroupChannel elements which we actually want.
        """
        if "channel" in value:
            return value["channel"]
        return value


class GroupList(XMLBaseModel):
    """List of Mirth API Channel groups within a list object"""

    __root_element__ = "list"
    channel_group: List[ChannelGroup]


class ChannelModel(XMLBaseModel):
    """Mirth API Channel object"""

    __root_element__ = "channel"
    id: UUID
    name: str
    description: Optional[str]
    revision: str


class ChannelList(XMLBaseModel):
    """List of Mirth API Channel objects within a list object"""

    __root_element__ = "list"
    channel: List[ChannelModel]


class LoginResponse(XMLBaseModel):
    """Mirth API `com.mirth.connect.model.LoginStatus` response object"""

    __root_element__ = "com.mirth.connect.model.LoginStatus"
    status: str
    message: Optional[str] = None
    updated_username: Optional[str] = None


class EventModel(XMLBaseModel):
    """Mirth API Event object"""

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
    """List of Mirth API Event objects within a list object"""

    __root_element__ = "list"
    event: List[EventModel]


class ChannelStatistics(XMLBaseModel):
    """Mirth API channelStatistics object"""

    __root_element__ = "channelStatistics"
    server_id: UUID
    channel_id: UUID
    received: int
    sent: int
    error: int
    filtered: int
    queued: int


class ChannelStatisticsList(XMLBaseModel):
    """List of Mirth API channel statistics objects within a list object"""

    __root_element__ = "list"
    channel_statistics: List[ChannelStatistics]


class ConnectorMessageData(MirthBaseModel):
    """Object mapping for connectorMessage `raw` or `parsed` data"""

    channel_id: UUID
    content: Optional[str]
    content_type: str
    data_type: Optional[str]
    encrypted: bool
    message_id: str
    message_data_id: Optional[str]


def _xml_map_item_to_dict(in_dict: "OrderedDict[Any, Any]"):
    if not isinstance(in_dict, OrderedDict):
        raise TypeError(
            f"XML map must be passed as an OrderedDict. Instead got {type(in_dict)}"
        )

    # XML map parsing only works if we have one or two XML keys.
    # One key means both actual key and value are the same type (string)
    # Two keys means actual key and value are different types.
    # Actual key must always be string, actual value can be anything,
    # but we'll be turning it into a string since we're just grabbing XML text
    if len(in_dict.keys()) not in (0, 1, 2):
        raise ValueError("XML map can only contain a maximum of 2 keys")

    if len(in_dict.keys()) == 0:
        return {}
    # If we have one key, both key and value are the same type
    if len(in_dict.keys()) == 1:
        # In this case, we NEED a second value under the first key,
        # corresponding to the actual value
        values = list(in_dict.values())[0]
        if len(values) != 2:
            raise ValueError("XML map expected two items exactly under the string key")
        actual_key = values[0]
        actual_val = values[1]

    # The only other option is having two XML keys.
    # In this case, the string key describes the actual map key,
    # and the other key describes the type of it's corresponding value.
    # We don't care about the XML value type, so we just want to extract
    # the map key, and whatever the actual value is.
    else:
        values = list(in_dict.values())
        actual_key = values[0]
        actual_val = values[1]

    out = {actual_key: actual_val}
    return out


def _xml_map_to_dict(in_data: _RawHashMapTypes):
    out: Dict[Any, Any] = {}
    # If a list of items is passed in, then we want to merge
    # them into a single dictionary. The xmltodict module will
    # create lists where we want a map, so we just manually handle
    # this conversion here.
    if isinstance(in_data, (list, tuple)):
        for item in in_data:
            out.update(_xml_map_item_to_dict(item))
        return out
    return _xml_map_item_to_dict(in_data)


def convert_hashmap(value: Optional[Dict]) -> Dict:
    """Convert a Mirth XML HashMap object into a Python dictionary

    Args:
        value (Optional[Dict]): Converted Mirth XML hashmap

    Returns:
        Dict[Any, Any]: Python dictionary
    """
    if not value:
        return {}
    if "entry" in value and isinstance(value["entry"], (OrderedDict, list)):
        return _xml_map_to_dict(value["entry"])
    return value


class ConnectorMessageModel(XMLBaseModel):
    """Mirth API connectorMessage object"""

    __root_element__ = "connectorMessage"
    chain_id: int
    order_id: int
    server_id: UUID
    channel_id: str

    status: Optional[str]

    received_date: MirthDatetime

    channel_name: str
    connector_name: str

    message_id: str
    error_code: int
    send_attempts: int

    raw: Optional[ConnectorMessageData]
    encoded: Optional[ConnectorMessageData]
    sent: Optional[ConnectorMessageData]
    response: Optional[ConnectorMessageData]

    meta_data_id: int
    meta_data_map: Dict[str, Optional[str]]

    @validator("meta_data_map", pre=True)
    def convert_hashmap(cls, value):  # pylint: disable=no-self-use
        """Convert the XML hashmap into a Python dictionary"""
        return convert_hashmap(value)


class ChannelMessageModel(XMLBaseModel):
    """Mirth API Message object"""

    __root_element__ = "message"
    message_id: int
    server_id: UUID
    channel_id: UUID
    processed: bool

    received_date: MirthDatetime

    connector_messages: Dict[int, ConnectorMessageModel]

    @validator("connector_messages", pre=True)
    def convert_hashmap(cls, value):  # pylint: disable=no-self-use
        """Convert the XML hashmap into a Python dictionary"""
        return convert_hashmap(value)


class ChannelMessageList(XMLBaseModel):
    """List of Mirth API Message objects within a list object"""

    __root_element__ = "list"
    message: List[ChannelMessageModel]
