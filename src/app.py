

from flask import Flask
from datetime import timedelta
import os 

# -----------------------------------------------------------------------
# IMPORTAÇÕES ESSENCIAIS DO PACOTE SRC
# -----------------------------------------------------------------------
from . import db, migrate 
from .routes import tarefas_bp as main_blueprint
from .models import Usuario, Tarefa

def create_app():
   
    basedir = os.path.abspath(os.path.dirname(__file__)) 

    
    app = Flask(
        __name__, 
        instance_relative_config=True,
        template_folder=os.path.join(basedir, 'templates') # <--- CORREÇÃO AQUI
    ) 
    
    
    # CONFIGURAÇÕES
    # ----------------------------------------------------
    app.config["SECRET_KEY"] = "sua_chave_secreta_aqui" 
    
    # Configuração do DB: Usa o caminho dentro da pasta 'instance'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "tarefas.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.permanent_session_lifetime = timedelta(minutes=40)

   
    db.init_app(app) 
    migrate.init_app(app, db) 

    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ----------------------------------------------------
    # REGISTRO DAS ROTAS
    # ----------------------------------------------------
    app.register_blueprint(main_blueprint)

    return app