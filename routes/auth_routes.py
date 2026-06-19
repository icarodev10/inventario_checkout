# routes/auth_routes.py
from flask import Blueprint, jsonify, request, session
import sqlite3

auth_bp = Blueprint('auth', __name__)
DB_NAME = 'inventario_v2.db'

@auth_bp.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    usuario_input = dados.get('usuario')
    senha = dados.get('senha')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, cargo FROM usuarios WHERE nome = ? AND senha = ?", 
                   (usuario_input, senha))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Abre o sistema e salva os dados do usuário na sessão
        session['user_id'] = user[0]
        session['nome'] = user[1]
        session['cargo'] = user[2]
        return jsonify({"sucesso": True, "nome": user[1], "cargo": user[2]})
    else:
        return jsonify({"sucesso": False, "erro": "Usuário ou senha incorretos."}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"sucesso": True})

@auth_bp.route('/api/me', methods=['GET'])
def verificar_sessao():
    if 'user_id' in session:
        return jsonify({"logado": True, "nome": session['nome'], "cargo": session['cargo']})
    return jsonify({"logado": False}), 401

@auth_bp.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    if session.get('cargo') != 'admin':
        return jsonify({"erro": "Acesso negado"}), 403

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cargo FROM usuarios ORDER BY id DESC")
    usuarios = [{"id": linha[0], "nome": linha[1], "cargo": linha[2]} for linha in cursor.fetchall()]
    conn.close()
    return jsonify(usuarios)

@auth_bp.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    if session.get('cargo') != 'admin':
        return jsonify({"erro": "Acesso negado"}), 403

    dados = request.json
    nome = dados.get('nome')
    senha = dados.get('senha')
    cargo = dados.get('cargo') # 'admin' ou 'usuario'

    if not nome or not senha or not cargo:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nome, senha, cargo) VALUES (?, ?, ?)", (nome, senha, cargo))
        conn.commit()
        sucesso = True
        erro = ""
    except sqlite3.IntegrityError:
        sucesso = False
        erro = "Já existe um usuário com esse nome."
    finally:
        conn.close()

    if sucesso:
        return jsonify({"sucesso": True})
    return jsonify({"erro": erro}), 400

@auth_bp.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def deletar_usuario(id_usuario):
    if session.get('cargo') != 'admin':
        return jsonify({"erro": "Acesso negado"}), 403

    # Não deletar você mesmo
    if id_usuario == session.get('user_id'):
        return jsonify({"erro": "Você não pode deletar a si mesmo!"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": True})

