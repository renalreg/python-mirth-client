"""
Pydantic models for parsing Mirth XML responses
and converting returned data into Python objects
"""

import xml
from datetime import datetime
from typing import (
    OrderedDict,
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


class ChannelModel(XMLBaseModel):
    """Mirth API Channel object"""

    __root_element__ = "channel"
    id: str
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


class ConnectorMessageData(MirthBaseModel):
    """Object mapping for connectorMessage `raw` or `parsed` data"""

    channel_id: UUID
    content: Optional[str]
    content_type: str
    data_type: Optional[str]
    encrypted: bool
    message_id: str
    message_data_id: Optional[str]


def _xml_map_item_to_dict(in_dict: Dict[str, Any]):
    if not isinstance(in_dict, OrderedDict):
        raise TypeError("XML map must be passed as an OrderedDict")
    if not "string" in in_dict.keys():
        raise ValueError("XML map requires at least one string key")

    # XML map parsing only works if we have one or two XML keys.
    # One key means both actual key and value are the same type (string)
    # Two keys means actual key and value are different types.
    # Actual key must always be string, actual value can be anything,
    # but we'll be turning it into a string since we're just grabbing XML text
    if len(in_dict.keys()) not in (1, 2):
        raise ValueError("XML map can only contain a maximum of 2 keys")

    # If we have one key, both key and value are strings
    if len(in_dict.keys()) == 1:
        # In this case, we NEED a second value under the "string" key,
        # corresponding to the actual value
        if len(in_dict["string"]) != 2:
            raise ValueError("XML map expected two items exactly under the string key")
        actual_key = in_dict["string"][0]
        actual_val = in_dict["string"][1]

    # The only other option is having two XML keys.
    # In this case, the string key describes the actual map key,
    # and the other key describes the type of it's corresponding value.
    # We don't care about the XML value type, so we just want to extract
    # the map key, and whatever the actual value is.
    else:
        if not isinstance(in_dict["string"], str):
            # In this case our string XML key MUST contain a single string
            # which corresponds to the actual key we want to return
            raise ValueError("XML map string key must contain a single string value")
        values: List[str] = list(in_dict.values())
        actual_key = values[0]
        actual_val = values[1]

    out = {actual_key: actual_val}
    return out


def _xml_map_to_dict(in_data: Union[Dict[str, Any], List[Dict[str, Any]]]):
    out: Dict[str, str] = {}
    # If a list of items is passed in, then we want to merge
    # them into a single dictionary. The xmltodict module will
    # create lists where we want a map, so we just manually handle
    # this conversion here.
    if isinstance(in_data, (list, tuple)):
        for item in in_data:
            out.update(_xml_map_item_to_dict(item))
        return out
    return _xml_map_item_to_dict(in_data)


class MetaDataMap(Dict):
    """Custom field class for a Mirth API MetaDataMap object"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Convert xmltodict output into a tidy Python dictionary"""
        return _xml_map_to_dict(value)


class ConnectorMessageModel(XMLBaseModel):
    """Mirth API connectorMessage object"""

    __root_element__ = "connectorMessage"
    chain_id: int
    order_id: int
    server_id: UUID
    channel_id: str

    channel_name: str
    connector_name: str

    message_id: str
    error_code: int
    send_attempts: int

    raw: Optional[ConnectorMessageData]
    encoded: Optional[ConnectorMessageData]
    sent: Optional[ConnectorMessageData]
    response: Optional[ConnectorMessageData]

    meta_data_map: MetaDataMap

    @validator("meta_data_map", pre=True)
    def strip_metadatamap_entry_roots(cls, value):  # pylint: disable=no-self-use
        """
        Extract the actual metaDataMap elements from the parsed-XML dictionary.
        The 'metaDataMap' element contains an element 'entry', which contains
        a list of map elements which we actually want.
        """
        if "entry" in value:
            return value["entry"]
        return value


class ChannelMessageModel(XMLBaseModel):
    """Mirth API Message object"""

    __root_element__ = "message"
    message_id: int
    server_id: UUID
    channel_id: UUID
    processed: bool

    connector_messages: List[ConnectorMessageModel]

    @validator("connector_messages", pre=True)
    def strip_connector_messages_roots(cls, value):  # pylint: disable=no-self-use
        """
        Extract the actual connectorMessage elements from the parsed-XML dictionary.
        The 'connectorMessages' element contains an element 'entry', which contains
        a list of ConnectorMessageModel elements which we actually want.
        """
        if "entry" in value:
            return value["entry"]
        return value


class ChannelMessageList(XMLBaseModel):
    """List of Mirth API Message objects within a list object"""

    __root_element__ = "list"
    message: List[ChannelMessageModel]
