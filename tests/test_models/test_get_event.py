import datetime
from pathlib import Path
from mirth_client.models import EventModel

EVENT_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-serverEvent.xml")
    .read_text()
)


def test_xml_to_obj():
    response = EventModel.parse_raw(EVENT_RESPONSE)
    assert response == {
        "id": 0,
        "level": "INFORMATION",
        "name": "Name 1",
        "outcome": "SUCCESS",
        "attributes": {
            "@class": "linked-hash-map",
            "entry": {"string": ["key", "value"]},
        },
        "user_id": "0",
        "ip_address": "0:0:0:0:0:0:0:1",
        "date_time": datetime.datetime(
            2022, 2, 1, 12, 39, 54, 101000, tzinfo=datetime.timezone.utc
        ),
    }
