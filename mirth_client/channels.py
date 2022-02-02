# pylint: disable=cyclic-import
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import UUID

# Override Bandit warnings, since we use this to generate XML, not parse
from xml.etree.ElementTree import Element, SubElement, tostring  # nosec

from semver import VersionInfo

from .exceptions import MirthPostError
from .models import (
    ChannelMessageList,
    ChannelMessageModel,
    ChannelMessageResponseModel,
    ChannelModel,
    ChannelStatistics,
    MirthErrorMessageModel,
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


def raise_post_errors(received: ChannelMessageModel) -> None:
    """Raise errors from Mirth POST response

    Args:
        received (ChannelMessageModel): Mirth POST response message

    Raises:
        MirthPostError: If the Mirth POST response contains an error
    """
    for connector_message in received.connector_messages.values():
        if connector_message.status == "ERROR":
            if connector_message.response and connector_message.response.content:
                error_response_content = MirthErrorMessageModel.parse_raw(
                    connector_message.response.content, content_type="xml"
                )
                error_message = error_response_content.message
            else:
                error_message = f"Error Code {connector_message.error_code}"
            raise MirthPostError(f"Error posting to Mirth: {error_message}")


class Channel:
    """Class corresponding to a Mirth channel"""

    def __init__(self, mirth: "MirthAPI", id_: str) -> None:
        self.mirth: "MirthAPI" = mirth
        self.id = UUID(id_)

        self.post_message_path = f"/channels/{self.id}/messages"
        if self.mirth.version:
            if VersionInfo.parse(self.mirth.version) >= VersionInfo.parse("3.9.0"):
                self.post_message_path = f"/channels/{self.id}/messagesWithObj"

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
        params: Optional[Dict] = None,
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
        messages = ChannelMessageList.parse_raw(response.text, content_type="xml")
        return messages.message

    async def preview_message(
        self, id_: str, params: Optional[Dict] = None
    ) -> Optional[ChannelMessageModel]:
        """Get a minimal representation of a channel message by ID

        Args:
            id_ (str): Message ID
            include_content (bool, optional): Include message content in response. Defaults to True.

        Returns:
            Optional[ChannelMessageModel]: Channel message object
        """
        params = params or {}
        params.update(
            {
                "minMessageId": str(id_),
                "maxMessageId": str(id_),
                "includeContent": False,
                "offset": 0,
                "limit": 1,
            }
        )

        response = await self.mirth.get(f"/channels/{self.id}/messages", params=params)

        if response.text == "<list/>":
            return None
        messages = ChannelMessageList.parse_raw(response.text, content_type="xml")
        if len(messages.message) < 1:
            return None
        return messages.message[0]

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
        if not response.text:
            return None
        return ChannelMessageModel.parse_raw(response.text, content_type="xml")

    async def post_message(
        self, data: Optional[str] = None, raise_errors: bool = True
    ) -> Optional[ChannelMessageModel]:
        """Send a new message to the channel

        Args:
            data (Optional[str], optional): Raw data to send to the channel. Defaults to None.

        Returns:
            int: Sent message ID
        """
        message: str = build_channel_message(data)
        response = await self.mirth.post(
            self.post_message_path,
            content=message,
            content_type="application/xml",
        )

        # In newer versions of Mirth, the API actually tells you the ID of the message you just sent
        # Use this to quickly return the message it received.
        # In older versions, Mirth is as useless as I've come to expect, and doesn't tell you
        # anything about the message you just sent. In this case we return nothing and don't
        # check if the message actually got processed. Sorry!
        if response.text:
            msg_id = ChannelMessageResponseModel.parse_raw(
                response.text, content_type="xml"
            ).long

            received = await self.get_message(str(msg_id), include_content=False)

            # This should never happen, but handle anyway for the sake of MyPy
            if not received:
                raise MirthPostError(
                    "Error posting to Mirth: Sent message is missing from Mirth"
                )

            if raise_errors:
                raise_post_errors(received)

            return received

        return None
