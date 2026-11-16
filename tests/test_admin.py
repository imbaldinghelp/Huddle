import re

import pytest

from app.auth.service import WRONG_LOGIN_MESSAGE, find_user
from app.constants import Role
from tests.conftest import PASSWORD, login

ADMIN_PAGES = [
    ("GET", "/admin/"),
    ("GET", "/admin/players"),
    ("GET", "/admin/players/new"),
    ("POST", "/admin/players/new"),
    ("POST", "/admin/players/1/reset-password"),
    ("POST", "/admin/players/1/deactivate"),
    ("POST", "/admin/players/1/reactivate"),
    ("GET", "/admin/plays"),
    ("GET", "/admin/plays/new"),
    ("POST", "/admin/plays"),
    ("GET", "/admin/plays/1/edit"),
    ("POST", "/admin/plays/1"),
    ("POST", "/admin/plays/1/publish"),
    ("POST", "/admin/plays/1/unpublish"),
    ("POST", "/admin/plays/1/delete"),
]


def temp_password_on(page):
    """Read the temporary password out of the credentials page."""
    values = re.findall(r"<dd>(.+?)</dd>", page)
    return values[1]


@pytest.mark.parametrize("method, path", ADMIN_PAGES)
def test_players_get_403_on_admin_routes(client, player, method, path):
    login(client, "wei")

    response = client.open(path, method=method)

    assert response.status_code == 403
    assert "Admins only." in response.text


@pytest.mark.parametrize("method, path", ADMIN_PAGES)
def test_visitors_are_sent_to_login_from_admin_routes(client, method, path):
    response = client.open(path, method=method)

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")


def test_admin_sees_players_list(client, admin, player):
    login(client, "coach")

    page = client.get("/admin/players").text

    assert "Wei Jie" in page
    assert "Coach Tan" in page


def test_admin_creates_player_with_temporary_password(client, admin):
    login(client, "coach")

    response = client.post("/admin/players/new", data={"display_name": "Jun Hao", "username": "Jun"})

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    temp_password = temp_password_on(response.text)

    created = find_user("jun")
    assert created.role == Role.PLAYER
    assert created.must_change_password is True
    assert created.password_hash != temp_password
    assert created.check_password(temp_password)

    # The password is shown once only: it is not on the players list afterwards.
    assert temp_password not in client.get("/admin/players").text


@pytest.mark.parametrize(
    "username, message",
    [
        ("wei", "That username is already taken."),
        ("a", "Use 3 to 30 characters"),
        ("has space", "Use 3 to 30 characters"),
    ],
)
def test_bad_usernames_are_rejected(client, admin, player, username, message):
    login(client, "coach")

    response = client.post(
        "/admin/players/new", data={"display_name": "Someone", "username": username}
    )

    assert message in response.text
    assert find_user("someone") is None


def test_reset_password_replaces_the_old_one(client, admin, player):
    login(client, "coach")

    response = client.post(f"/admin/players/{player.id}/reset-password")
    temp_password = temp_password_on(response.text)

    assert player.must_change_password is True
    assert not player.check_password(PASSWORD)

    client.post("/logout")
    assert WRONG_LOGIN_MESSAGE in login(client, "wei", PASSWORD).text
    assert login(client, "wei", temp_password).status_code == 302


def test_deactivate_and_reactivate_player(client, admin, player):
    login(client, "coach")

    client.post(f"/admin/players/{player.id}/deactivate")
    assert player.is_active is False

    client.post(f"/admin/players/{player.id}/reactivate")
    assert player.is_active is True


def test_admin_cannot_deactivate_themselves(client, admin):
    login(client, "coach")

    response = client.post(f"/admin/players/{admin.id}/deactivate", follow_redirects=True)

    assert admin.is_active is True
    assert "You cannot deactivate your own account." in response.text


def test_admin_cannot_reset_their_own_password_here(client, admin):
    login(client, "coach")

    client.post(f"/admin/players/{admin.id}/reset-password")

    assert admin.check_password(PASSWORD)
    assert admin.must_change_password is False


def test_actions_on_a_missing_user_give_404(client, admin):
    login(client, "coach")

    assert client.post("/admin/players/999/deactivate").status_code == 404
