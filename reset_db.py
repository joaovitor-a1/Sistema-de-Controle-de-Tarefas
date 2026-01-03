import os
from src.app import create_app
from src import db

app = create_app()
with app.app_context():
    # Cria a pasta instance se ela não existir
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
        print("Pasta instance criada!")
    
    db.drop_all()
    db.create_all()
    print(f"Banco criado com sucesso em: {os.path.join(app.instance_path, 'tarefas.db')}")