from pathlib import Path
from uuid import UUID
from mirth_client.models import ChannelStatisticsList

CHANNEL_STATISTICS_LIST_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-channel_statistics_list.xml")
    .read_text()
)

CHANNEL_STATISTICS_LIST_RESPONSE_MULTIPLE = (
    Path(__file__)
    .parent.parent.joinpath(
        "examples/3.12.0/responses/get-channel_statistics_list.multiple.xml"
    )
    .read_text()
)


def test_xml_to_obj():
    response = ChannelStatisticsList.parse_raw(CHANNEL_STATISTICS_LIST_RESPONSE)
    assert response == {
        "channel_statistics": [
            {
                "server_id": UUID("816f6ff6-8756-4674-b523-c9ca7559186e"),
                "channel_id": UUID("48830179-3d76-4568-a8e0-b2c645a07546"),
                "received": 0,
                "sent": 0,
                "error": 0,
                "filtered": 0,
                "queued": 0,
            }
        ]
    }


def test_xml_to_obj_multiple():
    response = ChannelStatisticsList.parse_raw(
        CHANNEL_STATISTICS_LIST_RESPONSE_MULTIPLE
    )
    assert response == {
        "channel_statistics": [
            {
                "server_id": UUID("816f6ff6-8756-4674-b523-c9ca7559186e"),
                "channel_id": UUID("48830179-3d76-4568-a8e0-b2c645a07546"),
                "received": 0,
                "sent": 0,
                "error": 0,
                "filtered": 0,
                "queued": 0,
            },
            {
                "server_id": UUID("816f6ff6-8756-4674-b523-c9ca7559186e"),
                "channel_id": UUID("48830179-3d76-4568-a8e0-b2c645a07547"),
                "received": 0,
                "sent": 0,
                "error": 0,
                "filtered": 0,
                "queued": 0,
            },
        ]
    }
