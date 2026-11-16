"""CSRF protection and login rate limiting, which the other tests switch off."""

import pytest

from app.auth.service import create_user
from app.constants import Role
from app.errors import TOO_MANY_LOGINS_MESSAGE
from app.extensions import db
from tests.conftest import PASSWORD, build_app, login


@pytest.fixture
def strict_client(request):
    """A client for an app with the protections named by the test switched on."""
    app, context = build_app(**request.param)
    create_user("wei", "Wei Jie", Role.PLAYER, PASSWORD, must_change_password=False)
    yield app.test_client()
    db.session.remove()
    context.pop()


@pytest.mark.parametrize("strict_client", [{"WTF_CSRF_ENABLED": True}], indirect=True)
def test_form_without_csrf_token_is_rejected(strict_client):
    response = login(strict_client, "wei")

    assert response.status_code == 400
    assert strict_client.get("/playbook").status_code == 302


@pytest.mark.parametrize("strict_client", [{"WTF_CSRF_ENABLED": True}], indirect=True)
def test_login_page_contains_a_csrf_token(strict_client):
    assert 'name="csrf_token"' in strict_client.get("/login").text


@pytest.mark.parametrize("strict_client", [{"RATELIMIT_ENABLED": True}], indirect=True)
def test_sixth_login_attempt_in_a_minute_is_blocked(strict_client):
    for _ in range(5):
        assert login(strict_client, "wei", "wrong-password").status_code == 200

    response = login(strict_client, "wei", PASSWORD)

    assert response.status_code == 429
    assert TOO_MANY_LOGINS_MESSAGE in response.text
    assert strict_client.get("/playbook").status_code == 302


@pytest.mark.parametrize("strict_client", [{"RATELIMIT_ENABLED": True}], indirect=True)
def test_viewing_the_login_page_is_not_rate_limited(strict_client):
    for _ in range(8):
        assert strict_client.get("/login").status_code == 200
