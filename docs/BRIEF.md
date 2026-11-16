# Huddle: build plan for Claude Code

You are helping me (Brian, SUTD basketball captain, Year 2 CS student) turn my Flask project **Huddle** into a proper, well-structured web app. I am still learning, so readable code and a clean project structure matter as much as features.

This brief is saved in the repo at `docs/BRIEF.md`. It is the source of truth for the whole project. Re-read the relevant sections at the start of each phase.

Work in **phases**. Start in plan mode: read the whole repo, then show me your plan for Phase 0 only. After each phase: stop, summarise what you built and why in simple terms (short bullets), list what I should test manually, and wait for me to type "continue" before starting the next phase.

---

## 1. What Huddle is

A private basketball playbook for my club.
- **Admin** (captain/coach): creates player accounts, manages them, and creates/edits plays with an interactive court editor.
- **Player**: logs in with details the admin gave them, then views plays and (later) asks an AI assistant questions about the plays.
- About 20 to 30 users. No public sign-up.

## 2. Current state of the repo

- `main.py`: Flask app with `/` and `/login`, both just render `login.html`. No auth yet.
- `templates/login.html`: styled login page (Player/Coach toggle + shared team password). Keep its visual identity.
- `static/style.css`: design tokens (`--ink`, `--paper`, `--orange`, `--green`, fonts Barlow Condensed + DM Sans).
- `static/images/sutd_team.jpg`: team photo used on the login page.
- `README.md`: Windows PowerShell run steps.
- Git repo with remote `origin` on GitHub, branch `main`.

## 3. Fixed decisions (do not change without asking me)

- **Framework:** stay on Flask with server-rendered Jinja templates. No React, no separate frontend app.
- **Dev machine:** Windows, PowerShell, `.venv`. All README commands must be PowerShell.
- **Roles:** only two: `admin` and `player`.
- **Categories:** exactly 4: Offense, Defense, Sideline, Baseline (labels shown to users have no "SLOB"/"BLOB"). Store as an enum/constant in one place so more can be added later.
- **Play input:** interactive court editor (section 7).
- **Hosting:** must be free (section 9).

## 4. Tech stack

| Purpose | Tool |
|---|---|
| Web framework | Flask (application factory + blueprints) |
| Templates | Jinja2 |
| Database | SQLite locally, PostgreSQL (Neon) in production, chosen by `DATABASE_URL` |
| ORM | Flask-SQLAlchemy (SQLAlchemy 2.x style) |
| Migrations | Flask-Migrate |
| Sessions | Flask-Login |
| Forms + CSRF | Flask-WTF |
| Password hashing | `werkzeug.security` |
| Login rate limiting | Flask-Limiter |
| Config / secrets | `python-dotenv`, `.env` (gitignored) + `.env.example` (committed) |
| Court editor/viewer | Vanilla JavaScript + SVG, no frontend framework |
| AI (Phase 3) | LiteLLM Python SDK, **pinned to an exact version** |
| Tests | pytest |
| Production server | gunicorn (Linux only, used on Render; locally use `flask run`) |

Pin all versions in `requirements.txt`.

## 5. Project structure (target)

```
Huddle/
├── app/
│   ├── __init__.py        # create_app()
│   ├── config.py          # DevConfig (dev + tests), ProdConfig
│   ├── extensions.py      # db, migrate, login_manager, csrf, limiter
│   ├── constants.py       # roles, play categories
│   ├── cli.py             # flask create-admin
│   ├── models/            # user.py, play.py, chat.py
│   ├── auth/              # routes.py, forms.py
│   ├── playbook/          # routes.py
│   ├── admin/             # routes.py, forms.py, decorators.py
│   ├── assistant/         # routes.py, service.py   (Phase 3)
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   ├── auth/  playbook/  admin/  assistant/
│   │   └── errors/        # 403, 404, 500
│   └── static/
│       ├── css/           # tokens.css, base.css, components.css, pages/*.css
│       ├── js/            # court/ (shared renderer), play-viewer.js, play-editor.js
│       ├── icons/         # custom SVG icons
│       └── images/
├── .claude/               # settings.json, skills/ (impeccable)
├── docs/
│   └── BRIEF.md           # this brief
├── migrations/
├── tests/
├── instance/              # local SQLite (gitignored)
├── .env.example
├── requirements.txt
├── run.py
├── CLAUDE.md
├── DESIGN.md
└── README.md
```

## 6. Data model

**users**: id, username (unique, lowercase), password_hash, display_name, role (`admin`/`player`), is_active, must_change_password, created_at, last_login_at

**plays**: id, title, category, summary, coaching_notes, status (`draft`/`published`), created_by (FK users.id), created_at, updated_at

**play_steps**: id, play_id (FK plays.id, cascade delete), step_number, description, diagram (JSON, schema in section 7)

**chat_logs** (Phase 3): id, user_id (FK), question, answer, created_at

Players only ever see `published` plays.

### Account rules
- The first admin is created only by CLI: `flask create-admin` (prompts for username, display name, password).
- Admin creates a player → app generates a random temporary password, shows it **once**, sets `must_change_password=True`.
- On first login, the player must set a new password before seeing anything else.
- Admin can reset a player's password (same temp-password flow) and deactivate/reactivate players. Deactivated users cannot log in. No hard delete of users.
- An admin cannot deactivate themselves.

### Security checklist
- Hash passwords with werkzeug; never log or store raw passwords.
- CSRF on every form and every JSON POST from the editor.
- `@admin_required` decorator for all admin routes; return 403 for players.
- Rate-limit `POST /login` (e.g. 5 per minute per IP).
- Same error message for wrong username and wrong password.
- Session cookie: HttpOnly, SameSite=Lax, Secure in production.
- `SECRET_KEY` from env; refuse to start in production without it.
- Validate editor JSON on the server (schema, coordinate ranges, max sizes).

## 7. Court editor and viewer

Before building, research how existing online basketball play diagram tools work (for example FastDraw by FastModel Sports and other web-based play makers) for **conventions only**. Do not copy their visuals.

**Standard notation to follow:**
- Offensive players: circles numbered 1 to 5
- Defenders (optional toggle per play): X1 to X5
- Ball: shown on the ball handler
- Cut: solid arrow
- Pass: dashed arrow
- Dribble: zigzag arrow
- Screen: line ending in a short perpendicular bar

**Editor (admin, desktop-first):**
- Half-court SVG (structure the code so full court can be added later).
- Drag players/ball to position.
- Draw actions by choosing a tool (cut, pass, dribble, screen) and dragging from a player.
- Steps: add step (copies previous end positions), delete step, reorder steps, text description per step.
- Undo for the last few actions.
- Save as draft or publish.

**Viewer (players, must work well on phones):**
- Prev/Next step buttons + keyboard arrows.
- Optional "Play" button that animates players moving between steps.
- Step description shown under the court.

**Diagram JSON (per step), coordinates normalised 0 to 1 so it scales to any screen:**
```json
{
  "players": [{"id": "O1", "team": "offense", "x": 0.5, "y": 0.8}],
  "ball": {"holder": "O1"},
  "actions": [{"type": "pass", "from": "O1", "to": "O2"},
              {"type": "cut", "player": "O3", "path": [[0.2,0.6],[0.4,0.3]]}]
}
```
You may refine this schema, but document it in `app/static/js/court/README.md` and validate it server-side.

One shared JS module renders the court and diagram; the editor and viewer both use it (no duplicated drawing code).

## 8. UI/UX

**Design skill:** I have installed the **impeccable** skill. Use it for all frontend work:
1. At the start of Phase 0, use it to create `DESIGN.md` from the existing login page (fonts, colors, spacing, tone). The existing look is the source of truth.
2. After building or changing any page, run its audit, fix the issues, then polish.

**Style goals:** clean, minimal, not generic or "AI-looking". No purple gradients, no emoji as icons, no generic stock layouts. Consistent spacing and type scale across all pages. Accessible: WCAG AA contrast, visible focus states, keyboard usable, works from 360px wide.

**Pages and flow:**
1. **Login** (`/login`): keep the current two-panel design with the team photo. Replace the Player/Coach toggle and team password with **username + password** (role comes from the account). Show errors with the existing `form-message` style.
2. **Change password** (`/account/password`): forced on first login.
3. **Main page** (`/playbook`): Huddle logo/wordmark in the header. The 4 categories as **large square cards, 2 per row** (2×2 grid, also 2×2 on phones). Each card: a custom SVG icon centered at the top (offense: attacking arrow or ball; defense: shield; sideline: arrow entering from the side line; baseline: arrow entering from the baseline), then the category name centered below. Show the number of published plays under the name. I suggested light blue for the label text; pick a color that fits the existing palette and passes AA contrast on the background (a darker blue is fine, light blue on the light background is not).
4. **Category page** (`/playbook/<category>`): list of published plays (title, short summary, last updated). Mark plays updated in the last 7 days as "Updated".
5. **Play page** (`/plays/<id>`): court viewer, step description, coaching notes.
6. **Admin area** (`/admin/...`): only visible to admins (link hidden for players, routes return 403). Pages: players list (create, reset password, deactivate/reactivate), plays list (create, edit in court editor, publish/unpublish, delete with confirmation).
7. **Header** on all logged-in pages: wordmark, current user's name, Admin link (admins only), Logout.
8. Error pages for 403, 404, 500 in the same style.

## 9. Hosting (Phase 4)

Must be free and reachable at any time:
- **App:** Render free web service (gunicorn). Free services sleep after 15 minutes without traffic, so add a lightweight `GET /healthz` endpoint (no DB query, no auth) and give me step-by-step instructions to set up a free cron-job.org job that pings it every 10 minutes.
- **Database:** Neon free PostgreSQL via `DATABASE_URL` (Render's free Postgres expires, do not use it).
- Render's filesystem is temporary: nothing user-created may be stored on disk. All play data lives in the database.
- Run migrations on deploy.
- Give me a deploy checklist in README (Render settings, env vars, Neon setup, creating the first admin in production).

## 10. AI assistant (Phase 3)

- Page `/assistant`: chat box for logged-in users.
- `app/assistant/service.py` is the only file that talks to the LLM, via LiteLLM.
- Provider and model come from env (`LLM_MODEL`, plus a fallback model list). Default to Groq's free tier, with Gemini or OpenRouter free models as fallback. Check the providers' current docs for valid model names; do not guess them.
- Context: send the text of all **published** plays (title, category, summary, coaching notes, step descriptions). No RAG/embeddings for now.
- System prompt: answer only from the playbook; if the answer is not in the playbook, say so; never invent plays.
- The assistant is read-only: it can never change data.
- Per-user daily question limit (env, default 20), enforced using `chat_logs`.
- Handle provider errors and timeouts with a friendly message; never show raw errors or API keys.
- API keys only in `.env`.

## 11. Phases

**Phase 0: Restructure (no new features)**
- Create a git branch for this phase.
- Move to the structure in section 5 (app factory, blueprints, config, extensions, static subfolders). Move existing CSS/images into the new folders without losing anything.
- Login page still renders exactly as before.
- Create `CLAUDE.md` (section 12), `DESIGN.md` (via impeccable), `.env.example`, pinned `requirements.txt`.
- Set up pytest with a basic "app starts, login page returns 200" test.
- Update README (Windows PowerShell setup, run, test).

**Phase 1: Accounts and roles**
- Models + first migration, `flask create-admin`, login/logout, forced password change, admin player management, `@admin_required`, security checklist, error pages.
- Tests: login success/fail, deactivated user blocked, player gets 403 on admin routes, forced password change.

**Phase 2: Playbook**
- Main page, category pages, play page with viewer, admin plays list, court editor, draft/publish.
- Tests: players never see drafts, editor JSON validation, play CRUD permissions.

**Phase 3: AI assistant** (section 10)
- Tests with the LLM call mocked.

**Phase 4: Deploy** (section 9)

## 12. CLAUDE.md (create in Phase 0, follow it in every session)

Keep it short (under 200 lines). Only include what you could not work out by reading the code. It must contain at least:
- One-paragraph project summary, the fixed decisions from section 3, and a line pointing to `docs/BRIEF.md` as the full spec.
- Exact commands (PowerShell): set up venv, run the app, run all tests, run one test file, create/apply migrations, create admin.
- Where each kind of file goes (follow section 5). New feature = new blueprint folder.
- Rules: no business logic in templates; routes stay thin, move logic into functions/services; models only in `app/models/`; one CSS file per page in `static/css/pages/`, shared styles in `components.css`, colors/fonts only via tokens in `tokens.css`; no inline styles or inline scripts except tiny bootstraps.
- Naming: snake_case for Python, kebab-case for CSS classes and static file names.
- Every change keeps README and the structure tree in README up to date.
- Run tests before saying a phase is done.
- Commit at the end of each phase with a clear message. Never push or force-push without asking me.

## 13. How to work with me

- Explain your decisions briefly in plain language; I am learning Flask, SQL and JavaScript.
- If something in this brief is unclear or seems wrong, ask me before building.
- Prefer simple, readable code over clever code. Small functions, clear names, short comments where the "why" is not obvious.
- At the end of each phase, re-check the project tree against section 5 and fix anything out of place.
