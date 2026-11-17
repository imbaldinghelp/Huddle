# Huddle

Huddle is a private basketball playbook for SUTD Basketball, built with Flask.

**Status:** Phase 3 (AI assistant) is done. Admins manage player accounts and build plays in the court editor, as drafts or published. Players log in, browse the four categories, step through each published play and chat with the assistant about it. Deployment arrives in Phase 4. The full plan is in [docs/BRIEF.md](docs/BRIEF.md).

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

The defaults work as they are, except the assistant: it needs a free API key in `.env` before it can answer (see [Assistant](#assistant)). Everything else runs without one. `.env` is private and gitignored: never commit it.

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

You should see `211 passed`.

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

The defaults work as they are, except the assistant: it needs a free API key in `.env` before it can answer (see [Assistant](#assistant)). Everything else runs without one. `.env` is private and gitignored: never commit it.

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

You should see `211 passed`.

### If something goes wrong

| What you see | What to do |
|---|---|
| `flask` or `pytest` "not recognized" / "command not found" | The virtual environment is not active. Run the activate step again (step 4); the prompt must start with `(.venv)`. |
| `No such table: users` (or `plays`) | The database is missing or out of date. Run `flask db upgrade`. |
| The court does not appear on a play page or in the editor | Do a hard refresh (Ctrl+F5, or Cmd+Shift+R on Mac) so the browser loads the newest JavaScript. |
| `Address already in use` | Another program uses that port. Add a different one, for example `flask run --port 5002`. |
| `ModuleNotFoundError` | Packages are missing. Run `python -m pip install -r requirements.txt` with the environment active. |
| Forgot your admin password | Run `flask create-admin` again with a new username, then reset the old admin's password from the Admin page. |
| The assistant says it "could not answer just now" | Look at the terminal running Huddle for lines starting `Assistant:`. There is one for each model that failed, with the reason. `AuthenticationError`, `Missing ... API key` or `Illegal header value` means the key in `.env` is missing, empty or wrong (restart Huddle after editing `.env`). `RateLimitError` means the free limit is used up for now. `NotFoundError` means the model name is wrong or retired. |
| The `Assistant:` line says `CERTIFICATE_VERIFY_FAILED` | Your network (often a work or school one) inspects secure connections with its own certificate, which Python does not know. Add `SSL_CERT_FILE=<path to that network's CA .pem file>` to `.env` and restart. Do not turn certificate checks off. |
| `No such table: chat_logs` (or `plays`) | Run `flask db upgrade`. |

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

- **Add a player:** log in as an admin, open **Admin** and choose **Add player**. Huddle shows a temporary password once; send it to the player. They must choose their own password at first login.
- **Forgotten password:** an admin opens **Admin** and chooses **Reset password** for that person. This gives a new temporary password.
- **Someone leaves the team:** choose **Deactivate**. They can no longer log in, and can be reactivated later. Accounts are never deleted.
- **Change your own password:** click your name in the header.
- Logging in is limited to 5 attempts per minute from one address.

## Plays

Players open the **Playbook**, pick one of the four categories (Offense, Defense, Sideline, Baseline), then a play. On the play page they step through the diagram with **Previous** and **Next** (or the left and right arrow keys), or press **Play** to watch the players move.

Admins create and manage plays:

- **Create a play:** open a category in the Playbook, such as **Offense**, and choose **New play** at the top right. The editor opens with that category already chosen. **Admin > New play** does the same without a category. Fill in the title, then build the diagram in the court editor.
- **Find your drafts:** admins see drafts in the category lists, marked **Draft**. Players never see them. **Admin > Plays** lists every play in one place.
- **Court editor tools:** **Move** drags players (and the ball, onto another player). **Cut**, **Dribble** and **Screen** are drawn by dragging from a player. **Pass** is dragged from the player with the ball to a teammate. **Erase** removes an arrow you click. **Undo** (or Ctrl+Z) steps back.
- **Steps:** **Add step** starts a new step with everyone where the last one left them. Steps can be moved up, moved down and removed, and each has its own description.
- **Draft or published:** **Save as draft** keeps a play hidden from players. **Save and publish** makes it visible. You can also publish, unpublish and delete from the plays list.
- **Reading a diagram:** solid arrow = cut, dashed arrow = pass, zigzag arrow = dribble, line ending in a bar = screen, orange dot = the ball, X1 to X5 = defenders.

The diagram format is documented in [app/static/js/court/README.md](app/static/js/court/README.md).

## Assistant

Every published play has an **Ask about this play** chat next to the diagram (under it on a phone). Type a question and press Enter, or tap one of the ready-made questions, for example "Walk me through this play."

- **What it knows:** the text of every published play (title, category, summary, coaching notes and step descriptions), and which play you are looking at, so "this play" and "it" work. Drafts are never sent, and a draft has no chat. It does not see the diagrams, so write what happens in each step's description.
- **Follow-up questions:** it remembers the last few messages of today's chat about that play, so you can ask "and what happens after that?". Each play has its own chat, and a chat starts fresh each day.
- **What it does not do:** it is told to answer only from the playbook and to say so when the answer is not there. It cannot change anything in Huddle.
- **Daily limit:** each person gets 20 questions a day in total, across all plays (`ASSISTANT_DAILY_LIMIT`). The count starts again at midnight Singapore time. Only answered questions count.
- **What is saved:** each question and its answer, with the play it was about, in the `chat_logs` table. Only you see your own chats.

**Set it up (once).** The assistant uses a free AI model through the [LiteLLM](https://docs.litellm.ai/) package.

1. Create a free API key at <https://console.groq.com/keys>.
2. Open `.env` and add the key (if your `.env` is older than this feature, copy the "AI assistant" lines from `.env.example` first):

   ```
   GROQ_API_KEY=your-key-here
   ```

3. Optional but recommended: add a second free key from <https://aistudio.google.com/apikey> as `GEMINI_API_KEY`. Huddle switches to Gemini when Groq fails or is over its free limit.
4. Restart Huddle.

The models are chosen in `.env` too: `LLM_MODEL` is tried first, then each model in `LLM_FALLBACK_MODELS` (comma-separated). Names are written `<provider>/<model>`. Left unset, Huddle uses `groq/llama-3.3-70b-versatile`, then `gemini/gemini-3.5-flash-lite`. Providers retire models from time to time: if the assistant stops answering, check the provider's models page and update the name.

The whole playbook is sent with every question. Free plans cap how much text can be sent per minute, so if the playbook grows large and Groq starts refusing, put the Gemini model first in `LLM_MODEL`.

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
│   │   ├── user.py          # users table
│   │   ├── play.py          # plays and play_steps tables
│   │   └── chat.py          # chat_logs table (assistant questions and answers)
│   ├── auth/                # login, logout, change password
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── service.py       # account rules (check login, create user, passwords)
│   │   └── hooks.py         # runs on every request: load user, force password change
│   ├── admin/               # admin-only pages: overview, players, plays, court editor
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── service.py       # create player, reset password, deactivate, counts
│   │   └── decorators.py    # @admin_required
│   ├── playbook/            # player pages: categories, play lists, play viewer
│   │   ├── routes.py
│   │   ├── service.py       # play rules (find, save, publish, delete)
│   │   └── validation.py    # checks a play sent by the court editor
│   ├── assistant/           # the chat about a play
│   │   ├── routes.py        # receives a question from the play page, returns the answer
│   │   └── service.py       # daily limit, memory, prompt, and the only code that calls the LLM
│   ├── templates/
│   │   ├── base.html        # bare page skeleton
│   │   ├── shell.html       # logged-in layout: header + content
│   │   ├── components/      # site_header, breadcrumbs, flash_messages, forms, admin_tabs, text, play_chat
│   │   ├── auth/            # login, change_password
│   │   ├── admin/           # index (overview), players, new_player, player_credentials, plays, play_editor
│   │   ├── playbook/        # index, category, play
│   │   └── errors/          # layout, 400, 403, 404, 500
│   └── static/
│       ├── css/
│       │   ├── tokens.css       # colours and fonts
│       │   ├── base.css         # resets and defaults
│       │   ├── components.css   # shared pieces (fields, buttons, header, court...)
│       │   └── pages/           # login, admin, error, playbook, play, play-editor
│       ├── js/
│       │   ├── court/           # shared court drawing (see its README.md)
│       │   │   ├── court.js     # court lines
│       │   │   ├── render.js    # players, ball and arrows
│       │   │   ├── model.js     # questions and changes about a diagram
│       │   │   ├── animate.js   # positions part-way through a step
│       │   │   ├── geometry.js  # line maths
│       │   │   ├── svg.js       # SVG helpers
│       │   │   └── README.md    # the diagram format
│       │   ├── play-viewer.js   # play page: steps, arrow keys, Play button
│       │   ├── play-editor.js   # court editor: tools, steps, undo, save
│       │   ├── play-chat.js     # play page: the chat with the assistant
│       │   ├── password-toggle.js
│       │   └── confirm-submit.js
│       ├── icons/               # custom SVG icons (categories, drawing tools)
│       └── images/
│           └── sutd_team.jpg
├── migrations/              # database migrations (Flask-Migrate)
├── instance/                # local SQLite database (gitignored)
├── tests/
│   ├── conftest.py          # shared test fixtures and sample play data
│   ├── test_app.py          # app starts, static files, error page
│   ├── test_auth.py         # login, logout, deactivated users
│   ├── test_password_change.py
│   ├── test_admin.py        # admin pages and permissions
│   ├── test_admin_plays.py  # creating, editing, publishing, deleting plays
│   ├── test_playbook.py     # what players see; drafts stay hidden
│   ├── test_play_validation.py  # checks on court editor data
│   ├── test_assistant.py    # the chat: asking, memory, daily limit, errors (the LLM is faked)
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

Each blueprint folder also has an `__init__.py` that creates the blueprint.
