from typing import Dict, List, Optional

import httpx

from .channels import Channel
from .exceptions import MirthLoginError
from .models import ChannelList, ChannelModel, EventList, EventModel, LoginResponse


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

    async def get_channels(self, name: Optional[str] = None) -> List[Channel]:
        """Get a list of all channels on the Mirth instance. Optionally search
        for a specific channel name.

        Args:
            name (Optional[str], optional): Channel name. Defaults to None.

        Returns:
            List[Channel]: List of Mirth channels
        """
        response = await self.get("/channels")

        channels = ChannelList.parse_raw(
            response.text, content_type="xml", force_list=("channel",)
        )

        channel_objects: List[Channel] = []

        for channel in channels.channel:
            # Create functional Channel objects from response data
            channel_objects.append(
                Channel(
                    self,
                    channel.id,
                    channel.name,
                    channel.description,
                    channel.revision,
                )
            )

        if name:
            channel_objects = [
                channel for channel in channel_objects if channel.name == name
            ]

        return channel_objects

    async def get_channel(self, id_: str) -> Optional[Channel]:
        """Get a specific Mirth channel by its GUID/UUID

        Args:
            id_ (str): Channel GUID/UUID

        Returns:
            Optional[Channel]: Matching channel, if found, else None
        """
        response = await self.get(f"/channels/{id_}")

        channel = ChannelModel.parse_raw(response.text, content_type="xml")

        if not channel:
            return None

        return Channel(
            self,
            channel.id,
            channel.name,
            channel.description,
            channel.revision,
        )

    async def get_events(
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

    async def get_event(self, id_: str) -> Optional[EventModel]:
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
