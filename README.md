# ai_app
Using AI to create a flask app.

## Flask app

Run the development server:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser.

Login page:

```text
http://localhost:5000/login
```

Initialize the SQLite database (creates `users.db` with sample users `alice`/`password1` and `bob`/`password2`):

```bash
python init_db.py
```

# Capability

Some detains on what it does here.
