# Huddle

Huddle is a Flask-based playbook project for SUTD Basketball. The current version is an early login-page preview; authentication, play storage, and play browsing are not implemented yet.

## Run Locally on Windows

Open PowerShell in the project folder (`Huddle`). Create the virtual environment once:

```powershell
py -m venv .venv
```

Activate it and install Flask:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install Flask
```

Start the local development server:

```powershell
python -m flask --app main run --debug
```

Open <http://127.0.0.1:5000> in your browser. Leave the PowerShell terminal running while you use the site. Press `Ctrl+C` in that terminal to stop the server.

If the virtual environment already exists, do not recreate it; activate it and start Flask. If activation is unavailable, run commands through the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install Flask
.\.venv\Scripts\python.exe -m flask --app main run --debug
```


