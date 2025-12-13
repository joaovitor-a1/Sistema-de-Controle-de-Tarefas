from flask import Blueprint, render_template, request, redirect, url_for, flash, session
# 🚨 CORREÇÃO: Importa a instância 'db' de src.app
from src.app import db
# 🚨 CORREÇÃO: Importa as classes de modelo de src.models
from src.models import User, Tarefa
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

tarefas_bp = Blueprint("tarefas_bp", __name__)

STATUS_VALIDOS = ["A Fazer", "Em Progresso", "Concluída"]
PRIORIDADES = ["Baixa", "Média", "Alta", "Crítica"]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for("tarefas_bp.login"))
        return f(*args, **kwargs)
    return decorated_function

# Rota de Login
@tarefas_bp.route("/", methods=["GET", "POST"])
# ... (código da rota login) ...
def login():
    if "user_id" in session:
        return redirect(url_for("tarefas_bp.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Login bem-sucedido. Bem-vindo(a), {user.username}!", "success")
            return redirect(url_for("tarefas_bp.dashboard"))

        flash("Usuário ou senha incorretos!", "danger")

    return render_template("login.html")

# Rota de Logout
@tarefas_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("tarefas_bp.login"))

# Rota do Dashboard (Quadro Kanban)
@tarefas_bp.route("/dashboard")
@login_required
def dashboard():
    # Consulta as tarefas do usuário logado e as organiza por colunas (status)
    tarefas_a_fazer = Tarefa.query.filter_by(
        usuario_id=session["user_id"], status="A Fazer"
    ).order_by(Tarefa.prioridade.desc()).all()
    
    tarefas_progresso = Tarefa.query.filter_by(
        usuario_id=session["user_id"], status="Em Progresso"
    ).order_by(Tarefa.prioridade.desc()).all()

    tarefas_concluidas = Tarefa.query.filter_by(
        usuario_id=session["user_id"], status="Concluída"
    ).order_by(Tarefa.criado_em.desc()).all()

    return render_template(
        "dashboard.html",
        a_fazer=tarefas_a_fazer,
        progresso=tarefas_progresso,
        concluidas=tarefas_concluidas,
        username=session["username"],
    )

# Rota para Criar Nova Tarefa
@tarefas_bp.route("/tarefa/nova", methods=["GET", "POST"])
@login_required
def nova_tarefa():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        prioridade = request.form.get("prioridade")

        if not titulo:
            flash("O título da tarefa é obrigatório!", "danger")
            return redirect(url_for("tarefas_bp.nova_tarefa"))

        nova_tarefa = Tarefa(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            usuario_id=session["user_id"],
            status="A Fazer"
        )

        db.session.add(nova_tarefa)
        db.session.commit()
        flash(f"Tarefa '{titulo}' criada com sucesso!", "success")
        return redirect(url_for("tarefas_bp.dashboard"))

    return render_template("nova_tarefa.html", prioridades=PRIORIDADES)

# Rota para Mudar o Status (Mover no Kanban)
@tarefas_bp.route("/tarefa/mudar_status/<int:tarefa_id>/<string:novo_status>")
@login_required
def mudar_status(tarefa_id, novo_status):
    if novo_status not in STATUS_VALIDOS:
        flash("Status inválido.", "danger")
        return redirect(url_for("tarefas_bp.dashboard"))

    tarefa = Tarefa.query.get_or_404(tarefa_id)

    if tarefa.usuario_id != session["user_id"]:
        flash("Você não tem permissão para alterar esta tarefa.", "danger")
        return redirect(url_for("tarefas_bp.dashboard"))

    tarefa.status = novo_status
    db.session.commit()
    flash(f"Status da tarefa '{tarefa.titulo}' alterado para {novo_status}!", "success")
    return redirect(url_for("tarefas_bp.dashboard"))

# Rota de Registro de Usuário
@tarefas_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Nome de usuário já existe.", "danger")
            return redirect(url_for("tarefas_bp.register"))
        
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registro bem-sucedido! Faça login.", "success")
        return redirect(url_for("tarefas_bp.login"))

    return render_template("register.html")