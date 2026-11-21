# Huddle

Huddle is a private basketball playbook for SUTD Basketball (about 20 to 30 users, no public sign-up). Admins (captain/coach) create player accounts and build plays in an interactive court editor; players log in to view published plays and, later, ask an AI assistant about them. The owner, Brian, is learning Flask, SQL and JavaScript, so readable code and a clean structure matter as much as features.

**Full spec: `docs/BRIEF.md`.** It is the source of truth. Re-read the relevant sections at the start of each phase. Visual rules: `DESIGN.md`.

## Fixed decisions (ask before changing)

- Flask with server-rendered Jinja templates. No React, no separate frontend app.
- Dev machine is Windows + PowerShell + `.venv`; Brian also uses a Mac. README gives both: PowerShell and Mac Terminal (zsh) steps. Commands below are PowerShell; on Mac use `source .venv/bin/activate`, `python3`, `cp`, and `flask run --port 5001` (port 5000 is taken by AirPlay).
- Two roles only: `admin` and `player`.
- Four play categories: Offense, Defense, Sideline, Baseline (shown to users without "SLOB"/"BLOB"), defined once in `app/constants.py`.
- Plays are entered with the interactive court editor (vanilla JS + SVG).
- Hosting must be free: Render web service + Neon PostgreSQL. Nothing user-created is stored on disk.
- The env template is `.env.example`. Packages are added to `requirements.txt` in the phase that first uses them, pinned to exact versions.
- Two configs only: `DevConfig` (development and tests) and `ProdConfig`. Tests pass their own settings through `create_app("development", overrides)`.

## Commands (PowerShell)

```powershell
# Set up (once)
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env

# Run the app (http://127.0.0.1:5000)
flask run

# Tests
python -m pytest                      # all tests
python -m pytest tests/test_app.py    # one file

# Database
flask db upgrade                            # apply migrations (also after every pull)
flask db migrate -m "describe the change"   # create a migration after changing a model
flask create-admin                          # create an admin account
```

`flask run` finds the app through `.flaskenv` (`FLASK_APP=run`).

## Where files go

Follow the tree in `docs/BRIEF.md` section 5. A folder is created in the phase that first needs it.

- `app/__init__.py`: `create_app()` only. `app/config.py`: settings. `app/extensions.py`: extension objects. `app/constants.py`: roles and categories. `app/errors.py`: error pages. `app/cli.py`: `flask` commands.
- A new feature is a new blueprint folder: `app/<feature>/` with `__init__.py`, `routes.py`, and `forms.py` / `service.py` when needed. Register it in `register_blueprints()`.
- Logic lives in `service.py` (for example `app/auth/service.py`, `app/admin/service.py`); routes call it.
- Models: `app/models/` only, one file per table group.
- Templates: `app/templates/<blueprint>/`. Shared partials and macros in `app/templates/components/`. Logged-in pages extend `shell.html` (header + content); pages without the header (login, errors) extend `base.html`.
- CSS: `app/static/css/`. JS: `app/static/js/`. Icons: `app/static/icons/`. Images: `app/static/images/`.
- Tests: `tests/`, shared fixtures in `tests/conftest.py`.

## Rules

- No business logic in templates.
- Routes stay thin: read the request, call a function or service, return a response.
- Every admin route uses `@admin_required` (`app/admin/decorators.py`). Every form, including one-button action forms, carries a CSRF token.
- Never store, log or flash a raw password. Temporary passwords are rendered once, straight into the response.
- After changing a model, create a migration and commit it with the change. Never edit or replace a migration that already exists: add a new one.
- The court diagram JSON is documented in `app/static/js/court/README.md` and checked on the server in `app/playbook/validation.py`. Change the format in all four places together: README, validation (with its tests), the JS, and `app/assistant/court_text.py` (which describes diagrams to the assistant).
- All court drawing goes through `app/static/js/court/`; the viewer and editor never draw on their own.
- The assistant is a chat on the play page (`components/play_chat.html` + `static/js/play-chat.js`). Questions go as JSON to `POST /plays/<id>/ask` in `app/assistant/routes.py`. `app/assistant/service.py` is the only file that talks to the LLM, through LiteLLM. Models and the daily limit come from env (`LLM_MODEL`, `LLM_FALLBACK_MODELS`, `ASSISTANT_DAILY_LIMIT`). Only published plays are sent, plus the last few messages of today's chat about that play. Tests replace `service.call_llm` with a fake and never call a real model.
- CSS: one file per page in `static/css/pages/`; shared styles in `components.css`; colours and fonts only through tokens in `tokens.css`.
- No inline styles and no inline scripts, except tiny bootstraps.
- Link static files with `url_for('static', ...)` and routes with `url_for('<blueprint>.<view>')`.
- Naming: snake_case for Python; kebab-case for CSS classes and static file names.
- Prefer simple, readable code: small functions, clear names, short comments only where the "why" is not obvious.
- Frontend work uses the impeccable skill: after building or changing a page, run its audit, fix the issues, then polish.
- Every change keeps README, and the structure tree inside it, up to date.

## Working in phases

- Phases are listed in `docs/BRIEF.md` section 11.
- Run the tests before saying a phase is done.
- At the end of a phase: check the project tree against section 5, summarise what was built and why in short bullets, list what to test manually, then wait for "continue".
- Git belongs to Brian. Do not stage, commit, branch or push; leave changes in the working tree for him. (This replaces the brief's "commit at the end of each phase".) Read-only git commands are fine.
- If the brief is unclear or seems wrong, ask before building.

## Future improvements (Brian's wishlist, not yet scheduled)

Do these only when asked, or fold them into a phase when Brian says so. Mention them when a related page is touched.

- More UI/UX polish as Brian spots things. Done on 2026-11-17: chat-style assistant, "New play" on category pages, admin overview page, breadcrumbs, new Sideline and Baseline icons. Done on 2026-11-21: redrawn Sideline icon, bigger category cards, coaching notes removed (step descriptions cover them), growing Summary box, arrow buttons that slide steps, publishing lands on the play's category page, plays managed from each category's Edit page (Admin is players only).
- Assistant chat, next steps: a "New chat" button to clear the conversation (today it resets each day), a quick way to reach the chat on phones (it sits below the court and step text), and rendering simple formatting such as lists in replies (replies are plain text today).
- Keyboard-only drawing in the court editor (the court is mouse/touch only today).
