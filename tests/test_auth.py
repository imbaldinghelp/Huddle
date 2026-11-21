from app.auth.service import DEACTIVATED_MESSAGE, WRONG_LOGIN_MESSAGE
from app.extensions import db
from tests.conftest import PASSWORD, login


def test_login_success_opens_playbook(client, player):
    response = login(client, "wei")

    assert response.status_code == 302
    assert response.headers["Location"] == "/playbook"
    assert client.get("/playbook").status_code == 200
    assert player.last_login_at is not None


def test_username_is_not_case_sensitive(client, player):
    response = login(client, "  WEI ")

    assert response.headers["Location"] == "/playbook"


def test_wrong_password_is_rejected(client, player):
    response = login(client, "wei", "not-the-password")

    assert response.status_code == 200
    assert WRONG_LOGIN_MESSAGE in response.text
    assert client.get("/playbook").status_code == 302


def test_unknown_username_gets_the_same_message(client, player):
    response = login(client, "nobody", PASSWORD)

    assert response.status_code == 200
    assert WRONG_LOGIN_MESSAGE in response.text


def test_deactivated_user_cannot_log_in(client, player):
    player.is_active = False
    db.session.commit()

    response = login(client, "wei")

    assert response.status_code == 200
    assert DEACTIVATED_MESSAGE in response.text
    assert client.get("/playbook").status_code == 302


def test_deactivated_user_with_wrong_password_learns_nothing(client, player):
    player.is_active = False
    db.session.commit()

    response = login(client, "wei", "not-the-password")

    assert WRONG_LOGIN_MESSAGE in response.text
    assert DEACTIVATED_MESSAGE not in response.text


def test_deactivating_a_logged_in_user_ends_their_session(client, player):
    login(client, "wei")
    assert client.get("/playbook").status_code == 200

    player.is_active = False
    db.session.commit()

    assert client.get("/playbook").status_code == 302


def test_playbook_requires_login(client):
    response = client.get("/playbook")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")


def test_logout_ends_the_session(client, player):
    login(client, "wei")

    response = client.post("/logout")

    assert response.headers["Location"] == "/login"
    assert client.get("/playbook").status_code == 302


def test_login_returns_to_the_page_you_wanted(client, player):
    response = client.post(
        "/login?next=/account/password", data={"username": "wei", "password": PASSWORD}
    )

    assert response.headers["Location"] == "/account/password"


def test_login_ignores_links_to_other_websites(client, player):
    response = client.post(
        "/login?next=https://evil.example", data={"username": "wei", "password": PASSWORD}
    )

    assert response.headers["Location"] == "/playbook"


def test_header_hides_admin_link_from_players(client, player):
    login(client, "wei")

    page = client.get("/playbook").text

    assert "Wei Jie" in page
    assert "/admin" not in page


def test_header_shows_admin_link_to_admins(client, admin):
    login(client, "coach")

    assert 'href="/admin/players"' in client.get("/playbook").text


# ---------- Account page ----------


def test_clicking_your_name_opens_your_account(client, player):
    login(client, "wei")

    assert 'href="/account"' in client.get("/playbook").text
    page = client.get("/account").text

    assert "Your account" in page
    assert "Wei Jie" in page
    assert "wei" in page
    assert "Player" in page
    assert "questions left today" in page
    assert 'href="/account/password"' in page


def test_account_page_needs_a_login(client):
    response = client.get("/account")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login")
