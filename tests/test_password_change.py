import pytest

from app.auth.service import create_user
from app.constants import Role
from tests.conftest import PASSWORD, login

TEMP_PASSWORD = "temp-Pass-1234"
NEW_PASSWORD = "my-own-new-password"


@pytest.fixture
def new_player(app):
    """A player who still has the temporary password an admin gave them."""
    return create_user("jun", "Jun Hao", Role.PLAYER, TEMP_PASSWORD, must_change_password=True)


def set_password(client, new, confirm=None):
    data = {"new_password": new, "confirm_password": confirm or new}
    return client.post("/account/password", data=data)


def test_first_login_goes_to_password_page(client, new_player):
    response = login(client, "jun", TEMP_PASSWORD)
    assert response.headers["Location"] == "/playbook"

    # Every page sends them back until the password is changed.
    response = client.get("/playbook")
    assert response.status_code == 302
    assert response.headers["Location"] == "/account/password"
    assert "Set your password." in client.get("/account/password").text


def test_setting_a_password_unlocks_the_playbook(client, new_player):
    login(client, "jun", TEMP_PASSWORD)

    response = set_password(client, NEW_PASSWORD)

    assert response.headers["Location"] == "/playbook"
    assert new_player.must_change_password is False
    assert new_player.check_password(NEW_PASSWORD)
    assert client.get("/playbook").status_code == 200


def test_user_can_still_log_out_before_changing_password(client, new_player):
    login(client, "jun", TEMP_PASSWORD)

    assert client.post("/logout").headers["Location"] == "/login"


@pytest.mark.parametrize(
    "new, confirm, message",
    [
        ("short", "short", "Use at least 8 characters."),
        (NEW_PASSWORD, "something-else", "The two passwords do not match."),
        (TEMP_PASSWORD, TEMP_PASSWORD, "different from your current one"),
    ],
)
def test_bad_new_passwords_are_rejected(client, new_player, new, confirm, message):
    login(client, "jun", TEMP_PASSWORD)

    response = set_password(client, new, confirm)

    assert response.status_code == 200
    assert message in response.text
    assert new_player.must_change_password is True


def test_changing_password_by_choice_needs_the_current_one(client, player):
    login(client, "wei")
    data = {"new_password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD}

    response = client.post("/account/password", data={**data, "current_password": "wrong"})
    assert "That is not your current password." in response.text
    assert player.check_password(PASSWORD)

    response = client.post("/account/password", data={**data, "current_password": PASSWORD})
    assert response.headers["Location"] == "/playbook"
    assert player.check_password(NEW_PASSWORD)
