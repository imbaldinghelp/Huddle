"""Play logic: finding plays for the playbook pages and saving them for admins.

Both the playbook routes (players reading) and the admin routes (admins
editing) call these functions, so the rules about plays live in one place.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.constants import CATEGORY_LABELS, PlayCategory, PlayStatus
from app.extensions import db
from app.models.play import Play, PlayStep
from app.models.user import utc_now

# ---------- Reading (playbook pages) ----------


def list_categories():
    """The four categories with how many published plays each one holds."""
    query = (
        select(Play.category, func.count(Play.id))
        .where(Play.status == PlayStatus.PUBLISHED)
        .group_by(Play.category)
    )
    counts = dict(db.session.execute(query).all())
    return [
        {
            "slug": category.value,
            "label": CATEGORY_LABELS[category],
            "play_count": counts.get(category.value, 0),
        }
        for category in PlayCategory
    ]


def find_category(slug):
    """Turn the word in the address ("offense") into a category, or None."""
    try:
        return PlayCategory(slug)
    except ValueError:
        return None


def list_published_plays(category):
    query = (
        select(Play)
        .where(Play.category == category, Play.status == PlayStatus.PUBLISHED)
        .order_by(func.lower(Play.title))
    )
    return db.session.scalars(query).all()


def list_all_published_plays():
    """Every published play with its steps, grouped by category then title.

    The assistant reads these. selectinload fetches all the steps in one
    extra query instead of one query per play.
    """
    query = (
        select(Play)
        .where(Play.status == PlayStatus.PUBLISHED)
        .options(selectinload(Play.steps))
        .order_by(Play.category, func.lower(Play.title))
    )
    return db.session.scalars(query).all()


def get_play(play_id):
    return db.session.get(Play, play_id)


def can_view(play, user):
    """Players only ever see published plays. Admins can preview drafts."""
    return play.is_published or user.is_admin


def steps_data(play):
    """A play's steps as plain data, ready to hand to the court JavaScript."""
    return [{"description": step.description, "diagram": step.diagram} for step in play.steps]


# ---------- Writing (admin pages) ----------


def list_all_plays():
    """Every play, drafts included, most recently changed first."""
    return db.session.scalars(select(Play).order_by(Play.updated_at.desc())).all()


def save_play(clean, author, play=None):
    """Create a play, or replace the contents of an existing one.

    clean is the checked data from validation.validate_play().
    """
    if play is None:
        play = Play(created_by=author.id)
        db.session.add(play)

    play.title = clean["title"]
    play.category = clean["category"]
    play.summary = clean["summary"]
    play.coaching_notes = clean["coaching_notes"]
    play.status = clean["status"]
    play.updated_at = utc_now()
    # Replacing the whole list deletes the old steps (see Play.steps).
    play.steps = [
        PlayStep(step_number=number, description=step["description"], diagram=step["diagram"])
        for number, step in enumerate(clean["steps"], start=1)
    ]
    db.session.commit()
    return play


def set_status(play, status):
    """Publish a play, or move it back to drafts."""
    play.status = status
    play.updated_at = utc_now()
    db.session.commit()


def delete_play(play):
    db.session.delete(play)
    db.session.commit()
