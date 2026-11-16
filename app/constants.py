"""Fixed values used across the app: user roles and play categories.

Keeping them here means a new category is added in one place only.
"""

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    PLAYER = "player"


class PlayCategory(StrEnum):
    OFFENSE = "offense"
    DEFENSE = "defense"
    SIDELINE = "sideline"
    BASELINE = "baseline"


# The name shown to users for each category.
CATEGORY_LABELS = {
    PlayCategory.OFFENSE: "Offense",
    PlayCategory.DEFENSE: "Defense",
    PlayCategory.SIDELINE: "Sideline (SLOB)",
    PlayCategory.BASELINE: "Baseline (BLOB)",
}
