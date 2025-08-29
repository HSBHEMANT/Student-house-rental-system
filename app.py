import os
import logging
import json
from flask import Flask
from extensions import db, login_manager
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///housedatabase.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

# ✅ Add upload config
app.config['UPLOAD_FOLDER'] = os.path.join("static", "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ✅ Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # <<<< IMPORTANT
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@app.template_filter('fromjson')
def fromjson_filter(value):
    try:
        return json.loads(value)
    except Exception:
        return []

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    import models
    db.create_all()
    from routes import register_routes
    register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
