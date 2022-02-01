from pathlib import Path
from mirth_client.models import LoginResponse

LOGIN_RESPONSE = (
    Path(__file__)
    .parent.parent.joinpath("examples/3.12.0/responses/post-loginStatus.xml")
    .read_text()
)


def test_xml_to_obj():
    login_response = LoginResponse.parse_raw(LOGIN_RESPONSE)
    assert login_response == {
        "status": "SUCCESS",
        "message": None,
        "updated_username": "newUserName",
    }
