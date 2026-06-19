# routes/estoque_routes.py
from flask import Blueprint, jsonify, request, session
import sqlite3
from services.rfid_service import estado_leitor
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Cria o Blueprint 'estoque'
estoque_bp = Blueprint('estoque', __name__)
DB_NAME = 'inventario_v2.db'

@estoque_bp.route('/api/scan')
def api_scan():
    # Retorna o estado atual do leitor para o painel reagir na hora
    return jsonify(estado_leitor)

@estoque_bp.route('/api/produtos')
def listar_produtos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor() 
    cursor.execute("SELECT tag_id, nome, status, localizacao, detalhes, foto FROM equipamentos")
    linhas = cursor.fetchall()
    conn.close()
    
    lista = [{"tag_id": l[0], "nome": l[1], "status": l[2], "localizacao": l[3], "detalhes": l[4], "foto": l[5]} for l in linhas]
    return jsonify(lista)

@estoque_bp.route('/api/movimentacoes')
def listar_movimentacoes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            m.equipamento_tag, 
            IFNULL(e.nome, 'Item Excluído'), 
            IFNULL(u.nome, 'Usuário Excluído'), 
            m.data_retirada, 
            m.data_devolucao
        FROM movimentacoes m
        LEFT JOIN equipamentos e ON m.equipamento_tag = e.tag_id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.id DESC LIMIT 50
    ''')  
    linhas = cursor.fetchall()
    conn.close()
    
    lista = []
    for l in linhas:
        lista.append({
            "tag_id": l[0], 
            "equipamento": l[1], 
            "usuario": l[2],
            "data_retirada": l[3], 
            "data_devolucao": l[4] or "Em uso"
        })
    return jsonify(lista)

@estoque_bp.route('/api/movimentar', methods=['POST'])
def movimentar_item():
    if 'user_id' not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    dados = request.json
    tag_id = dados.get('tag_id')
    user_id = session['user_id']
    agora = datetime.now().strftime('%d/%m/%Y %H:%M') # FFormatar Data

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Status atual do item (Retirada ou Devolução)
    cursor.execute("SELECT status FROM equipamentos WHERE tag_id = ?", (tag_id,))
    res = cursor.fetchone()

    if not res:
        return jsonify({"erro": "Equipamento não encontrado"}), 404

    status_atual = res[0]

    if status_atual == 'Ativo':
        # RETIRADA: Muda para Inativo e cria um registro novo sem data de devolução
        cursor.execute("UPDATE equipamentos SET status = 'Inativo' WHERE tag_id = ?", (tag_id,))
        cursor.execute('''
            INSERT INTO movimentacoes (equipamento_tag, usuario_id, data_retirada)
            VALUES (?, ?, ?)
        ''', (tag_id, user_id, agora))
        acao = "Retirada"

    else:
        # DEVOLUÇÃO: Muda para Ativo e atualiza o último registro em aberto desse item
        cursor.execute("UPDATE equipamentos SET status = 'Ativo' WHERE tag_id = ?", (tag_id,))
        cursor.execute('''
            UPDATE movimentacoes 
            SET data_devolucao = ? 
            WHERE equipamento_tag = ? AND data_devolucao IS NULL
        ''', (agora, tag_id))
        acao = "Devolução"

    conn.commit() 
    conn.close()
    
    # Atualiza o estado da memória pro painel reagir na hora
    from services.rfid_service import estado_leitor
    estado_leitor["status"] = "Inativo" if status_atual == 'Ativo' else "Ativo"

    return jsonify({"sucesso": True, "acao": acao})

# --- CONFIGURAÇÕES DE UPLOAD ---
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROTA DE CADASTRO ---
@estoque_bp.route('/api/cadastrar', methods=['POST'])
def cadastrar_produto():
    #  Só admin cadastra
    if session.get('cargo') != 'admin':
        return jsonify({"erro": "Acesso negado. Apenas administradores podem cadastrar."}), 403

    # 2. Verifica se a Tag ID veio no formulário
    tag_id = request.form.get('tag_id')
    if not tag_id:
        return jsonify({"erro": "ID da Tag é obrigatório"}), 400

    # 3. Processa a Foto (Arquivo binário)
    caminho_foto_no_db = ""
    if 'foto' in request.files:
        arquivo = request.files['foto']
        if arquivo.filename != '' and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            caminho_fisico = os.path.join(UPLOAD_FOLDER, filename)
            
            # Garante que a pasta uploads existe
            os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
            
            arquivo.save(caminho_fisico)
            caminho_foto_no_db = '/' + UPLOAD_FOLDER.replace('\\', '/') + '/' + filename

    # 4. Salva no SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO equipamentos (tag_id, nome, status, localizacao, detalhes, foto)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tag_id, request.form.get('nome'), request.form.get('status'), 
          request.form.get('localizacao'), request.form.get('detalhes'), caminho_foto_no_db))
    conn.commit()
    conn.close()

    

    # 5. Reseta o display do leitor no serviço isolado // 
    from services.rfid_service import estado_leitor
    estado_leitor.update({
        "tag_id": None, "nome": "Item Salvo com Sucesso!", "status": "",
        "localizacao": "", "detalhes": "Aguardando próxima leitura...", 
        "foto": "", "conhecido": False
    })
    
    return jsonify({"sucesso": True})