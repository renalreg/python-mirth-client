# pylint: disable=cyclic-import
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID

# Override Bandit warnings, since we use this to generate XML, not parse
from xml.etree.ElementTree import Element, SubElement, tostring  # nosec

import httpx

from .models import (
    ChannelMessageList,
    ChannelMessageModel,
    ChannelModel,
    ChannelStatistics,
)
from .utils import deprecated

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
    """Class corresponding to a Mirth channel"""

    def __init__(self, mirth: "MirthAPI", id_: str) -> None:
        self.mirth: "MirthAPI" = mirth
        self.id = UUID(id_)

    async def get_info(self) -> ChannelModel:
        """Get basic channel metadata from Mirth.

        Returns:
            ChannelModel: Channel metadata
        """
        response = await self.mirth.get(f"/channels/{self.id}")
        return ChannelModel.parse_raw(response.text, content_type="xml")

    async def get_statistics(self) -> ChannelStatistics:
        """Get basic channel statistics from Mirth.

        Includes number of messages that passed, errored etc.

        Returns:
            ChannelStatistics: ChannelStatistics API response
        """
        response = await self.mirth.get(f"/channels/{self.id}/statistics")
        return ChannelStatistics.parse_raw(response.text, content_type="xml")

    async def get_messages(
        self,
        limit: int = 20,
        offset: int = 0,
        include_content: bool = False,
        status: Optional[List[str]] = None,
        params: Optional[Dict[str, Union[List[str], str, int]]] = None,
    ) -> List[ChannelMessageModel]:
        """Get a list of messages handled by the channel

        Args:
            limit (int, optional): Number of events to return. Defaults to 20.
            offset (int, optional): Offset of events list. Defaults to 0.
            include_content (bool, optional): Include message content in response. Defaults to True.
            status (Optional[str], optional): Filter by message status (e.g. ERROR). Defaults to None.

        Returns:
            List[ChannelMessageModel]: List of channel messages
        """
        params = params or {}
        params.update(
            {
                "limit": str(limit),
                "offset": str(offset),
                "includeContent": str(include_content).lower(),
            }
        )

        if status:
            params["status"] = [s.upper() for s in status]

        response = await self.mirth.get(f"/channels/{self.id}/messages", params=params)

        if response.text == "<list/>":
            return []
        messages = ChannelMessageList.parse_raw(
            response.text, content_type="xml", force_list=("message", "entry")
        )
        return messages.message

    async def get_message(
        self, id_: str, include_content: bool = True
    ) -> Optional[ChannelMessageModel]:
        """Get a specific channel message by ID

        Args:
            id_ (str): Message ID
            include_content (bool, optional): Include message content in response. Defaults to True.

        Returns:
            Optional[ChannelMessageModel]: Channel message object
        """
        params = {"includeContent": include_content}
        response = await self.mirth.get(
            f"/channels/{self.id}/messages/{id_}", params=params
        )
        return ChannelMessageModel.parse_raw(response.text, content_type="xml")

    async def post_message(self, data: Optional[str] = None) -> httpx.Response:
        """Send a new message to the channel

        Args:
            data (Optional[str], optional): Raw data to send to the channel. Defaults to None.

        Returns:
            httpx.Response: Mirth API response
        """
        message: str = build_channel_message(data)
        return await self.mirth.post(
            f"/channels/{self.id}/messages",
            data=message,
            content_type="application/xml",
        )

    # Deprecated function aliases
    @deprecated
    async def get(self) -> ChannelModel:  # pylint: disable=missing-function-docstring
        return await self.get_info()
