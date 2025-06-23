import datetime
from pathlib import Path
from mirth_client.models import EventList

EVENT_LIST_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-serverEventList.xml")
    .read_text()
)

EVENT_LIST_RESPONSE_MULTIPLE = (
    Path(__file__)
    .parent.parent.joinpath(
        "examples/3.12.0/responses/get-serverEventList.multiple.xml"
    )
    .read_text()
)


def test_xml_to_obj():
    response = EventList.parse_raw(EVENT_LIST_RESPONSE)
    assert response == {
        "event": [
            {
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
                    2022, 2, 1, 12, 39, 54, 113000, tzinfo=datetime.timezone.utc
                ),
            }
        ]
    }


def test_xml_to_obj_multiple():
    response = EventList.parse_raw(EVENT_LIST_RESPONSE_MULTIPLE)
    assert response == {
        "event": [
            {
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
                    2022, 2, 1, 12, 39, 54, 113000, tzinfo=datetime.timezone.utc
                ),
            },
            {
                "id": 1,
                "level": "INFORMATION",
                "name": "Name 2",
                "outcome": "SUCCESS",
                "attributes": {
                    "@class": "linked-hash-map",
                    "entry": {"string": ["key", "value"]},
                },
                "user_id": "0",
                "ip_address": "0:0:0:0:0:0:0:1",
                "date_time": datetime.datetime(
                    2022, 2, 1, 12, 39, 54, 114000, tzinfo=datetime.timezone.utc
                ),
            },
        ]
    }
