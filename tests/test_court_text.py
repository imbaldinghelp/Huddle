"""The court diagram in words, as the assistant reads it."""

import pytest

from app.assistant.court_text import describe_diagram, spot_name
from tests.conftest import diagram_data


@pytest.mark.parametrize(
    "x, y, name",
    [
        (0.5, 0.65, "top of the key"),
        (0.812, 0.45, "right wing"),
        (0.188, 0.45, "left wing"),
        (0.06, 0.1, "left corner"),
        (0.94, 0.1, "right corner"),
        (0.5, 0.15, "under the basket"),
        (0.4, 0.12, "left block"),
        (0.36, 0.42, "left elbow"),
        (0.5, 0.42, "free-throw line"),
        (0.25, 0.12, "left short corner"),
        (0.5, 0.9, "near half court"),
        (0.5, 0.0, "out of bounds behind the baseline, under the basket"),
        (0.02, 0.5, "out of bounds on the left sideline"),
    ],
)
def test_spots_get_basketball_names(x, y, name):
    assert spot_name(x, y) == name


def test_a_step_is_described_in_words():
    lines = describe_diagram(diagram_data())

    assert lines[0] == (
        "Positions at the start: 1 at the top of the key (has the ball), 2 at the right wing, "
        "3 at the left wing, 4 at the left mid post, 5 at the right mid post."
    )
    assert lines[1] == "What happens: 1 passes to 2. 3 cuts to the left block."


def test_a_screen_names_the_teammate_it_is_for():
    diagram = diagram_data(actions=[{"type": "screen", "player": "O5", "path": [[0.78, 0.43]]}])

    assert "5 sets a screen for 2 at the right mid-range wing." in describe_diagram(diagram)[-1]


def test_a_step_with_no_arrows_says_nobody_moves():
    assert describe_diagram(diagram_data(actions=[]))[-1] == "What happens: nobody moves (a set-up step)."


def test_defenders_are_listed_on_their_own_line():
    defenders = [{"id": f"X{n}", "team": "defense", "x": 0.5, "y": 0.5} for n in range(1, 6)]
    diagram = diagram_data()
    diagram["players"] = diagram["players"] + defenders

    lines = describe_diagram(diagram)

    assert lines[1].startswith("Defenders: X1 at the high post")
    # Defenders never have the ball, and screens are only set for teammates.
    assert "(has the ball)" not in lines[1]
