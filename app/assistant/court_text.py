"""Turns a step's court diagram into words the assistant can read.

The model cannot see the drawing, so each step is described in basketball
terms instead: where everyone stands, who has the ball, and who passes,
cuts, dribbles or screens to where. The diagram format is documented in
app/static/js/court/README.md.

Positions are rough on purpose ("right wing", "left block"): the model
needs the idea, not the exact spot.
"""

import math

# The court's size in decimetres, the same numbers as app/static/js/court/court.js.
COURT_WIDTH = 150
HALF_LENGTH = 140
MARGIN = 10
BASKET = (COURT_WIDTH / 2, 15.75)
THREE_POINT_RADIUS = 67.5
KEY_HALF_WIDTH = 24.5
KEY_LENGTH = 58
# The three-point line runs straight up from the baseline in the corners
# until it meets the arc, this far from the baseline.
CORNER_THREE_DEPTH = BASKET[1] + math.sqrt(THREE_POINT_RADIUS**2 - (COURT_WIDTH / 2 - 9) ** 2)


def court_point(x, y):
    """A saved position (fractions of the drawing) in decimetres on the court.

    (0, 0) is the left end of the baseline; y grows towards half court.
    """
    width = COURT_WIDTH + MARGIN * 2
    height = HALF_LENGTH + MARGIN * 2
    return x * width - MARGIN, y * height - MARGIN


def spot_name(x, y):
    """A basketball name for a spot, such as "right wing" or "left block".

    Left and right are as the attackers see them, facing the basket, which
    is also left and right on the diagram (the basket is at the top).
    """
    cx, cy = court_point(x, y)
    across = cx - BASKET[0]
    side = "left" if across < 0 else "right"

    if cy < 0:
        where = "under the basket" if abs(across) < 12 else f"{side} side"
        return f"out of bounds behind the baseline, {where}"
    if cx < 0 or cx > COURT_WIDTH:
        return f"out of bounds on the {side} sideline"
    if cy > HALF_LENGTH:
        return "past half court"

    in_corner = (cx < 9 or cx > COURT_WIDTH - 9) and cy < CORNER_THREE_DEPTH
    beyond_arc = math.dist((cx, cy), BASKET) > THREE_POINT_RADIUS
    if in_corner or (beyond_arc and cy >= CORNER_THREE_DEPTH):
        return three_point_spot(cy, across, side)
    if abs(across) <= KEY_HALF_WIDTH and cy <= KEY_LENGTH:
        return paint_spot(cy, across, side)
    return mid_range_spot(cy, across, side)


def three_point_spot(cy, across, side):
    if cy < CORNER_THREE_DEPTH:
        return f"{side} corner"
    if cy > 105:
        return "near half court" if abs(across) < 25 else f"near half court, {side} side"
    if abs(across) < 22:
        return "top of the key"
    return f"{side} wing"


def paint_spot(cy, across, side):
    if cy < 25:
        return "under the basket" if abs(across) < 8 else f"{side} block"
    if cy < 45:
        return "middle of the paint" if abs(across) < 8 else f"{side} side of the paint"
    return "free-throw line" if abs(across) < 14 else f"{side} elbow"


def mid_range_spot(cy, across, side):
    if abs(across) <= KEY_HALF_WIDTH:
        return "high post, above the free-throw line"
    if cy < 25:
        return f"{side} short corner"
    if cy < 45:
        return f"{side} mid post"
    if abs(across) < 40:
        return f"{side} elbow area"
    return f"{side} mid-range wing"


# ---------- One step in words ----------


def player_name(player_id):
    """O3 is "3" (the numbers on the diagram); defenders keep their X."""
    return player_id[1:] if player_id.startswith("O") else player_id


def describe_diagram(diagram):
    """A step's diagram as a few plain lines of text."""
    players = {player["id"]: player for player in diagram["players"]}
    holder = diagram["ball"]["holder"]

    lines = ["Positions at the start: " + positions_text(players, holder, "offense")]
    if any(player["team"] == "defense" for player in players.values()):
        lines.append("Defenders: " + positions_text(players, holder, "defense"))

    moves = [action_text(action, players) for action in diagram["actions"]]
    lines.append("What happens: " + (" ".join(moves) if moves else "nobody moves (a set-up step)."))
    return lines


def positions_text(players, holder, team):
    parts = []
    for player in players.values():
        if player["team"] != team:
            continue
        part = f"{player_name(player['id'])} at the {spot_name(player['x'], player['y'])}"
        if player["id"] == holder:
            part += " (has the ball)"
        parts.append(part)
    return ", ".join(parts) + "."


def action_text(action, players):
    if action["type"] == "pass":
        return f"{player_name(action['from'])} passes to {player_name(action['to'])}."

    who = player_name(action["player"])
    end = action["path"][-1]
    to = spot_name(*end)
    if action["type"] == "cut":
        return f"{who} cuts to the {to}."
    if action["type"] == "dribble":
        return f"{who} dribbles to the {to}."
    # A screen is set for whoever stands closest to where the screener stops.
    target = nearest_other_player(end, action["player"], players)
    for_whom = f" for {player_name(target)}" if target else ""
    return f"{who} sets a screen{for_whom} at the {to}."


# A screen this close (in metres) to a player is treated as set for them.
SCREEN_REACH = 3


def nearest_other_player(point, screener_id, players):
    """The teammate standing closest to a point, if one is within reach."""
    here = court_point(*point)
    team = players[screener_id]["team"]
    best_id, best_distance = None, SCREEN_REACH * 10
    for player_id, player in players.items():
        if player_id == screener_id or player["team"] != team:
            continue
        gap = math.dist(here, court_point(player["x"], player["y"]))
        if gap < best_distance:
            best_id, best_distance = player_id, gap
    return best_id
