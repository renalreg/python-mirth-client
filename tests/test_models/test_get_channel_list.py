from pathlib import Path
from uuid import UUID
from mirth_client.models import ChannelList

CHANNEL_LIST_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-channelList.xml")
    .read_text()
)

CHANNEL_LIST_RESPONSE_MULTIPLE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-channelList.multiple.xml")
    .read_text()
)


def test_xml_to_obj():
    response = ChannelList.parse_raw(CHANNEL_LIST_RESPONSE)
    assert response == {
        "channel": [
            {
                "id": UUID("493d666a-1242-46a2-8425-b061e215884c"),
                "name": "Channel 1",
                "description": "Example description.",
                "revision": "0",
            }
        ]
    }


def test_xml_to_obj_multiple():
    response = ChannelList.parse_raw(CHANNEL_LIST_RESPONSE_MULTIPLE)
    assert response == {
        "channel": [
            {
                "id": UUID("493d666a-1242-46a2-8425-b061e215884c"),
                "name": "Channel 1",
                "description": "Example description.",
                "revision": "0",
            },
            {
                "id": UUID("493d666a-1242-46a2-8425-b061e215884d"),
                "name": "Channel 2",
                "description": "Example description 2.",
                "revision": "0",
            },
        ]
    }
