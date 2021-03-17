from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID
from xml.etree.ElementTree import Element, SubElement, tostring

from .models import ChannelMessage, ChannelStatistics

if TYPE_CHECKING:
    from .mirth import MirthAPI


def parse_channel_message(xml_dict: Dict):
    """
    Constructs a ChannelMessage object from a dictionary representation of Mirth Channel message XML
    """
    connector_messages: Union[List, Dict] = xml_dict.get("connectorMessages", {}).get(
        "entry", []
    )

    message_dict = {
        "messageId": xml_dict.get("messageId"),
        "serverId": xml_dict.get("serverId"),
        "processed": xml_dict.get("processed"),
    }

    if connector_messages and isinstance(connector_messages, list):
        message_dict["connectorMessages"] = [
            entry.get("connectorMessage") for entry in connector_messages
        ]
    elif connector_messages and isinstance(connector_messages, dict):
        message_dict["connectorMessages"] = [connector_messages.get("connectorMessage")]
    else:
        message_dict["connectorMessages"] = []

    return ChannelMessage(**message_dict)


def build_channel_message(raw_data: Optional[str], binary: bool = False) -> str:
    """
    Builds a valid Mirth Channel message XML string from raw data
    """
    root = Element("com.mirth.connect.donkey.model.message.RawMessage")

    binary_element = SubElement(root, "binary")
    binary_element.text = binary

    if raw_data:
        raw_data_element = SubElement(root, "rawData")
        raw_data_element.text = raw_data

    return tostring(root, encoding="unicode")


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
        self,
        limit: int = 20,
        offset: int = 0,
        include_content: bool = True,
        status: Optional[str] = None,
    ):
        params = {"limit": limit, "offset": offset, "includeContent": include_content}

        if status:
            params["status"] = status.upper()

        r = self.mirth.get(f"/channels/{self.id}/messages", params=params)
        messages: Union[List, Dict] = (
            self.mirth.parse(r).get("list", {}).get("message", [])
        )

        # XML parser returns a list ONLY if more than 1 message is present
        # otherwise it just returns the message itself. We have to account for this.
        if messages and isinstance(messages, list):
            return [parse_channel_message(message_dict) for message_dict in messages]
        if messages and isinstance(messages, dict):
            return [parse_channel_message(messages)]
        return []

    def get_message(self, id_: str, include_content: bool = True):
        params = {"includeContent": include_content}
        r = self.mirth.get(f"/channels/{self.id}/messages/{id_}", params=params)
        return parse_channel_message(self.mirth.parse(r).get("message"))

    def post_message(self, data: Optional[str] = None):
        message: str = build_channel_message(data)
        return self.mirth.post(
            f"/channels/{self.id}/messages",
            data=message,
            content_type="application/xml",
        )
