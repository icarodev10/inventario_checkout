# database/db_setup.py
import sqlite3

DB_NAME = 'inventario_v2.db'

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Equipamentos do espaço
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            tag_id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            status TEXT NOT NULL,
            localizacao TEXT,
            detalhes TEXT,
            foto TEXT
        )
    ''')

    # Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            cargo TEXT NOT NULL
        )
    ''')

    # Movimentações (Histórico)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento_tag TEXT,
            usuario_id INTEGER,
            data_retirada DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_devolucao DATETIME,
            FOREIGN KEY (equipamento_tag) REFERENCES equipamentos (tag_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados modular criado com sucesso!")

if __name__ == '__main__':
    criar_tabelas()