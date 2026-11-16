# Huddle

Huddle is a private basketball playbook for SUTD Basketball, built with Flask.

**Status:** Phase 0 (restructure) is done. The app shows the login page only; accounts, plays and the court editor arrive in later phases. The full plan is in [docs/BRIEF.md](docs/BRIEF.md).

## Set up on Windows (once)

You need Python 3.12 or newer. Open PowerShell in the project folder (`Huddle`):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` holds your local settings and secrets. It is gitignored: never commit it. The defaults work for local development without editing anything.

## Run

Activate the virtual environment (your prompt shows `(.venv)` when it is active), then start the development server:

```powershell
.\.venv\Scripts\Activate.ps1
flask run
```

Open <http://127.0.0.1:5000> in your browser. Press `Ctrl+C` in the terminal to stop the server, and type `deactivate` to leave the virtual environment.

If PowerShell refuses to run `Activate.ps1`, call the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m flask run
```

## Test

```powershell
python -m pytest                      # all tests
python -m pytest tests/test_app.py    # one file
```

## Project structure

```
Huddle/
├── app/
│   ├── __init__.py          # create_app(): builds the Flask app
│   ├── config.py            # DevConfig (dev + tests), ProdConfig
│   ├── constants.py         # roles, play categories
│   ├── auth/                # login page routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── templates/
│   │   ├── base.html        # shared page skeleton
│   │   └── auth/
│   │       └── login.html
│   └── static/
│       ├── css/
│       │   ├── tokens.css       # colours and fonts
│       │   ├── base.css         # resets and defaults
│       │   ├── components.css   # shared pieces
│       │   └── pages/
│       │       └── login.css
│       ├── js/
│       │   └── password-toggle.js
│       └── images/
│           └── sutd_team.jpg
├── .claude/                 # Claude Code settings and the impeccable skill
├── .impeccable/             # design data used by the impeccable skill
├── docs/
│   └── BRIEF.md             # full project spec
├── tests/
│   ├── conftest.py          # shared test fixtures
│   └── test_app.py
├── .env.example             # template for your local .env
├── .flaskenv                # tells `flask run` where the app is
├── requirements.txt         # pinned package versions
├── run.py                   # entry point
├── CLAUDE.md                # rules for Claude Code sessions
├── DESIGN.md                # visual design system
└── README.md
```

More folders (`models/`, `playbook/`, `admin/`, `assistant/`, `migrations/`) are added in the phase that first needs them.
