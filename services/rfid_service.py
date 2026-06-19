# services/rfid_service.py
import serial
import time
import sqlite3

# Estado global do leitor, atualizado pela Thread que escuta o Arduino
estado_leitor = {
    "tag_id": None,
    "nome": "Aguardando leitura...",
    "status": "",
    "localizacao": "",
    "detalhes": "Passe a tag no leitor.",
    "foto": "",
    "conhecido": False
}

def buscar_produto(tag_id):
    # Conecta no banco de dados
    conn = sqlite3.connect('inventario_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome, status, localizacao, detalhes, foto FROM equipamentos WHERE tag_id = ?", (tag_id,))
    res = cursor.fetchone()
    conn.close()
    return res

def iniciar_escuta_serial(porta='COM3', baud_rate=9600):
    """
    Função que vai rodar em Thread, 100% isolada da web.
    """
    try:
        arduino = serial.Serial(porta, baud_rate, timeout=1)
        print(f"[Hardware] RFID conectado na porta {porta}")
    except Exception as e:
        print(f"[Hardware ERRO] Não achou o leitor: {e}")
        return

    while True:
        try:
            if arduino.in_waiting > 0:
                linha = arduino.readline().decode('utf-8').strip()
                
                if "ID da Tag Lido:" in linha:
                    tag_id = linha.replace("ID da Tag Lido: ", "").strip()
                    
                    estado_leitor["tag_id"] = tag_id
                    produto = buscar_produto(tag_id)
                    
                    if produto:
                        estado_leitor.update({
                            "nome": produto[0], "status": produto[1], 
                            "localizacao": produto[2], "detalhes": produto[3], 
                            "foto": produto[4], "conhecido": True
                        })
                    else:
                        estado_leitor.update({
                            "nome": "Nova Tag Detectada", "status": "Inativo", 
                            "localizacao": "Não definida", "detalhes": "Item não cadastrado.", 
                            "foto": "", "conhecido": False
                        })
        except Exception:
            time.sleep(1)