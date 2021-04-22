import warnings
from typing import Dict, List, Optional, Union
from uuid import UUID

import httpx

from .channels import Channel
from .exceptions import MirthLoginError
from .models import (
    ChannelGroup,
    ChannelList,
    ChannelModel,
    ChannelStatistics,
    ChannelStatisticsList,
    EventList,
    EventModel,
    GroupList,
    LoginResponse,
)
from .utils import deprecated


class MirthAPI:
    """Class corresponding to a Mirth web API connection"""

    def __init__(self, url: str, verify_ssl: bool = True) -> None:
        self.base = url.rstrip("/")

        self._dict_constructor = dict
        self.session = httpx.AsyncClient(verify=verify_ssl)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

    async def close(self):
        """Close the API connection session"""
        await self.session.aclose()

    async def post(
        self, url: str, content_type: Optional[str] = None, **kwargs
    ) -> httpx.Response:
        """Send a POST request to the API instance

        Args:
            url (str): Relative URL to the resource
            content_type (Optional[str], optional): Request content type. Defaults to None.

        Returns:
            httpx.Response: API response
        """
        path: str = self.base + url

        if content_type:
            if "headers" not in kwargs:
                kwargs["headers"] = {"Content-Type": content_type}
            else:
                kwargs["headers"].setdefault("Content-Type", content_type)

        return await self.session.post(path, **kwargs)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Send a GET request to the API instance

        Args:
            url (str): Relative URL to the resource

        Returns:
            httpx.Response: API response
        """
        path: str = self.base + url
        return await self.session.get(path, **kwargs)

    async def login(self, user: str, password: str):
        """Log in to the Mirth instance

        Args:
            user (str): Mirth username
            password (str): Mirth password

        Raises:
            MirthLoginError: Unable to login due to bad connection or incorrect credentials

        Returns:
            LoginResponse: API login response
        """
        response = await self.post(
            "/users/_login", data={"username": user, "password": password}
        )

        login_status = LoginResponse.parse_raw(response.text, content_type="xml")
        if login_status and login_status.status == "SUCCESS":
            return login_status
        raise MirthLoginError("Unable to log in")

    async def channel_info(self) -> List[ChannelModel]:
        """Get a list of all channel metadata on the Mirth instance.

        Returns:
            List[Channel]: List of Mirth channels
        """
        response = await self.get("/channels")

        channels = ChannelList.parse_raw(
            response.text, content_type="xml", force_list=("channel",)
        )

        return channels.channel

    async def statistics(self) -> List[ChannelStatistics]:
        """Get a list of all channel statistics on the Mirth instance.

        Returns:
            List[Channel]: List of Mirth channel statistics
        """
        response = await self.get("/channels/statistics")

        statistics = ChannelStatisticsList.parse_raw(response.text, content_type="xml")
        return statistics.channel_statistics

    async def channels(self) -> List[Channel]:
        """Get a list of interactive Channel objects on the Mirth instance.

        Returns:
            List[Channel]: Channel objects
        """
        channel_infos = await self.channel_info()
        return [self.channel(channel.id) for channel in channel_infos]

    async def groups(self) -> List[ChannelGroup]:
        """Get a list of Channel groups on the Mirth instance.
        Includes IDs of channels within each group.

        Returns:
            List[ChannelGroup]: List of channel groups
        """
        response = await self.get("/channelgroups")

        groups = GroupList.parse_raw(
            response.text, content_type="xml", force_list=("channelGroup",)
        )
        return groups.channel_group

    def channel(self, id_: Union[str, UUID]) -> Channel:
        """Return an interactive Channel object

        Args:
            id_ (str, UUID): Channel GUID/UUID

        Returns:
            Channel: Channel object
        """
        return Channel(self, str(id_))

    async def events(
        self,
        limit: int = 20,
        offset: int = 0,
        level: Optional[str] = None,
        outcome: Optional[str] = None,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> List[EventModel]:
        """Get a paged list of all events on the Mirth instance.

        Args:
            limit (int, optional): Number of events to return. Defaults to 20.
            offset (int, optional): Offset of events list. Defaults to 0.
            level (Optional[str]): Mirth event LEVEL to filter by. Defaults to None.
            outcome (Optional[str]): Searches on whether the event outcome was successful or not. Defaults to None.
            user_id (Optional[int]): The user ID to query events by. Defaults to None.
            name (Optional[str]): Searches the event name for this string. Defaults to None.

        Returns:
            List[EventModel]: List of Mirth events
        """
        params: Dict[str, str] = {"limit": str(limit), "offset": str(offset)}

        if level:
            params["level"] = level
        if outcome and outcome in ("SUCCESS", "FAILURE"):
            params["outcome"] = outcome
        if user_id is not None:
            params["userId"] = str(user_id)
        if name:
            params["name"] = name

        response = await self.get("/events", params=params)

        events = EventList.parse_raw(
            response.text, content_type="xml", force_list=("event",)
        )

        return events.event

    async def event(self, id_: str) -> Optional[EventModel]:
        """Get a specific Mirth event by ID

        Args:
            id_ (str): Event ID

        Returns:
            Optional[EventModel]: Mirth Event object
        """
        response = await self.get(f"/events/{id_}")
        event = EventModel.parse_raw(response.text, content_type="xml")

        if not event:
            return None

        return event

    # Deprecated function aliases

    @deprecated
    async def get_channels(  # pylint: disable=missing-function-docstring
        self, name: Optional[str] = None
    ) -> List[ChannelModel]:
        if name:
            warnings.warn(
                "Argument 'name' is deprecated and has no effect on get_channels",
                DeprecationWarning,
                stacklevel=2,
            )
        return await self.channel_info()

    @deprecated
    async def get_channel(  # pylint: disable=missing-function-docstring
        self, id_: str
    ) -> ChannelModel:
        response = await self.get(f"/channels/{id_}")
        return ChannelModel.parse_raw(response.text, content_type="xml")

    @deprecated
    async def get_events(  # pylint: disable=missing-function-docstring
        self,
        limit: int = 20,
        offset: int = 0,
        level: Optional[str] = None,
        outcome: Optional[str] = None,
        user_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> List[EventModel]:
        return await self.events(limit, offset, level, outcome, user_id, name)

    @deprecated
    async def get_event(  # pylint: disable=missing-function-docstring
        self, id_: str
    ) -> Optional[EventModel]:
        return await self.event(id_)
