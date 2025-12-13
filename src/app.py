from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "chave_segura"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.permanent_session_lifetime = timedelta(minutes=40)

    db.init_app(app)
    migrate.init_app(app, db)

    # Importação do Blueprint DEPOIS que o db foi inicializado
    from src.routes import tarefas_bp
    app.register_blueprint(tarefas_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)