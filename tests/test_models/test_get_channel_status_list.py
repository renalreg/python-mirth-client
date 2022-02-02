from pathlib import Path
from uuid import UUID
from mirth_client.models import DashboardStatusList, MirthDatetime

DASHBOARD_STATUS_LIST_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-dashboard_status_list.xml")
    .read_text()
)

DASHBOARD_STATUS_LIST_RESPONSE_MULTIPLE = (
    Path(__file__)
    .parent.parent.joinpath(
        "examples/3.12.0/responses/get-dashboard_status_list.multiple.xml"
    )
    .read_text()
)


def test_xml_to_obj():
    response = DashboardStatusList.parse_raw(DASHBOARD_STATUS_LIST_RESPONSE)
    assert response == {
        "dashboard_status": [
            {
                "channel_id": UUID("4b432aec-29f1-4855-b6df-6fa382d1e5fa"),
                "name": "Channel Name",
                "state": "STARTED",
                "deployed_revision_delta": 0,
                "deployed_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
            }
        ]
    }


def test_xml_to_obj_multiple():
    response = DashboardStatusList.parse_raw(DASHBOARD_STATUS_LIST_RESPONSE_MULTIPLE)
    assert response == {
        "dashboard_status": [
            {
                "channel_id": UUID("4b432aec-29f1-4855-b6df-6fa382d1e5fa"),
                "name": "Channel Name",
                "state": "STARTED",
                "deployed_revision_delta": 0,
                "deployed_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
            },
            {
                "channel_id": UUID("4b432aec-29f1-4855-b6df-6fa382d1e5fb"),
                "name": "Channel Name 2",
                "state": "STARTED",
                "deployed_revision_delta": 0,
                "deployed_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
            },
        ]
    }
