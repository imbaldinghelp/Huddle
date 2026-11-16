"""Admins creating, editing, publishing and deleting plays."""

import pytest

from app.auth.service import create_user
from app.constants import PlayStatus, Role
from app.extensions import db
from app.models.play import Play, PlayStep
from tests.conftest import PASSWORD, build_app, diagram_data, login, make_play, play_data


def all_plays():
    return db.session.query(Play).all()


def test_admin_sees_every_play_drafts_included(client, admin):
    make_play(admin, title="Horns Flare")
    make_play(admin, title="Secret Draft", status="draft")
    login(client, "coach")

    page = client.get("/admin/plays").text

    assert "Horns Flare" in page
    assert "Secret Draft" in page


def test_editor_page_loads_for_a_new_play(client, admin):
    login(client, "coach")

    page = client.get("/admin/plays/new").text

    assert "New play" in page
    assert 'data-save-url="/admin/plays"' in page


def test_editor_page_loads_a_saved_play(client, admin):
    play = make_play(admin, title="Horns Flare")
    login(client, "coach")

    page = client.get(f"/admin/plays/{play.id}/edit").text

    assert 'value="Horns Flare"' in page
    assert "1 passes to 2 on the wing." in page
    assert f'data-save-url="/admin/plays/{play.id}"' in page


def test_admin_creates_a_draft(client, admin):
    login(client, "coach")

    response = client.post("/admin/plays", json=play_data(title="Horns Flare", status="draft"))

    assert response.status_code == 200
    play = all_plays()[0]
    assert response.json == {"redirect": f"/admin/plays/{play.id}/edit"}
    assert play.title == "Horns Flare"
    assert play.status == PlayStatus.DRAFT
    assert play.created_by == admin.id
    assert play.steps[0].step_number == 1
    assert play.steps[0].diagram["ball"] == {"holder": "O1"}


def test_admin_publishes_from_the_editor(client, admin):
    login(client, "coach")

    response = client.post("/admin/plays", json=play_data(status="published"))

    assert response.json == {"redirect": "/admin/plays"}
    assert all_plays()[0].is_published


def test_saving_again_replaces_the_steps(client, admin):
    play = make_play(admin, title="Horns Flare")
    login(client, "coach")
    two_steps = [
        {"description": "First.", "diagram": diagram_data()},
        {"description": "Second.", "diagram": diagram_data(actions=[])},
    ]

    client.post(f"/admin/plays/{play.id}", json=play_data(title="Horns Flare 2", steps=two_steps))

    assert len(all_plays()) == 1
    assert play.title == "Horns Flare 2"
    assert [step.description for step in play.steps] == ["First.", "Second."]
    # The old step is gone from the database, not just from the play.
    assert db.session.query(PlayStep).count() == 2


def test_invalid_play_is_not_saved(client, admin):
    login(client, "coach")
    broken = play_data(title="", steps=[{"description": "", "diagram": diagram_data(ball={"holder": "X9"})}])

    response = client.post("/admin/plays", json=broken)

    assert response.status_code == 400
    assert "Title: enter a title." in response.json["errors"]
    assert any(error.startswith("Step 1:") for error in response.json["errors"])
    assert all_plays() == []


def test_a_request_that_is_not_json_is_rejected(client, admin):
    login(client, "coach")

    response = client.post("/admin/plays", data="not json")

    assert response.status_code == 400
    assert all_plays() == []


def test_publish_and_unpublish_from_the_list(client, admin):
    play = make_play(admin, status="draft")
    login(client, "coach")

    client.post(f"/admin/plays/{play.id}/publish")
    assert play.status == PlayStatus.PUBLISHED

    response = client.post(f"/admin/plays/{play.id}/unpublish", follow_redirects=True)
    assert play.status == PlayStatus.DRAFT
    assert "is back in drafts" in response.text


def test_delete_removes_the_play_and_its_steps(client, admin):
    play = make_play(admin, title="Horns Flare")
    login(client, "coach")

    response = client.post(f"/admin/plays/{play.id}/delete", follow_redirects=True)

    assert "Horns Flare has been deleted." in response.text
    assert all_plays() == []
    assert db.session.query(PlayStep).count() == 0


def test_actions_on_a_missing_play_give_404(client, admin):
    login(client, "coach")

    assert client.get("/admin/plays/999/edit").status_code == 404
    assert client.post("/admin/plays/999", json=play_data()).status_code == 404
    assert client.post("/admin/plays/999/delete").status_code == 404


def test_player_cannot_change_plays(client, admin, player):
    play = make_play(admin, title="Horns Flare")
    login(client, "wei")

    assert client.post("/admin/plays", json=play_data(title="Sneaky")).status_code == 403
    assert client.post(f"/admin/plays/{play.id}", json=play_data(title="Sneaky")).status_code == 403
    assert client.post(f"/admin/plays/{play.id}/unpublish").status_code == 403
    assert client.post(f"/admin/plays/{play.id}/delete").status_code == 403

    assert [saved.title for saved in all_plays()] == ["Horns Flare"]
    assert play.is_published


# ---------- CSRF on the editor's JSON save ----------


@pytest.fixture
def csrf_client():
    """A logged-in admin's browser, on an app with CSRF protection switched on."""
    app, context = build_app(WTF_CSRF_ENABLED=True)
    coach = create_user("coach", "Coach Tan", Role.ADMIN, PASSWORD, must_change_password=False)
    client = app.test_client()
    # The login form needs a token too, so log in by filling the session directly.
    with client.session_transaction() as session:
        session["_user_id"] = str(coach.id)
        session["_fresh"] = True
    yield client
    db.session.remove()
    context.pop()


def test_editor_save_without_csrf_token_is_rejected(csrf_client):
    response = csrf_client.post("/admin/plays", json=play_data())

    assert response.status_code == 400
    assert all_plays() == []


def test_editor_save_with_csrf_token_in_the_header_works(csrf_client):
    page = csrf_client.get("/admin/plays/new").text
    token = page.split('data-csrf-token="')[1].split('"')[0]

    response = csrf_client.post("/admin/plays", json=play_data(), headers={"X-CSRFToken": token})

    assert response.status_code == 200
    assert len(all_plays()) == 1
