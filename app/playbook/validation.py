"""Checks a play sent by the court editor before it is saved.

The editor runs in the browser, so nothing it sends can be trusted: every
value is checked here and the play is rebuilt from the checked values only.
The diagram format is documented in app/static/js/court/README.md.
"""

from app.constants import PlayCategory, PlayStatus

MAX_TITLE = 80
MAX_SUMMARY = 200
MAX_DESCRIPTION = 500
MAX_STEPS = 20
MAX_PATH_POINTS = 12

OFFENSE_IDS = ["O1", "O2", "O3", "O4", "O5"]
DEFENSE_IDS = ["X1", "X2", "X3", "X4", "X5"]
# A player moves in one of these ways. A pass moves the ball instead.
MOVE_TYPES = {"cut", "dribble", "screen"}
# One move for each player, plus one pass.
MAX_ACTIONS = len(OFFENSE_IDS) + len(DEFENSE_IDS) + 1


class DiagramError(Exception):
    """Raised when a step's diagram breaks a rule. The message is shown to the admin."""


def validate_play(data):
    """Check a whole play. Returns (clean_play, errors).

    clean_play is a dict that is safe to save, or None when there are errors.
    errors is a list of messages for the admin.
    """
    if not isinstance(data, dict):
        return None, ["The play could not be read. Refresh the page and try again."]

    errors = []
    play = {
        "title": clean_text(data.get("title"), "Title", MAX_TITLE, errors, required=True),
        "category": clean_choice(data.get("category"), PlayCategory, "Choose a category.", errors),
        "summary": clean_text(data.get("summary"), "Summary", MAX_SUMMARY, errors),
        "status": clean_choice(data.get("status"), PlayStatus, "Choose draft or published.", errors),
        "steps": clean_steps(data.get("steps"), errors),
    }
    if errors:
        return None, errors
    return play, []


def clean_text(value, label, max_length, errors, required=False):
    if not isinstance(value, str):
        value = ""
    # Browsers on Windows send line breaks as two characters; store one.
    value = value.replace("\r\n", "\n").strip()
    if required and not value:
        errors.append(f"{label}: enter a {label.lower()}.")
    if len(value) > max_length:
        errors.append(f"{label}: use {max_length} characters or fewer.")
    return value


def clean_choice(value, choices, message, errors):
    allowed = [choice.value for choice in choices]
    if value not in allowed:
        errors.append(message)
        return None
    return value


def clean_steps(raw_steps, errors):
    if not isinstance(raw_steps, list) or not raw_steps:
        errors.append("A play needs at least one step.")
        return []
    if len(raw_steps) > MAX_STEPS:
        errors.append(f"A play can have at most {MAX_STEPS} steps.")
        return []

    steps = []
    for number, raw_step in enumerate(raw_steps, start=1):
        label = f"Step {number}"
        if not isinstance(raw_step, dict):
            errors.append(f"{label}: the step could not be read.")
            continue
        description = clean_text(raw_step.get("description"), label, MAX_DESCRIPTION, errors)
        try:
            diagram = clean_diagram(raw_step.get("diagram"))
        except DiagramError as error:
            errors.append(f"{label}: {error}")
            continue
        steps.append({"description": description, "diagram": diagram})

    if not errors and not same_players_in_every_step(steps):
        errors.append("Every step must show the same players.")
    return steps


def same_players_in_every_step(steps):
    line_ups = {tuple(player["id"] for player in step["diagram"]["players"]) for step in steps}
    return len(line_ups) == 1


# ---------- One step's diagram ----------


def clean_diagram(raw):
    """Return a checked copy of one diagram, or raise DiagramError."""
    require(isinstance(raw, dict), "the diagram is missing.")
    players = clean_players(raw.get("players"))
    player_ids = [player["id"] for player in players]
    holder = clean_holder(raw.get("ball"))
    actions = clean_actions(raw.get("actions"), player_ids, holder)
    return {"players": players, "ball": {"holder": holder}, "actions": actions}


def require(condition, message):
    if not condition:
        raise DiagramError(message)


def clean_players(raw_players):
    require(isinstance(raw_players, list), "the players are missing.")
    require(len(raw_players) <= len(OFFENSE_IDS) + len(DEFENSE_IDS), "there are too many players.")

    positions = {}
    for raw in raw_players:
        require(isinstance(raw, dict), "a player could not be read.")
        player_id = raw.get("id")
        require(isinstance(player_id, str), "a player has no name.")
        require(player_id not in positions, f"{player_id} appears twice.")
        positions[player_id] = (clean_coordinate(raw.get("x")), clean_coordinate(raw.get("y")))

    # The line-up is the five attackers, with or without all five defenders.
    line_up = OFFENSE_IDS + DEFENSE_IDS if DEFENSE_IDS[0] in positions else OFFENSE_IDS
    require(set(positions) == set(line_up), "the players must be 1 to 5, with or without X1 to X5.")

    return [
        {
            "id": player_id,
            "team": "offense" if player_id in OFFENSE_IDS else "defense",
            "x": positions[player_id][0],
            "y": positions[player_id][1],
        }
        for player_id in line_up
    ]


def clean_coordinate(value):
    """Positions are fractions of the court drawing: 0 is one edge, 1 the other."""
    # bool counts as a number in Python, so it is ruled out by name.
    is_number = isinstance(value, (int, float)) and not isinstance(value, bool)
    require(is_number and 0 <= value <= 1, "a position is outside the court.")
    return round(float(value), 4)


def clean_holder(raw_ball):
    """Who has the ball: always one of the five attackers."""
    require(isinstance(raw_ball, dict), "the ball is missing.")
    holder = raw_ball.get("holder")
    require(holder in OFFENSE_IDS, "the ball must be with one of players 1 to 5.")
    return holder


def clean_actions(raw_actions, player_ids, holder):
    require(isinstance(raw_actions, list), "the arrows are missing.")
    require(len(raw_actions) <= MAX_ACTIONS, "there are too many arrows.")

    actions = []
    movers = set()
    has_pass = False
    for raw in raw_actions:
        require(isinstance(raw, dict), "an arrow could not be read.")
        if raw.get("type") == "pass":
            require(not has_pass, "only one pass fits in a step. Add another step for the next pass.")
            has_pass = True
            actions.append(clean_pass(raw, holder))
        else:
            action = clean_move(raw, player_ids, holder)
            require(action["player"] not in movers, f"{action['player']} has two arrows.")
            movers.add(action["player"])
            actions.append(action)
    return actions


def clean_pass(raw, holder):
    passer, receiver = raw.get("from"), raw.get("to")
    require(passer == holder, "a pass must start from the player with the ball.")
    require(receiver in OFFENSE_IDS and receiver != passer, "a pass must go to a teammate.")
    return {"type": "pass", "from": passer, "to": receiver}


def clean_move(raw, player_ids, holder):
    move_type, player_id = raw.get("type"), raw.get("player")
    require(move_type in MOVE_TYPES, "an arrow has an unknown type.")
    require(player_id in player_ids, "an arrow belongs to a player who is not on the court.")
    if move_type == "dribble":
        require(player_id == holder, "only the player with the ball can dribble.")
    return {"type": move_type, "player": player_id, "path": clean_path(raw.get("path"))}


def clean_path(raw_path):
    """The points a player moves through, after their starting position."""
    require(isinstance(raw_path, list) and raw_path, "an arrow has no path.")
    require(len(raw_path) <= MAX_PATH_POINTS, "an arrow has too many points.")
    path = []
    for point in raw_path:
        require(isinstance(point, list) and len(point) == 2, "an arrow has a broken point.")
        path.append([clean_coordinate(point[0]), clean_coordinate(point[1])])
    return path
