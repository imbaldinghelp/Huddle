"""The server-side check on what the court editor sends."""

import pytest

from app.playbook.validation import MAX_PATH_POINTS, MAX_STEPS, validate_play
from tests.conftest import diagram_data, play_data

DEFENDERS = [{"id": f"X{number}", "team": "defense", "x": 0.5, "y": 0.1 * number} for number in range(1, 6)]


def errors_for(**changes):
    clean, errors = validate_play(play_data(**changes))
    assert clean is None
    return " ".join(errors)


def errors_for_diagram(**changes):
    return errors_for(steps=[{"description": "", "diagram": diagram_data(**changes)}])


def players_with(player_id, **changes):
    """The usual players, with one of them changed."""
    players = diagram_data()["players"]
    for player in players:
        if player["id"] == player_id:
            player.update(changes)
    return players


def one_cut(**changes):
    return {"type": "cut", "player": "O2", "path": [[0.1, 0.1]], **changes}


def test_valid_play_is_accepted_and_cleaned():
    data = play_data(title="  Horns Flare  ")
    data["steps"][0]["diagram"]["extra"] = "ignored"

    clean, errors = validate_play(data)

    assert errors == []
    assert clean["title"] == "Horns Flare"
    diagram = clean["steps"][0]["diagram"]
    # Only the known keys are kept.
    assert set(diagram) == {"players", "ball", "actions"}
    assert [player["id"] for player in diagram["players"]] == ["O1", "O2", "O3", "O4", "O5"]


def test_defenders_are_accepted_when_all_five_are_there():
    players = diagram_data()["players"] + DEFENDERS
    data = play_data(steps=[{"description": "", "diagram": diagram_data(players=players)}])

    clean, errors = validate_play(data)

    assert errors == []
    assert len(clean["steps"][0]["diagram"]["players"]) == 10


@pytest.mark.parametrize("data", [None, [], "play", 42])
def test_something_that_is_not_a_play_is_rejected(data):
    clean, errors = validate_play(data)

    assert clean is None
    assert errors


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"title": "   "}, "Title: enter a title."),
        ({"title": "x" * 81}, "Title: use 80 characters or fewer."),
        ({"summary": "x" * 201}, "Summary: use 200 characters or fewer."),
        ({"category": "zone"}, "Choose a category."),
        ({"status": "secret"}, "Choose draft or published."),
        ({"steps": []}, "at least one step"),
        ({"steps": "none"}, "at least one step"),
        ({"steps": [{"description": "", "diagram": diagram_data()}] * (MAX_STEPS + 1)}, "at most 20 steps"),
        ({"steps": [{"description": "x" * 501, "diagram": diagram_data()}]}, "Step 1: use 500 characters or fewer."),
        ({"steps": [{"description": ""}]}, "Step 1: the diagram is missing."),
    ],
)
def test_bad_play_details_are_rejected(changes, message):
    assert message in errors_for(**changes)


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"players": players_with("O1", x=1.2)}, "outside the court"),
        ({"players": players_with("O1", y=-0.1)}, "outside the court"),
        ({"players": players_with("O1", x="0.5")}, "outside the court"),
        ({"players": players_with("O1", x=True)}, "outside the court"),
        ({"players": players_with("O1", x=float("nan"))}, "outside the court"),
        ({"players": players_with("O5", id="O9")}, "players must be 1 to 5"),
        ({"players": players_with("O5", id="O1")}, "O1 appears twice"),
        ({"players": diagram_data()["players"][:4]}, "players must be 1 to 5"),
        ({"players": diagram_data()["players"] + DEFENDERS[:1]}, "players must be 1 to 5"),
        ({"ball": {"holder": "X1"}}, "ball must be with one of players 1 to 5"),
        ({"ball": None}, "the ball is missing"),
        ({"actions": [one_cut(type="teleport")]}, "unknown type"),
        ({"actions": [one_cut(player="O7")]}, "not on the court"),
        ({"actions": [one_cut(path=[])]}, "has no path"),
        ({"actions": [one_cut(path=[[0.1, 5]])]}, "outside the court"),
        ({"actions": [one_cut(path=[[0.1]])]}, "broken point"),
        ({"actions": [one_cut(path=[[0.1, 0.1]] * (MAX_PATH_POINTS + 1))]}, "too many points"),
        ({"actions": [one_cut(), one_cut()]}, "O2 has two arrows"),
        ({"actions": [one_cut(type="dribble")]}, "only the player with the ball can dribble"),
        ({"actions": [{"type": "pass", "from": "O2", "to": "O3"}]}, "must start from the player with the ball"),
        ({"actions": [{"type": "pass", "from": "O1", "to": "O1"}]}, "must go to a teammate"),
        ({"actions": [{"type": "pass", "from": "O1", "to": "O2"}] * 2}, "only one pass"),
        ({"actions": [one_cut()] * 12}, "too many arrows"),
    ],
)
def test_bad_diagrams_are_rejected(changes, message):
    errors = errors_for_diagram(**changes)

    assert errors.startswith("Step 1: ")
    assert message in errors


def test_every_step_must_show_the_same_players():
    steps = [
        {"description": "", "diagram": diagram_data()},
        {"description": "", "diagram": diagram_data(players=diagram_data()["players"] + DEFENDERS)},
    ]

    assert "Every step must show the same players." in errors_for(steps=steps)


def test_the_broken_step_is_named():
    steps = [
        {"description": "", "diagram": diagram_data()},
        {"description": "", "diagram": diagram_data(ball={"holder": "nobody"})},
    ]

    assert "Step 2: the ball must be with one of players 1 to 5." in errors_for(steps=steps)
