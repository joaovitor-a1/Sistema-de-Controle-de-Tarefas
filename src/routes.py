from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
# Importa db e migrate definidos em src/__init__.py
from . import db 
from .models import Usuario, Tarefa

# Cria o Blueprint para as rotas da aplicação de tarefas
tarefas_bp = Blueprint('tarefas_bp', __name__)



def is_logged_in():
    """Verifica se o usuário está logado."""
    return 'user_id' in session

# --- ROTAS DE AUTENTICAÇÃO ---

@tarefas_bp.route("/register", methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('tarefas_bp.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

       
        user = Usuario.query.filter_by(username=username).first()
        if user:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
        else:
          
            hashed_password = generate_password_hash(password, method='scrypt')
            
         
            novo_usuario = Usuario(username=username, password_hash=hashed_password)
            db.session.add(novo_usuario)
            db.session.commit()
            
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('tarefas_bp.login'))

    return render_template("register.html")

@tarefas_bp.route("/", methods=['GET', 'POST'])
@tarefas_bp.route("/login", methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('tarefas_bp.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        
        # Verificação de usuário e senha
        if user and check_password_hash(user.password_hash, password):
           
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('tarefas_bp.dashboard'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
            
    return render_template("login.html")

@tarefas_bp.route("/logout")
def logout():
    session.clear() 
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('tarefas_bp.login'))



@tarefas_bp.route("/dashboard")
def dashboard():
    if not is_logged_in():
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('tarefas_bp.login'))

    
    user_id = session['user_id']
    tarefas = Tarefa.query.filter_by(user_id=user_id).order_by(Tarefa.data_criacao.desc()).all()
    
    return render_template("dashboard.html", tarefas=tarefas)

@tarefas_bp.route("/nova_tarefa", methods=['GET', 'POST'])
def nova_tarefa():
    if not is_logged_in():
        flash('Você precisa estar logado para criar tarefas.', 'warning')
        return redirect(url_for('tarefas_bp.login'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        status = request.form.get('status', 'A Fazer') 
        user_id = session['user_id']
        
        
        nova = Tarefa(
            titulo=titulo,
            descricao=descricao,
            status=status,
            data_criacao=datetime.now(),
            user_id=user_id
        )
        db.session.add(nova)
        db.session.commit()
        
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('tarefas_bp.dashboard'))

    return render_template("nova_tarefa.html")

@tarefas_bp.route("/editar_tarefa/<int:tarefa_id>", methods=['GET', 'POST'])
def editar_tarefa(tarefa_id):
    if not is_logged_in():
        flash('Você precisa estar logado para editar tarefas.', 'warning')
        return redirect(url_for('tarefas_bp.login'))

    
    tarefa = Tarefa.query.filter_by(id=tarefa_id, user_id=session['user_id']).first()
    
    if not tarefa:
        flash('Tarefa não encontrada ou você não tem permissão para editá-la.', 'danger')
        return redirect(url_for('tarefas_bp.dashboard'))
        
    if request.method == 'POST':
        tarefa.titulo = request.form.get('titulo')
        tarefa.descricao = request.form.get('descricao')
        tarefa.status = request.form.get('status')
        
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('tarefas_bp.dashboard'))

    return render_template("editar_tarefa.html", tarefa=tarefa)

@tarefas_bp.route("/excluir_tarefa/<int:tarefa_id>", methods=['POST'])
def excluir_tarefa(tarefa_id):
    if not is_logged_in():
        flash('Você precisa estar logado para excluir tarefas.', 'warning')
        return redirect(url_for('tarefas_bp.login'))

   
    tarefa = Tarefa.query.filter_by(id=tarefa_id, user_id=session['user_id']).first()
    
    if not tarefa:
        flash('Tarefa não encontrada ou você não tem permissão para excluí-la.', 'danger')
        return redirect(url_for('tarefas_bp.dashboard'))
        
    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa excluída com sucesso!', 'success')
    return redirect(url_for('tarefas_bp.dashboard'))