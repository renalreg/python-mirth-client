from pathlib import Path
from uuid import UUID
from mirth_client.models import ChannelMessageList, MirthDatetime

CHANNEL_MESSAGES_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-messages.xml")
    .read_text()
)

CHANNEL_MESSAGES_RESPONSE_MULTIPLE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/get-messages.multiple.xml")
    .read_text()
)


def test_xml_to_obj():
    response = ChannelMessageList.parse_raw(CHANNEL_MESSAGES_RESPONSE)
    assert response == {
        "message": [
            {
                "message_id": 1,
                "server_id": UUID("ec905ad6-3c2b-414c-97d5-a1cc3d32905e"),
                "channel_id": UUID("2082b324-a2ae-4c00-afb4-fa4d0aafa15a"),
                "processed": True,
                "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
                "connector_messages": {
                    1: {
                        "chain_id": 0,
                        "order_id": 0,
                        "server_id": UUID("4979a6b2-b1e0-46d2-958b-d17eef985234"),
                        "channel_id": "d5958173-5327-4042-aea6-5a50debabd90",
                        "status": "SENT",
                        "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
                        "channel_name": "Channel 1",
                        "connector_name": None,
                        "message_id": "1",
                        "error_code": 0,
                        "send_attempts": 0,
                        "raw": None,
                        "encoded": None,
                        "sent": None,
                        "response": None,
                        "meta_data_id": 0,
                        "meta_data_map": {},
                    }
                },
            }
        ]
    }


def test_xml_to_obj_multiple():
    response = ChannelMessageList.parse_raw(CHANNEL_MESSAGES_RESPONSE_MULTIPLE)
    assert response == {
        "message": [
            {
                "message_id": 1,
                "server_id": UUID("ec905ad6-3c2b-414c-97d5-a1cc3d32905e"),
                "channel_id": UUID("2082b324-a2ae-4c00-afb4-fa4d0aafa15a"),
                "processed": True,
                "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
                "connector_messages": {
                    1: {
                        "chain_id": 0,
                        "order_id": 0,
                        "server_id": UUID("4979a6b2-b1e0-46d2-958b-d17eef985234"),
                        "channel_id": "d5958173-5327-4042-aea6-5a50debabd90",
                        "status": "SENT",
                        "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
                        "channel_name": "Channel 1",
                        "connector_name": None,
                        "message_id": "1",
                        "error_code": 0,
                        "send_attempts": 0,
                        "raw": None,
                        "encoded": None,
                        "sent": None,
                        "response": None,
                        "meta_data_id": 0,
                        "meta_data_map": {},
                    }
                },
            },
            {
                "message_id": 2,
                "server_id": UUID("ec905ad6-3c2b-414c-97d5-a1cc3d32905e"),
                "channel_id": UUID("2082b324-a2ae-4c00-afb4-fa4d0aafa15a"),
                "processed": True,
                "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 778000),
                "connector_messages": {
                    1: {
                        "chain_id": 0,
                        "order_id": 0,
                        "server_id": UUID("4979a6b2-b1e0-46d2-958b-d17eef985234"),
                        "channel_id": "d5958173-5327-4042-aea6-5a50debabd90",
                        "status": "SENT",
                        "received_date": MirthDatetime(2022, 2, 1, 9, 37, 32, 777000),
                        "channel_name": "Channel 1",
                        "connector_name": None,
                        "message_id": "2",
                        "error_code": 0,
                        "send_attempts": 0,
                        "raw": None,
                        "encoded": None,
                        "sent": None,
                        "response": None,
                        "meta_data_id": 0,
                        "meta_data_map": {},
                    }
                },
            },
        ]
    }
