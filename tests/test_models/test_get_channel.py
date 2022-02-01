from pathlib import Path
from uuid import UUID
from mirth_client.models import ChannelModel

CHANNEL_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-channel.xml")
    .read_text()
)


def test_xml_to_obj():
    response = ChannelModel.parse_raw(CHANNEL_RESPONSE)
    assert response == {
        "id": UUID("7e9ec9f5-5d48-4216-b10f-a32587cf8647"),
        "name": "Channel 1",
        "description": "Example description.",
        "revision": "0",
    }
