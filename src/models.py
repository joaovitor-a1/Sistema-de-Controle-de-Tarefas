from . import db # Importa o objeto db de src/__init__.py/ Instância do SQL Alchemy
from sqlalchemy.orm import relationship
from datetime import datetime

# --- MODELO USUÁRIO (Tabela para Login) ---

class Usuario(db.Model):
    __tablename__ = 'usuarios'
#Atributos do usuário (nome e senha)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) #Impede que o mesmo usuário tenha 2 logins
    password_hash = db.Column(db.String(128), nullable=False) #Campo obrigatório/ Armazena apenas o Hash da senha para segurança da mesma
    
    # Relação: 
    tarefas = relationship('Tarefa', backref='usuario', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Usuario {self.username}>'

# --- MODELO TAREFA (Tabela para o Kanban) ---

class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    
    # Status 
    status = db.Column(db.String(20), default='A Fazer', nullable=False)
    
    data_criacao = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
   
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return f'<Tarefa {self.titulo} - Status: {self.status}>'