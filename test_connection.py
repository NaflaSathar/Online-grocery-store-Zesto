from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # <-- import this
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

try:
    with app.app_context():
        # Use text() to wrap raw SQL
        result = db.session.execute(text('SELECT 1'))
        print("✅ Database connection successful.")
except Exception as e:
    print("❌ Database connection failed:", e)
