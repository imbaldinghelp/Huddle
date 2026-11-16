# Huddle

Huddle is a private basketball playbook for SUTD Basketball, built with Flask.

**Status:** Phase 1 (accounts and roles) is done. Admins can log in, add players, reset passwords and deactivate accounts. Players can log in and must set their own password the first time. Plays and the court editor arrive in Phase 2. The full plan is in [docs/BRIEF.md](docs/BRIEF.md).

## Set up from scratch

Follow the section for your computer, top to bottom. Each step says what you should see when it works. Commands go in a terminal: **PowerShell** on Windows, **Terminal** on Mac.

### Windows (PowerShell)

**1. Install the tools (once).**

- Python 3.11 or newer from <https://www.python.org/downloads/>. In the installer, tick **Add python.exe to PATH**.
- Git from <https://git-scm.com/download/win>.

Open a new PowerShell window and check both are installed:

```powershell
py --version
git --version
```

You should see two version numbers, for example `Python 3.12.4`. If a command is "not recognized", close PowerShell, open it again, and retry; if it still fails, reinstall and tick the PATH box.

**2. Get the code and open the project folder.**

```powershell
git clone <your-repository-url> Huddle
cd Huddle
```

If you already have the folder, just `cd` into it. Every command below is run inside this folder.

**3. Create the virtual environment (once).** This is a private copy of Python for Huddle, so its packages do not mix with other projects.

```powershell
py -m venv .venv
```

**4. Activate it (every time you open a new PowerShell window).**

```powershell
.\.venv\Scripts\Activate.ps1
```

Your prompt now starts with `(.venv)`. If PowerShell says "running scripts is disabled", run this once, answer `Y`, then repeat the activate command:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**5. Install the packages.**

```powershell
python -m pip install -r requirements.txt
```

**6. Create your settings file.**

```powershell
Copy-Item .env.example .env
```

The defaults work as they are. `.env` is private and gitignored: never commit it.

**7. Create the database.**

```powershell
flask db upgrade
```

You should see lines ending in `Running upgrade -> ...`, and a new file `instance\huddle.db`.

**8. Create your admin account.**

```powershell
flask create-admin
```

It asks for a username, a display name and a password (typing is hidden; you type the password twice). Passwords need at least 8 characters. You should see `Admin '...' created.`

**9. Start Huddle.**

```powershell
flask run
```

Open <http://127.0.0.1:5000> in your browser and log in with the admin account. Press `Ctrl+C` in PowerShell to stop the server.

**10. Check everything works (optional).**

```powershell
python -m pytest
```

You should see `65 passed`.

### Mac (Terminal)

**1. Install the tools (once).** Open Terminal (press Cmd+Space, type "Terminal").

- Git and the Apple developer tools: run `xcode-select --install` and follow the pop-up. If it says they are already installed, carry on.
- Python 3.11 or newer: install from <https://www.python.org/downloads/>, or with Homebrew (<https://brew.sh>) run `brew install python@3.12`.

Check both:

```bash
python3 --version
git --version
```

You should see two version numbers, and the Python one should be 3.11 or higher. Mac's built-in Python 3.9 is too old.

**2. Get the code and open the project folder.**

```bash
git clone <your-repository-url> Huddle
cd Huddle
```

If you already have the folder, just `cd` into it. Every command below is run inside this folder.

**3. Create the virtual environment (once).** This is a private copy of Python for Huddle, so its packages do not mix with other projects. If `python3` is still older than 3.11 after installing, use the full name instead, for example `python3.12 -m venv .venv`.

```bash
python3 -m venv .venv
```

**4. Activate it (every time you open a new Terminal window).**

```bash
source .venv/bin/activate
```

Your prompt now starts with `(.venv)`.

**5. Install the packages.**

```bash
python -m pip install -r requirements.txt
```

**6. Create your settings file.**

```bash
cp .env.example .env
```

The defaults work as they are. `.env` is private and gitignored: never commit it.

**7. Create the database.**

```bash
flask db upgrade
```

You should see lines ending in `Running upgrade -> ...`, and a new file `instance/huddle.db`.

**8. Create your admin account.**

```bash
flask create-admin
```

It asks for a username, a display name and a password (typing is hidden; you type the password twice). Passwords need at least 8 characters. You should see `Admin '...' created.`

**9. Start Huddle.**

```bash
flask run --port 5001
```

Open <http://127.0.0.1:5001> in your browser and log in with the admin account. Press `Ctrl+C` in Terminal to stop the server.

Mac note: port 5000 is taken by AirPlay Receiver on recent macOS, which is why the command above uses 5001. (Alternatively, turn off AirPlay Receiver in System Settings > General > AirDrop & Handoff and use plain `flask run`.)

**10. Check everything works (optional).**

```bash
python -m pytest
```

You should see `65 passed`.

### If something goes wrong

| What you see | What to do |
|---|---|
| `flask` or `pytest` "not recognized" / "command not found" | The virtual environment is not active. Run the activate step again (step 4); the prompt must start with `(.venv)`. |
| `No such table: users` when you log in or create an admin | The database is missing. Run `flask db upgrade`. |
| `Address already in use` | Another program uses that port. Add a different one, for example `flask run --port 5002`. |
| `ModuleNotFoundError` | Packages are missing. Run `python -m pip install -r requirements.txt` with the environment active. |
| Forgot your admin password | Run `flask create-admin` again with a new username, then reset the old admin's password from the Admin page. |

## Every day after that

Open a terminal in the `Huddle` folder, then:

| Step | Windows (PowerShell) | Mac (Terminal) |
|---|---|---|
| Activate | `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| Start | `flask run` | `flask run --port 5001` |
| Stop | `Ctrl+C` | `Ctrl+C` |
| Leave the environment | `deactivate` | `deactivate` |

If PowerShell refuses to activate, you can skip activation and run `.\.venv\Scripts\python.exe -m flask run` instead.

## After pulling new code

With the environment active:

```bash
python -m pip install -r requirements.txt
flask db upgrade
```

These commands are the same on Windows and Mac.

## Accounts

- **Add a player:** log in as an admin, open **Admin**, choose **Add player**. Huddle shows a temporary password once; send it to the player. They must choose their own password at first login.
- **Forgotten password:** an admin opens **Admin** and chooses **Reset password** for that person. This gives a new temporary password.
- **Someone leaves the team:** choose **Deactivate**. They can no longer log in, and can be reactivated later. Accounts are never deleted.
- **Change your own password:** click your name in the header.
- Logging in is limited to 5 attempts per minute from one address.

## Test

With the environment active (same commands on Windows and Mac):

```bash
python -m pytest                      # all tests
python -m pytest tests/test_auth.py   # one file
```

Tests use their own empty in-memory database, so they never touch `instance/huddle.db`.

## Database changes

After you change a model in `app/models/`, create a migration and apply it:

```bash
flask db migrate -m "describe the change"
flask db upgrade
```

Commit the new file in `migrations/versions/` together with the model change.

## Project structure

```
Huddle/
├── app/
│   ├── __init__.py          # create_app(): builds the Flask app
│   ├── config.py            # DevConfig (dev + tests), ProdConfig
│   ├── extensions.py        # db, migrate, login_manager, csrf, limiter
│   ├── constants.py         # roles, play categories
│   ├── cli.py               # flask create-admin
│   ├── errors.py            # 400, 403, 404, 429, 500 handlers
│   ├── models/
│   │   └── user.py          # users table
│   ├── auth/                # login, logout, change password
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── service.py       # account rules (check login, create user, passwords)
│   │   └── hooks.py         # runs on every request: load user, force password change
│   ├── admin/               # admin-only pages
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── service.py       # create player, reset password, deactivate
│   │   └── decorators.py    # @admin_required
│   ├── playbook/            # player pages (placeholder until Phase 2)
│   │   └── routes.py
│   ├── templates/
│   │   ├── base.html        # bare page skeleton
│   │   ├── shell.html       # logged-in layout: header + content
│   │   ├── components/      # site_header, flash_messages, forms (field macro)
│   │   ├── auth/            # login, change_password
│   │   ├── admin/           # players, new_player, player_credentials
│   │   ├── playbook/        # index
│   │   └── errors/          # layout, 400, 403, 404, 500
│   └── static/
│       ├── css/
│       │   ├── tokens.css       # colours and fonts
│       │   ├── base.css         # resets and defaults
│       │   ├── components.css   # shared pieces (fields, buttons, header...)
│       │   └── pages/           # login.css, admin.css, error.css
│       ├── js/
│       │   ├── password-toggle.js
│       │   └── confirm-submit.js
│       └── images/
│           └── sutd_team.jpg
├── migrations/              # database migrations (Flask-Migrate)
├── instance/                # local SQLite database (gitignored)
├── tests/
│   ├── conftest.py          # shared test fixtures
│   ├── test_app.py          # app starts, static files, error page
│   ├── test_auth.py         # login, logout, deactivated users
│   ├── test_password_change.py
│   ├── test_admin.py        # admin pages and permissions
│   ├── test_security.py     # CSRF and rate limiting
│   └── test_cli.py          # flask create-admin
├── .claude/                 # Claude Code settings and the impeccable skill
├── .impeccable/             # design data used by the impeccable skill
├── docs/
│   └── BRIEF.md             # full project spec
├── .env.example             # template for your local .env
├── .flaskenv                # tells `flask run` where the app is
├── requirements.txt         # pinned package versions
├── run.py                   # entry point
├── CLAUDE.md                # rules for Claude Code sessions
├── DESIGN.md                # visual design system
└── README.md
```

Each blueprint folder also has an `__init__.py` that creates the blueprint. More folders (`assistant/`, `static/icons/`) are added in the phase that first needs them.
