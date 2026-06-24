# criar_admin.py
import sqlite3

def criar_primeiro_usuario():
    conn = sqlite3.connect('inventario_v2.db')
    cursor = conn.cursor()
    
    # Inserindo um admin
    cursor.execute('''
        INSERT INTO usuarios (nome, senha, cargo) 
        VALUES (?, ?, ?)
    ''', ('Pessoa', '123', 'admin'))
    
    conn.commit()
    conn.close()
    print("Administrador Pessoa criado com sucesso!")
if __name__ == '__main__':
    criar_primeiro_usuario()

