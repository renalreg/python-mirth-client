from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID
from xml.etree.ElementTree import Element, SubElement, tostring

from .models import (
    ChannelMessageList,
    ChannelMessageModel,
    ChannelStatistics,
)

if TYPE_CHECKING:
    from .mirth import MirthAPI


def build_channel_message(raw_data: Optional[str], binary: bool = False) -> str:
    """
    Builds a valid Mirth Channel message XML string from raw data
    """
    root = Element("com.mirth.connect.donkey.model.message.RawMessage")

    binary_element = SubElement(root, "binary")
    binary_element.text = str(binary).lower()

    if raw_data:
        raw_data_element = SubElement(root, "rawData")
        raw_data_element.text = raw_data

    return tostring(root, encoding="unicode")


class Channel:
    def __init__(
        self,
        mirth: "MirthAPI",
        id: str,
        name: str,
        description: Optional[str],
        revision: str,
    ) -> None:
        self.mirth: "MirthAPI" = mirth
        self.id = UUID(id)
        self.name = name
        self.description = description
        self.revision = revision

    async def get_statistics(self):
        r = await self.mirth.get(f"/channels/{self.id}/statistics")
        return ChannelStatistics.parse_raw(r.text, content_type="xml")

    async def get_messages(
        self,
        limit: int = 20,
        offset: int = 0,
        include_content: bool = True,
        status: Optional[str] = None,
    ) -> List[ChannelMessageModel]:
        params: Dict[str, str] = {
            "limit": str(limit),
            "offset": str(offset),
            "includeContent": str(include_content).lower(),
        }

        if status:
            params["status"] = status.upper()

        r = await self.mirth.get(f"/channels/{self.id}/messages", params=params)

        messages = ChannelMessageList.parse_raw(
            r.text, content_type="xml", force_list=("message", "entry")
        )
        return messages.message

    async def get_message(self, id_: str, include_content: bool = True):
        params = {"includeContent": include_content}
        r = await self.mirth.get(f"/channels/{self.id}/messages/{id_}", params=params)
        return ChannelMessageModel.parse_raw(r.text, content_type="xml")

    async def post_message(self, data: Optional[str] = None):
        message: str = build_channel_message(data)
        return await self.mirth.post(
            f"/channels/{self.id}/messages",
            data=message,
            content_type="application/xml",
        )
