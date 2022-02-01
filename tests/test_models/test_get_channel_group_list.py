from pathlib import Path
from uuid import UUID
from mirth_client.models import GroupList

CHANNEL_GROUP_LIST_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-channel_group_list.xml")
    .read_text()
)

CHANNEL_GROUP_LIST_RESPONSE_MULTIPLE = (
    Path(__file__)
    .parent.parent.joinpath(
        "examples/3.12.0/responses/get-channel_group_list.multiple.xml"
    )
    .read_text()
)


def test_xml_to_obj():
    response = GroupList.parse_raw(CHANNEL_GROUP_LIST_RESPONSE)
    assert response == {
        "channel_group": [
            {
                "id": UUID("fd79fb2c-9651-4658-8788-fbbc8f4b0760"),
                "name": "Group Name",
                "description": "Group Description",
                "revision": "1",
                "channels": [
                    {
                        "id": UUID("d93efb68-e26c-40aa-b0c2-32850299c05d"),
                        "revision": "0",
                    }
                ],
            }
        ]
    }


def test_xml_to_obj_multiple():
    response = GroupList.parse_raw(CHANNEL_GROUP_LIST_RESPONSE_MULTIPLE)
    assert response == {
        "channel_group": [
            {
                "id": UUID("fd79fb2c-9651-4658-8788-fbbc8f4b0760"),
                "name": "Group Name",
                "description": "Group Description",
                "revision": "1",
                "channels": [
                    {
                        "id": UUID("d93efb68-e26c-40aa-b0c2-32850299c05d"),
                        "revision": "0",
                    },
                    {
                        "id": UUID("d93efb68-e26c-40aa-b0c2-32850299c052"),
                        "revision": "0",
                    },
                ],
            },
            {
                "id": UUID("fd79fb2c-9651-4658-8788-fbbc8f4b0761"),
                "name": "Group Name 2",
                "description": "Group Description 2",
                "revision": "1",
                "channels": [
                    {
                        "id": UUID("d93efb68-e26c-40aa-b0c2-32850299c06d"),
                        "revision": "0",
                    },
                    {
                        "id": UUID("d93efb68-e26c-40aa-b0c2-32850299c062"),
                        "revision": "0",
                    },
                ],
            },
        ]
    }
