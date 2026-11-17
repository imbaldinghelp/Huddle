"""What players see: categories, lists of plays and the play page."""

from datetime import timedelta

from app.extensions import db
from app.models.user import utc_now
from tests.conftest import login, make_play


def test_main_page_shows_the_four_categories_with_counts(client, admin, player):
    make_play(admin, title="Horns Flare", category="offense")
    make_play(admin, title="Motion Strong", category="offense")
    make_play(admin, title="2-3 Zone", category="defense")
    make_play(admin, title="Secret Draft", category="sideline", status="draft")
    login(client, "wei")

    page = client.get("/playbook").text

    for label in ["Offense", "Defense", "Sideline", "Baseline"]:
        assert label in page
    assert page.count(">2 plays<") == 1
    assert page.count(">1 play<") == 1
    # The draft is not counted, so sideline and baseline both show zero.
    assert page.count(">0 plays<") == 2


def test_category_page_lists_published_plays_only(client, admin, player):
    make_play(admin, title="Horns Flare", summary="Flare screen for the shooter.")
    make_play(admin, title="Secret Draft", status="draft")
    make_play(admin, title="2-3 Zone", category="defense")
    login(client, "wei")

    page = client.get("/playbook/offense").text

    assert "Horns Flare" in page
    assert "Flare screen for the shooter." in page
    assert "Secret Draft" not in page
    assert "2-3 Zone" not in page


def test_empty_category_says_so(client, player):
    login(client, "wei")

    assert "No plays here yet." in client.get("/playbook/baseline").text


def test_unknown_category_gives_404(client, player):
    login(client, "wei")

    assert client.get("/playbook/trick-shots").status_code == 404


def test_only_recently_changed_plays_are_marked_updated(client, admin, player):
    old = make_play(admin, title="Old Faithful")
    old.updated_at = utc_now() - timedelta(days=8)
    db.session.commit()
    login(client, "wei")

    assert ">Updated<" not in client.get("/playbook/offense").text

    make_play(admin, title="Brand New")
    assert client.get("/playbook/offense").text.count(">Updated<") == 1


def test_player_can_open_a_published_play(client, admin, player):
    play = make_play(admin, title="Horns Flare", coaching_notes="Set the screen and stay still.")
    login(client, "wei")

    page = client.get(f"/plays/{play.id}").text

    assert "Horns Flare" in page
    assert "Set the screen and stay still." in page
    # The step data for the court viewer is on the page.
    assert "1 passes to 2 on the wing." in page
    assert "Edit play" not in page


def test_player_never_sees_a_draft(client, admin, player):
    draft = make_play(admin, title="Secret Draft", status="draft")
    login(client, "wei")

    response = client.get(f"/plays/{draft.id}")

    assert response.status_code == 404
    assert "Secret Draft" not in response.text


def test_admin_can_preview_a_draft(client, admin):
    draft = make_play(admin, title="Secret Draft", status="draft")
    login(client, "coach")

    page = client.get(f"/plays/{draft.id}").text

    assert "Secret Draft" in page
    assert "Only admins can see this play" in page
    assert "Edit play" in page


def test_missing_play_gives_404(client, player):
    login(client, "wei")

    assert client.get("/plays/999").status_code == 404


def test_play_pages_require_login(client, admin):
    play = make_play(admin)

    for path in ["/playbook/offense", f"/plays/{play.id}"]:
        response = client.get(path)
        assert response.status_code == 302
        assert response.headers["Location"].startswith("/login")


# ---------- What admins see in the playbook ----------


def test_admin_gets_a_new_play_button_on_a_category(client, admin):
    login(client, "coach")

    page = client.get("/playbook/defense").text

    # It opens the editor with this category already chosen.
    assert 'href="/admin/plays/new?category=defense"' in page
    assert "Choose New play" in page


def test_player_gets_no_new_play_button(client, admin, player):
    make_play(admin)
    login(client, "wei")

    assert "New play" not in client.get("/playbook/offense").text
    assert "New play" not in client.get("/playbook/baseline").text


def test_admin_sees_drafts_in_a_category_marked_as_drafts(client, admin):
    make_play(admin, title="Horns Flare")
    make_play(admin, title="Secret Draft", status="draft")
    login(client, "coach")

    page = client.get("/playbook/offense").text

    assert "Horns Flare" in page
    assert "Secret Draft" in page
    assert page.count(">Draft<") == 1


def test_pages_have_a_trail_back_to_the_playbook(client, admin, player):
    play = make_play(admin, title="Horns Flare", category="offense")
    login(client, "wei")

    category_page = client.get("/playbook/offense").text
    play_page = client.get(f"/plays/{play.id}").text

    assert 'aria-label="Breadcrumb"' in category_page
    assert '<a href="/playbook">Playbook</a>' in category_page
    assert '<a href="/playbook">Playbook</a>' in play_page
    assert '<a href="/playbook/offense">Offense</a>' in play_page
