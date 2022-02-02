from pathlib import Path
from uuid import UUID
from mirth_client.models import ChannelStatistics

CHANNEL_STATISTICS_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-channel_statistics.xml")
    .read_text()
)


def test_xml_to_obj():
    response = ChannelStatistics.parse_raw(CHANNEL_STATISTICS_RESPONSE)
    assert response == {
        "server_id": UUID("fb4966f7-891a-485d-ba1a-69f5b0e5147f"),
        "channel_id": UUID("40f6d5fc-0d1f-4163-bb9b-9f64c9841c33"),
        "received": 0,
        "sent": 0,
        "error": 0,
        "filtered": 0,
        "queued": 0,
    }
