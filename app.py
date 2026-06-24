# app.py
from flask import Flask, render_template, redirect, url_for, session
import threading


from routes.estoque_routes import estoque_bp
from routes.auth_routes import auth_bp
from services.rfid_service import iniciar_escuta_serial

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_laboratorio' 

app.register_blueprint(estoque_bp)
app.register_blueprint(auth_bp)

# --- ROTAS FRONT-END ---

@app.route('/')
def index():
    # Se o usuário não estiver na sessão, vai pra tela de login
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # Se ele for admin ou usuário logado, entra no sistema
    return render_template('index.html', nome=session.get('nome'), cargo=session.get('cargo'))

@app.route('/login')
def login_page():
    # Se ele já estiver logado e tentar acessar /login, manda pro sistema
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

if __name__ == '__main__':
    print("Iniciando serviços...")
    threading.Thread(target=iniciar_escuta_serial, daemon=True).start()
    app.run(debug=True, use_reloader=False)


