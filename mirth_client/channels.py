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


from pprint import pprint


class Channel:
    def __init__(
        self, mirth: "MirthAPI", id: str, name: str, description: str, revision: int
    ) -> None:
        self.mirth: "MirthAPI" = mirth
        self.id = UUID(id)
        self.name = name
        self.description = description
        self.revision = revision

    async def get_statistics(self):
        r = await self.mirth.get(f"/channels/{self.id}/statistics")
        return ChannelStatistics(**self.mirth.parse(r).get("channelStatistics"))

    async def get_messages(
        self,
        limit: int = 20,
        offset: int = 0,
        include_content: bool = True,
        status: Optional[str] = None,
    ):
        params = {"limit": limit, "offset": offset, "includeContent": include_content}

        if status:
            params["status"] = status.upper()

        r = await self.mirth.get(f"/channels/{self.id}/messages", params=params)

        # Convert XML to Python dictionary
        # Force message and entry items to appear as a list
        parsed = self.mirth.parse(r, force_list=("message", "entry"))

        messages: Union[List, Dict] = parsed.get("list", {}).get("message", [])
        return [parse_channel_message(message_dict) for message_dict in messages]

    async def get_message(self, id_: str, include_content: bool = True):
        params = {"includeContent": include_content}
        r = await self.mirth.get(f"/channels/{self.id}/messages/{id_}", params=params)
        return parse_channel_message(self.mirth.parse(r).get("message"))

    async def post_message(self, data: Optional[str] = None):
        message: str = build_channel_message(data)
        return await self.mirth.post(
            f"/channels/{self.id}/messages",
            data=message,
            content_type="application/xml",
        )
